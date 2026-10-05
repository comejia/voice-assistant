import wave

import pyaudio

from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.voice.pyaudio_microphone import PyAudioMicrophone

audio_config = AudioConfig(sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280)

microphone = PyAudioMicrophone(config=audio_config)
microphone.start()

frames = []

for _ in range(100):
    audio = microphone.read()
    frames.append(audio)

with wave.open("mic_test.wav", "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b"".join(frames))
