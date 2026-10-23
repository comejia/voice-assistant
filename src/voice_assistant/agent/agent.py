from abc import ABC, abstractmethod


class Agent(ABC):
    """Orquesta la conversación entre el usuario y el modelo.

    Las implementaciones definen la estrategia: una sola llamada al modelo, uso de
    herramientas, routing, etc.
    """

    @abstractmethod
    def run(self, text: str) -> str:
        """Resuelve un pedido del usuario y devuelve la respuesta a reproducir."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Descarta el estado de la conversación acumulado.

        Debe llamarse entre conversaciones independientes para que lo dicho antes no
        contamine el contexto del siguiente pedido.
        """
        ...
