from collections.abc import Sequence

from voice_assistant.agent import AgentConfig, SimpleAgent
from voice_assistant.llm import LLMProvider, LLMResponse, Message, Role


class FakeLLM(LLMProvider):
    """LLMProvider de prueba que responde un texto fijo.

    Expone ``last_messages`` para verificar qué conversación le arma el agente.
    """

    def __init__(self, reply: str = "ok"):
        self.reply = reply
        self.last_messages: list[Message] = []

    def chat(self, messages: Sequence[Message]) -> LLMResponse:
        self.last_messages = list(messages)
        return LLMResponse(content=self.reply)


def make_agent(keep_history: bool = True, reply: str = "ok") -> tuple[SimpleAgent, FakeLLM]:
    llm = FakeLLM(reply=reply)
    agent = SimpleAgent(llm, AgentConfig(system_prompt="sos deby", keep_history=keep_history))
    return agent, llm


def test_run_devuelve_la_respuesta_del_modelo():
    agent, _ = make_agent(reply="hola, soy deby")

    assert agent.run("hola") == "hola, soy deby"


def test_run_antepone_el_system_prompt_y_el_pedido():
    agent, llm = make_agent()

    agent.run("prende la luz")

    assert llm.last_messages == [
        Message(role=Role.SYSTEM, content="sos deby"),
        Message(role=Role.USER, content="prende la luz"),
    ]


def test_run_acumula_el_historial_entre_turnos():
    agent, llm = make_agent(reply="listo")

    agent.run("prende la luz")
    agent.run("y apagala")

    assert llm.last_messages == [
        Message(role=Role.SYSTEM, content="sos deby"),
        Message(role=Role.USER, content="prende la luz"),
        Message(role=Role.ASSISTANT, content="listo"),
        Message(role=Role.USER, content="y apagala"),
    ]


def test_run_sin_memoria_no_recuerda_turnos_previos():
    agent, llm = make_agent(keep_history=False)

    agent.run("prende la luz")
    agent.run("y apagala")

    assert llm.last_messages == [
        Message(role=Role.SYSTEM, content="sos deby"),
        Message(role=Role.USER, content="y apagala"),
    ]


def test_reset_descarta_el_historial_pero_conserva_el_system_prompt():
    agent, llm = make_agent()

    agent.run("prende la luz")
    agent.reset()
    agent.run("hola")

    assert llm.last_messages == [
        Message(role=Role.SYSTEM, content="sos deby"),
        Message(role=Role.USER, content="hola"),
    ]
