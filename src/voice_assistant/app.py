import logging
import os

import pyaudio
from dotenv import load_dotenv

from voice_assistant.agent import Agent, AgentConfig, SimpleAgent
from voice_assistant.llm import LLMConfig, LLMProvider, OpenAIProvider
from voice_assistant.speech_to_text import (
    FasterWhisperSTT,
    SpeechToText,
    SpeechToTextConfig,
)
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

    Soporta "openwakeword" (default) y "heed". La configuración de cada motor
    se toma de las variables de entorno WAKE_WORD_*.
    """
    engine = os.getenv("WAKE_WORD_ENGINE", "openwakeword").lower()

    if engine == "heed":
        threshold = os.getenv("WAKE_WORD_THRESHOLD")
        config = WakeWordConfig(
            model=os.getenv("WAKE_WORD_MODEL", "models/wake.onnx"),
            metadata_path=os.getenv("WAKE_WORD_METADATA", "models/wake.json"),
            # Opcionales: si no se indican, mandan los valores del wake.json.
            wake_word=os.getenv("WAKE_WORD_NAME", ""),
            threshold=float(threshold) if threshold else None,
        )
        logger.debug("Motor de wake word: heed (%s)", config.model)
        return HeedWakeWord(wake_word_config=config)

    # Motor por defecto: openwakeword.
    from openwakeword import utils

    utils.download_models()
    threshold = os.getenv("WAKE_WORD_THRESHOLD")
    wake_word_config = WakeWordConfig(
        model=os.getenv("WAKE_WORD_MODEL", "alexa"),
        wake_word=os.getenv("WAKE_WORD_NAME", "alexa"),
        inference_framework=os.getenv("WAKE_WORD_INFERENCE_FRAMEWORK", "tflite"),
        threshold=float(threshold) if threshold else None,
    )
    logger.debug("Motor de wake word: openwakeword (%s)", wake_word_config.model)
    return OpenWakeWord(wake_word_config=wake_word_config)


def _build_speech_to_text() -> SpeechToText:
    """Instancia el motor de speech-to-text.

    La configuración se toma de las variables de entorno STT_*. Actualmente solo
    hay un motor disponible (faster-whisper).
    """
    language = os.getenv("STT_LANGUAGE") or None
    config = SpeechToTextConfig(
        model=os.getenv("STT_MODEL", "tiny"),
        device=os.getenv("STT_DEVICE", "cpu"),
        compute_type=os.getenv("STT_COMPUTE_TYPE", "int8"),
        download_root=os.getenv("STT_DOWNLOAD_ROOT", "models/whisper"),
        language=language,
    )
    logger.debug("Motor de speech-to-text: faster-whisper (%s)", config.model)
    return FasterWhisperSTT(config=config)


def _build_llm() -> LLMProvider:
    """Instancia el proveedor de modelo de lenguaje.

    La configuración se toma de las variables de entorno LLM_*. Se usa un cliente compatible
    con la API de OpenAI, que sirve tanto para OpenAI como para servidores locales (Ollama) u
    otros proveedores: solo cambia LLM_BASE_URL.
    """
    base_url = os.getenv("LLM_BASE_URL") or None
    config = LLMConfig(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("LLM_API_KEY", ""),
        base_url=base_url,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )
    logger.debug(
        "Proveedor LLM: openai-compatible (%s @ %s)",
        config.model,
        config.base_url or "<default OpenAI>",
    )
    return OpenAIProvider(config=config)


def _build_agent(llm: LLMProvider) -> Agent:
    """Instancia el agente conversacional sobre un proveedor LLM.

    La configuración se toma de las variables de entorno AGENT_*.
    """
    system_prompt = os.getenv("AGENT_SYSTEM_PROMPT")
    keep_history = os.getenv("AGENT_KEEP_HISTORY", "true").lower() == "true"
    # Si no se define AGENT_SYSTEM_PROMPT, se usa el default de AgentConfig.
    config = (
        AgentConfig(keep_history=keep_history)
        if system_prompt is None
        else AgentConfig(system_prompt=system_prompt, keep_history=keep_history)
    )
    logger.debug("Agente: keep_history=%s", config.keep_history)
    return SimpleAgent(llm=llm, config=config)


def run() -> None:
    audio_config = AudioConfig(
        sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280
    )

    microphone = PyAudioMicrophone(config=audio_config)
    wake_word = _build_wake_word()
    speech_to_text = _build_speech_to_text()
    llm = _build_llm()
    agent = _build_agent(llm)

    # Tras la wake word se graba una ventana fija de audio con el comando. Como
    # el micrófono entrega chunks de tamaño fijo, se traduce a cuántos leer.
    command_seconds = float(os.getenv("STT_COMMAND_SECONDS", "5"))
    chunks_to_capture = int(command_seconds * audio_config.sample_rate / audio_config.chunk_size)

    try:
        microphone.start()

        logger.info("Esperando wake word...")

        while True:
            audio = microphone.read()
            logger.debug("Chunk recibido: %d bytes", len(audio))

            if wake_word.detect(audio):
                logger.info("Wake word detectada!")

                logger.info("Grabando comando (%.1f s)...", command_seconds)
                frames = [microphone.read() for _ in range(chunks_to_capture)]
                command_audio = b"".join(frames)

                logger.info("Transcribiendo...")
                text = speech_to_text.transcribe(command_audio)
                logger.info("Comando: %s", text)

                if text:
                    logger.info("Consultando al agente...")
                    response = agent.run(text)
                    logger.info("Respuesta: %s", response)
                else:
                    logger.info("No se detectó comando, se ignora.")

                wake_word.reset()
                logger.info("Esperando wake word...")

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
