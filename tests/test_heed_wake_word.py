from unittest.mock import patch

import pytest

from voice_assistant.wake_word import HeedWakeWord, WakeWordConfig

# Metadata controlada (lo que normalmente vive en wake.json), para no depender
# del modelo real al testear la lógica de trigger.
WORD_META = {
    "phrase": "hola deby",
    "threshold": 0.5,
    "sample_rate": 16_000,
    "audio_window_samples": 16_000,
    "trigger": {"consecutive_frames": 2, "refractory_seconds": 0.7},
}

# Un chunk de audio cualquiera; su contenido es irrelevante porque _infer se mockea.
CHUNK = b"\x00\x00" * 1280


def make_detector(score: float, **config_kwargs) -> HeedWakeWord:
    """Crea un HeedWakeWord con WORD_META y _infer mockeado para que devuelva
    siempre ``score``, sin cargar el wake.json ni el modelo ONNX reales."""
    config = WakeWordConfig(
        model="wake.onnx",
        metadata_path="wake.json",
        **config_kwargs,
    )
    with (
        patch("voice_assistant.wake_word.heed_wake_word.json.loads", return_value=WORD_META),
        patch("voice_assistant.wake_word.heed_wake_word.Path.read_text", return_value="{}"),
        patch("voice_assistant.wake_word.heed_wake_word.ort.InferenceSession"),
    ):
        detector = HeedWakeWord(config)
    detector._infer = lambda window: score
    return detector


def test_detect_true_cuando_supera_el_umbral():
    detector = make_detector(score=0.9)

    # Requiere consecutive_frames (2) para disparar.
    assert detector.detect(CHUNK) is False
    assert detector.detect(CHUNK) is True


def test_detect_false_cuando_no_supera_el_umbral():
    detector = make_detector(score=0.1)

    assert detector.detect(CHUNK) is False
    assert detector.detect(CHUNK) is False


def test_detect_false_cuando_es_igual_al_umbral():
    # La comparación es estricta (> threshold), por lo que un score igual
    # al umbral no debe considerarse detección.
    detector = make_detector(score=WORD_META["threshold"])

    assert detector.detect(CHUNK) is False
    assert detector.detect(CHUNK) is False


def test_refractory_suprime_disparos_seguidos():
    detector = make_detector(score=0.9)

    # Primer disparo tras los frames consecutivos.
    detector.detect(CHUNK)
    assert detector.detect(CHUNK) is True

    # Dentro del periodo refractario no vuelve a disparar.
    assert detector.detect(CHUNK) is False
    assert detector.detect(CHUNK) is False


def test_reset_limpia_el_estado_acumulado():
    # Tras resetear, los frames consecutivos previos no deben contar: vuelve a
    # hacer falta la secuencia completa para disparar.
    detector = make_detector(score=0.9)

    detector.detect(CHUNK)  # 1er frame sobre el umbral (aún no dispara)
    detector.reset()

    # Si el estado se limpió, este frame es "el primero" otra vez y no dispara.
    assert detector.detect(CHUNK) is False
    assert detector.detect(CHUNK) is True


def test_threshold_de_la_config_sobrescribe_al_metadata():
    # WORD_META trae 0.5; la config fuerza 0.8.
    detector = make_detector(score=0.0, threshold=0.8)

    assert detector.threshold == 0.8


def test_wake_word_que_no_coincide_falla():
    # Si se declara una frase distinta a la del modelo, debe fallar al construir.
    with pytest.raises(ValueError, match="no coincide"):
        make_detector(score=0.0, wake_word="otra frase")


def test_falta_metadata_path_falla():
    config = WakeWordConfig(model="wake.onnx")  # sin metadata_path
    with (
        patch("voice_assistant.wake_word.heed_wake_word.ort.InferenceSession"),
        pytest.raises(ValueError, match="metadata_path"),
    ):
        HeedWakeWord(config)
