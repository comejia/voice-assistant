import logging

from voice_assistant.llm import LLMProvider, Message, Role

from .agent import Agent
from .agent_config import AgentConfig

logger = logging.getLogger(__name__)


class SimpleAgent(Agent):
    """Agente que resuelve cada pedido con una sola llamada al modelo.

    Acumula la conversación para dar contexto a las respuestas siguientes. No ejecuta
    herramientas.
    """

    def __init__(self, llm: LLMProvider, config: AgentConfig):
        self._llm = llm
        self._config = config
        # Fuera de _history para que reset() no lo borre junto con la conversación.
        self._system = Message(role=Role.SYSTEM, content=config.system_prompt)
        self._history: list[Message] = []

    def run(self, text: str) -> str:
        self._history.append(Message(role=Role.USER, content=text))

        response = self._llm.chat([self._system, *self._history])

        self._history.append(Message(role=Role.ASSISTANT, content=response.content))

        if not self._config.keep_history:
            self.reset()

        return response.content

    def reset(self) -> None:
        self._history.clear()
        logger.debug("Historial del agente reiniciado")
