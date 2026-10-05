import logging

import numpy as np
from openwakeword.model import Model

from .wake_word import WakeWord
from .wake_word_config import WakeWordConfig

logger = logging.getLogger(__name__)


class OpenWakeWord(WakeWord):
    WARMUP_FRAMES = 30

    def __init__(self, wake_word_config: WakeWordConfig):
        self.config = wake_word_config
        self.model = Model(wakeword_models=[self.config.model_path])
        logger.debug("Modelo de wake word cargado: %s", self.config.model_path)
        self._warmup()

    def _warmup(self, samples_per_frame: int = 1280) -> None:
        """Precarga el buffer interno del modelo con silencio.

        openwakeword necesita contexto de audio acumulado para predecir de
        forma fiable; sin esto, las primeras detecciones tras el arranque
        pueden fallar.
        """
        silence = np.zeros(samples_per_frame, dtype=np.int16).tobytes()
        for _ in range(self.WARMUP_FRAMES):
            self.detect(silence)
        logger.debug("Modelo calentado con %d frames de silencio", self.WARMUP_FRAMES)

    def detect(self, audio: bytes) -> bool:
        frame = np.frombuffer(audio, dtype=np.int16)

        predictions = self.model.predict(frame)

        score = predictions[self.config.wake_word]
        logger.debug("Score '%s': %.4f", self.config.wake_word, score)

        return score > self.config.threshold
