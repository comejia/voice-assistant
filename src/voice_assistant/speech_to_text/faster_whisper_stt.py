import logging

import numpy as np
from faster_whisper import WhisperModel

from .speech_to_text import SpeechToText
from .speech_to_text_config import SpeechToTextConfig

logger = logging.getLogger(__name__)

# Factor para normalizar PCM int16 a float32 en [-1, 1], el formato que espera faster-whisper.
_INT16_MAX = 32768.0


class FasterWhisperSTT(SpeechToText):
    """Speech-to-text con ``faster-whisper`` (Whisper sobre CTranslate2).

    El modelo se descarga automáticamente a ``download_root`` la primera vez y se cachea.
    La inferencia corre en CPU con cuantización ``int8`` por defecto.
    """

    def __init__(self, config: SpeechToTextConfig):
        """Inicializa el motor y carga el modelo.

        Args:
            config: Configuración del motor de speech-to-text.
        """
        self.config = config
        self.model = WhisperModel(
            config.model,
            device=config.device,
            compute_type=config.compute_type,
            download_root=config.download_root,
        )
        logger.debug(
            "FasterWhisperSTT cargado: model=%s device=%s compute_type=%s",
            config.model,
            config.device,
            config.compute_type,
        )

    def transcribe(self, audio: bytes) -> str:
        """Transcribe audio a texto.

        Args:
            audio: Audio PCM de 16 bits, mono, a 16 kHz.

        Returns:
            El texto reconocido, o una cadena vacía si no se detectó habla.
        """
        samples = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / _INT16_MAX

        # vad_filter: ignora los silencios, donde Whisper tiende a alucinar texto.
        # no_repeat_ngram_size: corta los bucles de repetición de palabras.
        segments, _ = self.model.transcribe(
            samples,
            language=self.config.language,
            vad_filter=True,
            no_repeat_ngram_size=2,
        )
        text = " ".join(segment.text.strip() for segment in segments)

        logger.debug("Transcripción: %r", text)
        return text.strip()
