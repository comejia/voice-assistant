from dataclasses import dataclass

_DEFAULT_SYSTEM_PROMPT = (
    "Sos Deby, un asistente de voz en español. Respondé de forma breve, clara y "
    "conversacional, pensada para ser leída en voz alta. Evitá listas, markdown y "
    "tecnicismos innecesarios."
)


@dataclass(frozen=True)
class AgentConfig:
    """Configuración del agente conversacional.

    Attributes:
        system_prompt: Instrucción de sistema que fija personalidad y estilo. El default
            está orientado a respuestas aptas para texto-a-voz.
        keep_history: Si es ``False``, cada ``run`` se resuelve sin recordar los pedidos
            anteriores (comandos sueltos en vez de conversación).
    """

    system_prompt: str = _DEFAULT_SYSTEM_PROMPT
    keep_history: bool = True
