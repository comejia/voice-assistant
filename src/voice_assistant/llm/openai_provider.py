import logging
from collections.abc import Sequence

from openai import OpenAI

from .llm_config import LLMConfig
from .llm_provider import LLMProvider
from .llm_response import LLMResponse
from .message import Message

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Proveedor para APIs compatibles con OpenAI.

    Como el protocolo de chat de OpenAI es un estándar de facto, el mismo cliente sirve
    para OpenAI, servidores locales (Ollama) y otros proveedores (Groq, DeepSeek, ...);
    solo cambian ``base_url``, ``api_key`` y ``model`` en la config.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        logger.debug(
            "OpenAIProvider inicializado: model=%s base_url=%s",
            config.model,
            config.base_url or "<default OpenAI>",
        )

    def chat(self, messages: Sequence[Message]) -> LLMResponse:
        payload = [{"role": message.role.value, "content": message.content} for message in messages]

        completion = self._client.chat.completions.create(
            model=self.config.model,
            messages=payload,  # type: ignore[arg-type]
            temperature=self.config.temperature,
        )
        # El SDK devuelve content=None cuando no hay texto (p. ej. solo tool calls).
        content = completion.choices[0].message.content or ""

        logger.debug("Respuesta del modelo: %r", content)
        return LLMResponse(content=content)
