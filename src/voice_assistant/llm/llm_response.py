from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Respuesta de un ``LLMProvider`` a una petición de chat.

    Independiente del proveedor. Hoy solo transporta el texto generado; se ampliará
    con los pedidos de herramienta (``tool_calls``) cuando se sumen.
    """

    content: str = ""
