import logging
import os

import pyaudio
from dotenv import load_dotenv

from voice_assistant.voice import AudioConfig, PyAudioMicrophone
from voice_assistant.wake_word import (
    HeedWakeWord,
    OpenWakeWord,
    WakeWord,
    WakeWordConfig,
)

logger = logging.getLogger(__name__)


def _build_wake_word() -> WakeWord:
    """Instancia el detector de wake word según WAKE_WORD_ENGINE.

    - "openwakeword" (default): modelos preentrenados o .tflite de openwakeword.
    - "heed": modelo custom entrenado con heed-wakeword (wake.onnx + wake.json).
    """
    engine = os.getenv("WAKE_WORD_ENGINE", "openwakeword").lower()

    if engine == "heed":
        model_path = os.getenv("WAKE_WORD_MODEL", "models/wake.onnx")
        metadata_path = os.getenv("WAKE_WORD_METADATA", "models/wake.json")
        logger.debug("Motor de wake word: heed (%s)", model_path)
        return HeedWakeWord(model_path=model_path, metadata_path=metadata_path)

    # Motor por defecto: openwakeword.
    import openwakeword

    openwakeword.utils.download_models()
    # El modelo puede ser un nombre preentrenado de openwakeword (p. ej. "alexa",
    # "hey_jarvis") o la ruta a un .tflite custom.
    wake_word_config = WakeWordConfig(
        model=os.getenv("WAKE_WORD_MODEL", "alexa"),
        wake_word=os.getenv("WAKE_WORD_NAME", "alexa"),
        inference_framework=os.getenv("WAKE_WORD_INFERENCE_FRAMEWORK", "tflite"),
        threshold=float(os.getenv("WAKE_WORD_THRESHOLD", "0.5")),
    )
    logger.debug("Motor de wake word: openwakeword (%s)", wake_word_config.model)
    return OpenWakeWord(wake_word_config=wake_word_config)


def run() -> None:
    audio_config = AudioConfig(
        sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280
    )

    microphone = PyAudioMicrophone(config=audio_config)
    wake_word = _build_wake_word()

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
