import openwakeword
import pyaudio

from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.voice.pyaudio_microphone import PyAudioMicrophone
from voice_assistant.wake_word.open_wake_word import OpenWakeWord
from voice_assistant.wake_word.wake_word_config import WakeWordConfig


def run():

    openwakeword.utils.download_models()

    audio_config = AudioConfig(
        sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280
    )
    wake_word_config = WakeWordConfig(
        model_path="alexa", wake_word="alexa", inference_framework="tflite"
    )

    microphone = PyAudioMicrophone(config=audio_config)
    wake_word = OpenWakeWord(wake_word_config=wake_word_config)

    try:
        microphone.start()

        print("Esperando wake word...")

        while True:
            audio = microphone.read()
            print(f"Chunk recibido: {len(audio)} bytes")

            if wake_word.detect(audio):
                print("Wake word detectada!")
                print("Saliendo del programa...")
                break

    except KeyboardInterrupt:
        pass

    finally:
        microphone.close()
        print("Micrófono cerrado")


if __name__ == "__main__":
    run()
