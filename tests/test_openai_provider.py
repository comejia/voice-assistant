from unittest.mock import MagicMock, patch

from voice_assistant.llm import LLMConfig, Message, OpenAIProvider, Role


def make_provider(content: str | None) -> tuple[OpenAIProvider, MagicMock]:
    """Crea un OpenAIProvider con el cliente OpenAI mockeado.

    ``chat.completions.create`` devuelve una respuesta cuyo texto es ``content``.
    Retorna también el mock del cliente para inspeccionar la llamada.
    """
    with patch("voice_assistant.llm.openai_provider.OpenAI") as client_cls:
        client = MagicMock()
        message = MagicMock(content=content)
        client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=message)]
        )
        client_cls.return_value = client
        return OpenAIProvider(LLMConfig(model="gpt-4o-mini")), client


def test_chat_devuelve_el_texto_del_modelo():
    provider, _ = make_provider("hola, soy deby")

    assert provider.chat([Message(role=Role.USER, content="hola")]).content == "hola, soy deby"


def test_chat_devuelve_cadena_vacia_cuando_no_hay_texto():
    # El SDK entrega content=None cuando el modelo no produce texto (p. ej. si solo
    # pide ejecutar herramientas); se normaliza a "".
    provider, _ = make_provider(None)

    assert provider.chat([Message(role=Role.USER, content="hola")]).content == ""


def test_chat_traduce_los_mensajes_al_formato_del_sdk():
    provider, client = make_provider("ok")

    provider.chat(
        [
            Message(role=Role.SYSTEM, content="sos deby"),
            Message(role=Role.USER, content="hola"),
        ]
    )

    enviados = client.chat.completions.create.call_args.kwargs["messages"]
    assert enviados == [
        {"role": "system", "content": "sos deby"},
        {"role": "user", "content": "hola"},
    ]
