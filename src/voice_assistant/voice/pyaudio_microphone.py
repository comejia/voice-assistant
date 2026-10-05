import logging

import pyaudio

from .audio_config import AudioConfig
from .microphone import Microphone

logger = logging.getLogger(__name__)


class PyAudioMicrophone(Microphone):
    def __init__(self, config: AudioConfig):
        self.config = config
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        self.stream = self.audio.open(
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=self.config.chunk_size,
        )
        logger.debug("Stream de audio iniciado")

    def read(self) -> bytes:
        return self.stream.read(
            self.config.chunk_size,
            exception_on_overflow=False,
        )

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def close(self):
        self.stop()
        self.audio.terminate()
