import numpy as np
from openwakeword.model import Model

from .wake_word import WakeWord
from .wake_word_config import WakeWordConfig


class OpenWakeWord(WakeWord):
    def __init__(self, wake_word_config: WakeWordConfig):
        self.config = wake_word_config
        self.model = Model(wakeword_models=[self.config.model_path])

    def detect(self, audio: bytes) -> bool:
        frame = np.frombuffer(audio, dtype=np.int16)

        predictions = self.model.predict(frame)

        return predictions[self.config.wake_word] > self.config.threshold
