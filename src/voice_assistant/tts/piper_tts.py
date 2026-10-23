import logging

import pyaudio
from piper import PiperVoice, SynthesisConfig

from .text_to_speech import TextToSpeech
from .text_to_speech_config import TextToSpeechConfig

logger = logging.getLogger(__name__)


class PiperTTS(TextToSpeech):
    """Text-to-speech con Piper (modelos neuronales ONNX, 100% local en CPU).

    La voz se carga una sola vez al construir la instancia. Cada ``say`` sintetiza en
    streaming y reproduce los fragmentos a medida que se generan, lo que reduce la
    latencia hasta el primer sonido. Piper entrega PCM de 16 bits mono; el sample rate
    lo determina la voz.
    """

    def __init__(self, config: TextToSpeechConfig):
        """Carga la voz e inicializa el backend de audio.

        Args:
            config: Configuración del motor de text-to-speech.
        """
        self.config = config
        self._voice = PiperVoice.load(config.model)
        self._synthesis = SynthesisConfig(length_scale=config.length_scale)
        self._audio = pyaudio.PyAudio()
        logger.debug(
            "PiperTTS cargado: model=%s length_scale=%s",
            config.model,
            config.length_scale,
        )

    def say(self, text: str) -> None:
        """Sintetiza ``text`` y reproduce el audio resultante.

        Args:
            text: Texto a verbalizar. Una cadena vacía no produce audio.
        """
        if not text:
            return

        # El stream se abre con el primer fragmento porque su sample rate lo define la
        # voz y no se conoce hasta entonces.
        stream = None
        for chunk in self._voice.synthesize(text, syn_config=self._synthesis):
            if stream is None:
                stream = self._audio.open(
                    format=self._audio.get_format_from_width(chunk.sample_width),
                    channels=chunk.sample_channels,
                    rate=chunk.sample_rate,
                    output=True,
                )
            stream.write(chunk.audio_int16_bytes)

        if stream is not None:
            stream.stop_stream()
            stream.close()

    def close(self) -> None:
        """Libera los recursos del dispositivo de audio."""
        self._audio.terminate()
