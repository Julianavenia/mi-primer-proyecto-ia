from dataclasses import dataclass
from unittest.mock import MagicMock

from mi_primer_proyecto_ia.agent.conversation import Conversation
from mi_primer_proyecto_ia.config import Settings


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


def _settings() -> Settings:
    return Settings(anthropic_api_key="test-key")


def test_conversation_send_returns_text_and_updates_history():
    fake_client = MagicMock()
    fake_client.messages.create.return_value = MagicMock(content=[FakeTextBlock("¡Hola!")])

    conversation = Conversation(fake_client, _settings())
    reply = conversation.send("Hola")

    assert reply == "¡Hola!"
    assert conversation.history[0] == {"role": "user", "content": "Hola"}
    assert conversation.history[1]["role"] == "assistant"
    fake_client.messages.create.assert_called_once()
