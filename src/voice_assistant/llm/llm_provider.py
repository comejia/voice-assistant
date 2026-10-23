from abc import ABC, abstractmethod
from collections.abc import Sequence

from .llm_response import LLMResponse
from .message import Message


class LLMProvider(ABC):
    """Acceso a un modelo de lenguaje, independiente del SDK.

    Abstrae el proveedor concreto (OpenAI, Ollama, Groq, ...) detrás de una interfaz
    común. No guarda estado de la conversación: recibe el historial completo en cada
    llamada; mantenerlo es responsabilidad del agente.
    """

    @abstractmethod
    def chat(self, messages: Sequence[Message]) -> LLMResponse:
        """Envía la conversación (en orden cronológico) y devuelve la respuesta."""
        ...
