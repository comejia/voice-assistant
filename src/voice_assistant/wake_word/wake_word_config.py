from dataclasses import dataclass


@dataclass(frozen=True)
class WakeWordConfig:
    """Configuración de un detector de wake word.

    Attributes:
        model: Nombre o ruta al modelo.
        wake_word: Palabra o frase de activación.
        inference_framework: Framework de inferencia del modelo.
        threshold: Umbral de confianza para activar. ``None`` usa el default.
        metadata_path: Ruta a la metadata que acompaña al modelo.
    """

    model: str
    wake_word: str = ""
    inference_framework: str = "tflite"
    threshold: float | None = None
    metadata_path: str | None = None
