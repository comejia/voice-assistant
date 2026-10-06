import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voice_assistant.voice import AudioConfig
from voice_assistant.wake_word import OpenWakeWord, WakeWordConfig

MIC_TEST_WAV = Path(__file__).resolve().parent.parent / "mic_test.wav"


def make_detector(config: WakeWordConfig, score: float) -> OpenWakeWord:
    """Crea un OpenWakeWord con un Model mockeado que siempre devuelve ``score``."""
    with patch("voice_assistant.wake_word.open_wake_word.Model") as mock_model_cls:
        mock_model = MagicMock()
        mock_model.predict.return_value = {config.wake_word: score}
        mock_model_cls.return_value = mock_model
        return OpenWakeWord(config)


def test_detect_true_cuando_supera_el_umbral(word_config: WakeWordConfig):
    detector = make_detector(word_config, score=0.9)

    assert detector.detect(b"\x00\x00") is True


def test_detect_false_cuando_no_supera_el_umbral(word_config: WakeWordConfig):
    detector = make_detector(word_config, score=0.1)

    assert detector.detect(b"\x00\x00") is False


def test_detect_false_cuando_es_igual_al_umbral(word_config: WakeWordConfig):
    # La comparación es estricta (> threshold), por lo que un score igual
    # al umbral no debe considerarse detección.
    detector = make_detector(word_config, score=0.5)

    assert detector.detect(b"\x00\x00") is False


@pytest.mark.integration
def test_detects_wake_word(audio_config: AudioConfig, word_config: WakeWordConfig):

    wake_word = OpenWakeWord(word_config)

    with wave.open(str(MIC_TEST_WAV), "rb") as wav:
        while True:
            data = wav.readframes(audio_config.chunk_size)

            if not data:
                break

            audio = np.frombuffer(data, dtype=np.int16)

            if wake_word.detect(audio.tobytes()):
                return

    assert False, "No se detectó el wake word 'Alexa'"
