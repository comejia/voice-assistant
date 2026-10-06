import logging
import os

import openwakeword
import pyaudio
from dotenv import load_dotenv

from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.voice.pyaudio_microphone import PyAudioMicrophone
from voice_assistant.wake_word.open_wake_word import OpenWakeWord
from voice_assistant.wake_word.wake_word_config import WakeWordConfig

logger = logging.getLogger(__name__)


def run() -> None:
    openwakeword.utils.download_models()

    audio_config = AudioConfig(
        sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280
    )
    wake_word_config = WakeWordConfig(
        model="alexa", wake_word="alexa", inference_framework="tflite"
    )

    microphone = PyAudioMicrophone(config=audio_config)
    wake_word = OpenWakeWord(wake_word_config=wake_word_config)

    try:
        microphone.start()

        logger.info("Esperando wake word...")

        while True:
            audio = microphone.read()
            logger.debug("Chunk recibido: %d bytes", len(audio))

            if wake_word.detect(audio):
                logger.info("Wake word detectada!")
                logger.info("Saliendo del programa...")
                break

    except KeyboardInterrupt:
        pass

    finally:
        microphone.close()
        logger.info("Micrófono cerrado")


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        level=logging.WARNING,  # Las librerías de terceros quedan en WARNING.
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logging.getLogger("voice_assistant").setLevel(log_level)
    run()


if __name__ == "__main__":
    main()
