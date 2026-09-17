from anthropic import Anthropic
from anthropic.types import MessageParam

from mi_primer_proyecto_ia.config import Settings


class Conversation:
    """Mantiene el historial de una conversación y habla con Claude.

    La Messages API es stateless: hay que reenviar todo el historial en cada
    llamada. Esta clase solo lo hace explícito; no persiste nada entre procesos.
    """

    def __init__(self, client: Anthropic, settings: Settings) -> None:
        self._client = client
        self._settings = settings
        self.history: list[MessageParam] = []

    def send(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        response = self._client.messages.create(
            model=self._settings.model_name,
            max_tokens=self._settings.max_tokens,
            messages=self.history,
        )

        self.history.append({"role": "assistant", "content": response.content})
        return "".join(block.text for block in response.content if block.type == "text")
