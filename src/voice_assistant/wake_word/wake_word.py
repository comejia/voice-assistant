from abc import ABC, abstractmethod


class WakeWord(ABC):
    @abstractmethod
    def detect(self, audio: bytes) -> bool: ...

    @abstractmethod
    def reset(self) -> None:
        """Descarta el estado de audio acumulado.

        Debe llamarse tras una pausa en el flujo de audio (p. ej. mientras se
        graba el comando del usuario) para que el audio previo a la pausa no
        dispare una detección espuria al reanudar.
        """
        ...
