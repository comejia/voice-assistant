from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    """Configuración de un proveedor de modelo de lenguaje.

    Pensada para APIs compatibles con OpenAI, donde cambiar de proveedor (OpenAI, Ollama
    local, Groq, ...) se reduce a ajustar ``base_url``, ``api_key`` y ``model``.

    Attributes:
        model: Identificador del modelo (``gpt-4o-mini``, ``llama3.2``, ...).
        api_key: Credencial del proveedor. Servidores locales sin auth (Ollama) aceptan
            cualquier valor no vacío.
        base_url: Endpoint de la API. ``None`` usa el default del SDK (OpenAI).
        temperature: Aleatoriedad del muestreo; más bajo = más determinista.
    """

    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str | None = None
    temperature: float = 0.7
