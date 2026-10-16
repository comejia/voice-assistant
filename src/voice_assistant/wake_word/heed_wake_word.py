import json
import logging
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from heed.audio import log_mel, prepare_clip

from .wake_word import WakeWord

logger = logging.getLogger(__name__)

# El micrófono entrega PCM int16; se normaliza a float32 en [-1, 1].
_INT16_MAX = 32768.0


class HeedWakeWord(WakeWord):
    """Detector de wake word con un modelo entrenado con ``heed-wakeword``.

    Requiere dos archivos del export de heed:

    - ``wake.onnx``: el modelo, sobre el que se infiere con ``onnxruntime``.
    - ``wake.json``: el contrato de runtime (threshold, tamaño de ventana y
      lógica de trigger).

    El preprocesado del audio (HPF → log-mel → CMN) se delega a ``heed.audio``
    para que coincida con el usado durante el entrenamiento.
    """

    def __init__(self, model_path: str | Path, metadata_path: str | Path):
        """Inicializa el detector.

        Args:
            model_path: Ruta al modelo ONNX exportado (``wake.onnx``).
            metadata_path: Ruta al contrato de runtime (``wake.json``), de donde
                se leen el threshold, el tamaño de ventana y la lógica de trigger.
        """
        meta = json.loads(Path(metadata_path).read_text())
        self.threshold = float(meta["threshold"])
        self.phrase = meta.get("phrase", "")
        # Cantidad de samples que el modelo espera por inferencia (ventana de 1 s
        # a 16 kHz). Definido por el modelo en su contrato (wake.json).
        self.window_samples = int(meta.get("audio_window_samples", meta["sample_rate"]))

        trigger = meta.get("trigger", {})
        self.consecutive_frames = int(trigger.get("consecutive_frames", 2))
        self.refractory_seconds = float(trigger.get("refractory_seconds", 0.7))

        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self._input_name = self.session.get_inputs()[0].name

        # Ventana deslizante de audio crudo (float32).
        self._buffer = np.zeros(self.window_samples, dtype=np.float32)
        # Frames consecutivos cuya probabilidad superó el threshold.
        self._frames_above_threshold = 0
        self._last_trigger = -1e9

        logger.debug("HeedWakeWord cargado: phrase=%r threshold=%.3f", self.phrase, self.threshold)

    def _infer(self, window: np.ndarray) -> float:
        """Infiere la probabilidad de wake word para una ventana de audio.

        Args:
            window: Ventana de audio crudo (float32), de ``window_samples`` samples.

        Returns:
            Probabilidad en el rango [0, 1].
        """
        clip = prepare_clip(torch.from_numpy(window))  # HPF, normalize, trim, center
        mel = log_mel(clip).numpy()  # log-mel + CMN, shape (1, 40, 101)
        logit = self.session.run(None, {self._input_name: mel})[0]
        logit = float(np.asarray(logit).flatten()[0])
        return 1.0 / (1.0 + np.exp(-logit))

    def detect(self, audio: bytes) -> bool:
        """Procesa un chunk de audio y determina si se activó la wake word.

        Args:
            audio: Chunk de audio PCM de 16 bits (como lo entrega el micrófono).

        Returns:
            ``True`` si la wake word se detectó en este chunk, ``False`` si no.
        """
        chunk = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / _INT16_MAX

        # Deslizar la ventana: descartar lo más viejo, anexar lo nuevo.
        n = len(chunk)
        if n >= self.window_samples:
            self._buffer = chunk[-self.window_samples :].copy()
        else:
            self._buffer = np.concatenate([self._buffer[n:], chunk])

        prob = self._infer(self._buffer)
        logger.debug("Score heed '%s': %.4f", self.phrase, prob)

        now = time.monotonic()
        if prob > self.threshold:
            self._frames_above_threshold += 1
        else:
            self._frames_above_threshold = 0

        if (
            self._frames_above_threshold >= self.consecutive_frames
            and now - self._last_trigger >= self.refractory_seconds
        ):
            self._last_trigger = now
            self._frames_above_threshold = 0
            return True

        return False
