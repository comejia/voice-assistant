from abc import ABC, abstractmethod


class SpeechToText(ABC):
    """Contrato para transcribir audio a texto.

    Define la interfaz que deben implementar los motores de speech-to-text,
    de forma que el resto de la aplicación no dependa de una librería concreta.
    """

    @abstractmethod
    def transcribe(self, audio: bytes) -> str:
        """Transcribe audio a texto.

        Args:
            audio: Audio PCM de 16 bits, mono, a 16 kHz.

        Returns:
            El texto reconocido, o una cadena vacía si no se detectó habla.
        """
        ...
