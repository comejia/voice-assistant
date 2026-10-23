from abc import ABC, abstractmethod


class TextToSpeech(ABC):
    """Síntesis y reproducción de voz, independiente de la librería.

    Define la interfaz que deben implementar los motores de text-to-speech, de forma
    que el resto de la aplicación no dependa de un motor concreto (Piper, Coqui, ...).
    """

    @abstractmethod
    def say(self, text: str) -> None:
        """Sintetiza ``text`` y reproduce el audio resultante.

        Args:
            text: Texto a verbalizar. Una cadena vacía no produce audio.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Libera los recursos del dispositivo de audio.

        Debe llamarse al finalizar el uso del motor. Tras invocarlo, la instancia no
        vuelve a utilizarse.
        """
        ...
