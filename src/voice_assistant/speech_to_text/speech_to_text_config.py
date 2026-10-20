from dataclasses import dataclass


@dataclass(frozen=True)
class SpeechToTextConfig:
    """Configuración de un motor de speech-to-text.

    Attributes:
        model: Nombre del modelo (``tiny``, ``base``, ``small``, ...) o ruta a un modelo local.
        device: Dispositivo de inferencia (``cpu``, ``cuda`` o ``auto``).
        compute_type: Precisión numérica de la inferencia. Para CPU se recomienda ``int8``.
        download_root: Directorio donde se descarga y cachea el modelo.
        language: Código ISO del idioma (``es``, ``en``, ...). ``None`` lo detecta automáticamente.
    """

    model: str = "tiny"
    device: str = "cpu"
    compute_type: str = "int8"
    download_root: str = "models/whisper"
    language: str | None = None
