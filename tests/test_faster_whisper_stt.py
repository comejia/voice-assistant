from unittest.mock import MagicMock, patch

from voice_assistant.speech_to_text import FasterWhisperSTT, SpeechToTextConfig


def make_stt(segment_texts: list[str]) -> FasterWhisperSTT:
    """Crea un FasterWhisperSTT con WhisperModel mockeado.

    ``transcribe`` del modelo devuelve un segmento por cada texto de ``segment_texts``.
    """
    segments = [MagicMock(text=text) for text in segment_texts]
    with patch("voice_assistant.speech_to_text.faster_whisper_stt.WhisperModel") as model_cls:
        model = MagicMock()
        model.transcribe.return_value = (segments, None)
        model_cls.return_value = model
        return FasterWhisperSTT(SpeechToTextConfig())


def test_transcribe_une_los_segmentos_y_recorta_espacios():
    stt = make_stt([" prende ", " la luz "])

    assert stt.transcribe(b"\x00\x00") == "prende la luz"


def test_transcribe_devuelve_cadena_vacia_sin_habla():
    stt = make_stt([])

    assert stt.transcribe(b"\x00\x00") == ""
