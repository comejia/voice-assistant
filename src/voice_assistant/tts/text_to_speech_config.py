from dataclasses import dataclass


@dataclass(frozen=True)
class TextToSpeechConfig:
    """Configuración de un motor de text-to-speech.

    Attributes:
        model: Ruta al modelo de voz ``.onnx`` de Piper. El ``.onnx.json`` con los
            metadatos de la voz debe estar junto al archivo.
        length_scale: Factor de velocidad del habla; ``1.0`` es la velocidad nominal de
            la voz, valores mayores la ralentizan y menores la aceleran.
    """

    model: str = "models/piper/es_AR-daniela-high.onnx"
    length_scale: float = 1.0
