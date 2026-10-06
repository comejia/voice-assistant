import pyaudio
import pytest

from voice_assistant.voice import AudioConfig
from voice_assistant.wake_word import WakeWordConfig


@pytest.fixture
def audio_config():
    return AudioConfig(sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1280)


@pytest.fixture
def word_config():
    return WakeWordConfig(model="alexa", wake_word="alexa", inference_framework="tflite")
