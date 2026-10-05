import wave

import numpy as np

from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.wake_word.open_wake_word import OpenWakeWord
from voice_assistant.wake_word.wake_word_config import WakeWordConfig


def test_detects_wake_word(audio_config: AudioConfig, word_config: WakeWordConfig):

    wake_word = OpenWakeWord(word_config)

    with wave.open("mic_test.wav", "rb") as wav:
        while True:
            data = wav.readframes(audio_config.chunk_size)

            if not data:
                break

            audio = np.frombuffer(data, dtype=np.int16)

            if wake_word.detect(audio.tobytes()):
                return

    assert False, "No se detectó el wake word 'Alexa'"
