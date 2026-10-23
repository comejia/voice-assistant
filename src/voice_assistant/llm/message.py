from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    """Rol de un mensaje en la conversación.

    Los valores coinciden con los del protocolo de chat de OpenAI, de modo que una
    implementación compatible los mapee sin traducción.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class Message:
    """Un mensaje de la conversación, independiente del proveedor.

    El agente los agrupa en una lista y cada ``LLMProvider`` la traduce al formato
    de su SDK.
    """

    role: Role
    content: str = ""
