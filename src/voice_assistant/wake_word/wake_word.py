from abc import ABC, abstractmethod


class WakeWord(ABC):
    @abstractmethod
    def detect(self, audio: bytes) -> bool: ...
