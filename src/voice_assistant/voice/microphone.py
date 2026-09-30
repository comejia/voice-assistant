from abc import ABC, abstractmethod


class Microphone(ABC):
    @abstractmethod
    def start(self): ...

    @abstractmethod
    def read(self) -> bytes: ...

    @abstractmethod
    def stop(self): ...

    @abstractmethod
    def close(self): ...
