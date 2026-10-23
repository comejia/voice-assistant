from unittest.mock import MagicMock, patch

from voice_assistant.tts import PiperTTS, TextToSpeechConfig

_TTS = "voice_assistant.tts.piper_tts"


def make_tts(chunks: list) -> tuple[PiperTTS, MagicMock]:
    """Crea un PiperTTS con PiperVoice y PyAudio mockeados.

    ``synthesize`` devuelve ``chunks``. Devuelve también el stream de salida para
    inspeccionar qué se reprodujo.
    """
    with (
        patch(f"{_TTS}.PiperVoice") as voice_cls,
        patch(f"{_TTS}.pyaudio.PyAudio") as pyaudio_cls,
    ):
        voice_cls.load.return_value.synthesize.return_value = iter(chunks)
        stream = MagicMock()
        pyaudio_cls.return_value.open.return_value = stream
        return PiperTTS(TextToSpeechConfig()), stream


def _chunk(data: bytes) -> MagicMock:
    return MagicMock(audio_int16_bytes=data, sample_rate=22050, sample_width=2, sample_channels=1)


def test_say_reproduce_cada_chunk():
    tts, stream = make_tts([_chunk(b"\x01\x02"), _chunk(b"\x03\x04")])

    tts.say("hola")

    assert [c.args[0] for c in stream.write.call_args_list] == [b"\x01\x02", b"\x03\x04"]


def test_say_vacio_no_abre_stream():
    tts, stream = make_tts([])

    tts.say("")

    stream.write.assert_not_called()
