import pyaudio
import pytest

from voice_assistant.voice.audio_config import AudioConfig


@pytest.fixture
def audio_config():
    return AudioConfig(sample_rate=16_000, channels=1, format=pyaudio.paInt16, chunk_size=1_024)
