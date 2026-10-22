import json
import logging
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from heed.audio import log_mel, prepare_clip

from .wake_word import WakeWord
from .wake_word_config import WakeWordConfig

logger = logging.getLogger(__name__)

# El micrófono entrega PCM int16; se normaliza a float32 en [-1, 1].
_INT16_MAX = 32768.0


class HeedWakeWord(WakeWord):
    """Detector de wake word con un modelo entrenado con ``heed-wakeword``.

    Infiere con ``onnxruntime`` sobre el modelo exportado y aplica la lógica de
    trigger (threshold, frames consecutivos, periodo refractario). El
    preprocesado del audio (HPF → log-mel → CMN) se delega a ``heed.audio`` para
    que coincida con el usado durante el entrenamiento.
    """

    # Defaults de la lógica de trigger, usados si la metadata no los especifica.
    DEFAULT_CONSECUTIVE_FRAMES = 2
    DEFAULT_REFRACTORY_SECONDS = 0.7

    def __init__(self, wake_word_config: WakeWordConfig):
        """Inicializa el detector.

        Args:
            wake_word_config: Configuración del detector.

        Raises:
            ValueError: Si falta ``metadata_path`` o si ``wake_word`` no coincide
                con la frase declarada en la metadata.
        """
        self.config = wake_word_config
        if wake_word_config.metadata_path is None:
            raise ValueError("HeedWakeWord requiere metadata_path (ruta al wake.json)")

        meta = json.loads(Path(wake_word_config.metadata_path).read_text())
        self.phrase = meta.get("phrase", "")

        if wake_word_config.wake_word and wake_word_config.wake_word != self.phrase:
            raise ValueError(
                f"La wake word esperada ({wake_word_config.wake_word!r}) no coincide "
                f"con la del modelo ({self.phrase!r})"
            )

        self.threshold = float(
            wake_word_config.threshold
            if wake_word_config.threshold is not None
            else meta["threshold"]
        )
        # Samples que el modelo consume por inferencia (una ventana de audio).
        self.window_samples = int(meta.get("audio_window_samples", meta["sample_rate"]))

        trigger = meta.get("trigger", {})
        self.consecutive_frames = int(
            trigger.get("consecutive_frames", self.DEFAULT_CONSECUTIVE_FRAMES)
        )
        self.refractory_seconds = float(
            trigger.get("refractory_seconds", self.DEFAULT_REFRACTORY_SECONDS)
        )

        self.session = ort.InferenceSession(
            str(wake_word_config.model), providers=["CPUExecutionProvider"]
        )
        self._input_name = self.session.get_inputs()[0].name

        self.reset()

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

    def reset(self) -> None:
        # Ventana deslizante con el último segundo de audio crudo (float32).
        self._buffer = np.zeros(self.window_samples, dtype=np.float32)
        # Frames consecutivos cuya probabilidad superó el threshold.
        self._frames_above_threshold = 0
        # Arranca muy atrás para no bloquear la primera detección.
        self._last_trigger = float("-inf")
