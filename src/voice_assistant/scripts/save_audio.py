"""Script de utilidad para grabar audio del micrófono a un archivo WAV.

Útil para generar audios de prueba (p. ej. ``mic_test.wav`` para los tests
de integración del wake word).
"""

import wave
from pathlib import Path

import pyaudio

from voice_assistant.voice import AudioConfig, PyAudioMicrophone

# Guardar en la raíz del repo, donde el test de integración busca el audio,
# sin depender del directorio desde el que se ejecute el script.
OUTPUT_FILE = Path(__file__).resolve().parents[3] / "mic_test.wav"
FRAMES_TO_RECORD = 100  # ~8 s con chunk_size=1280 a 16 kHz


def main() -> None:
    audio_config = AudioConfig(
        sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280
    )

    microphone = PyAudioMicrophone(config=audio_config)
    frames = []

    try:
        microphone.start()
        print(f"Grabando {FRAMES_TO_RECORD} frames...")

        for _ in range(FRAMES_TO_RECORD):
            frames.append(microphone.read())
    finally:
        microphone.close()

    with wave.open(OUTPUT_FILE, "wb") as wav:
        wav.setnchannels(audio_config.channels)
        wav.setsampwidth(pyaudio.get_sample_size(audio_config.format))
        wav.setframerate(audio_config.sample_rate)
        wav.writeframes(b"".join(frames))

    print(f"Audio guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
