import pyaudio

from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.voice.pyaudio_microphone import PyAudioMicrophone


def run():
    config = AudioConfig(sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1_024)

    microphone = PyAudioMicrophone(config)

    try:
        microphone.start()

        print("Escuchando...")

        for _ in range(5):
            audio = microphone.read()

            print(f"Chunk recibido: {len(audio)} bytes")

    finally:
        microphone.close()
        print("Micrófono cerrado")


if __name__ == "__main__":
    run()
