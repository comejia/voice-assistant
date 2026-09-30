from voice_assistant.voice.audio_config import AudioConfig
from voice_assistant.voice.pyaudio_microphone import PyAudioMicrophone


def test_microphone_reads_audio(audio_config: AudioConfig):
    microphone = PyAudioMicrophone(audio_config)

    try:
        microphone.start()

        audio = microphone.read()

        assert audio, "El micrófono no devolvió audio"
        assert isinstance(audio, bytes), "El audio no es de tipo bytes"
        assert len(audio) == audio_config.chunk_size * 2, (
            "El tamaño del chunk de audio no es el esperado"
        )

    finally:
        microphone.close()
