from unittest.mock import patch

from voice_assistant.wake_word import HeedWakeWord

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


def make_detector(score: float) -> HeedWakeWord:
    """Crea un HeedWakeWord con WORD_META y _infer mockeado para que devuelva
    siempre ``score``, sin cargar el wake.json ni el modelo ONNX reales."""
    with (
        patch("voice_assistant.wake_word.heed_wake_word.json.loads", return_value=WORD_META),
        patch("voice_assistant.wake_word.heed_wake_word.Path.read_text", return_value="{}"),
        patch("voice_assistant.wake_word.heed_wake_word.ort.InferenceSession"),
    ):
        detector = HeedWakeWord("wake.onnx", "wake.json")
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
