from fastapi.testclient import TestClient

from mi_primer_proyecto_ia.agent.fake_client import (
    FakeAnthropicClient,
    FakeMessage,
    FakeTextBlock,
    FakeToolUseBlock,
)
from mi_primer_proyecto_ia.api.deps import get_conversation_store, get_llm_client, get_settings
from mi_primer_proyecto_ia.api.main import app
from mi_primer_proyecto_ia.config import Settings


def _client_with_script(script, max_tool_iterations: int = 10) -> TestClient:
    # Una sola instancia, reutilizada en cada llamada: FakeAnthropicClient consume
    # su guion con pop(0), así que el override debe devolver siempre el mismo
    # objeto (no reconstruirlo por request) para que el guion avance entre llamadas.
    fake_client = FakeAnthropicClient(script=script)
    app.dependency_overrides[get_llm_client] = lambda: fake_client
    app.dependency_overrides[get_conversation_store] = lambda: {}
    app.dependency_overrides[get_settings] = lambda: Settings(
        max_tool_iterations=max_tool_iterations
    )
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_post_chat_returns_reply_and_new_conversation_id():
    client = _client_with_script(
        [FakeMessage(content=[FakeTextBlock(text="¡Hola!")], stop_reason="end_turn")]
    )

    response = client.post("/chat", json={"message": "hola"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "¡Hola!"
    assert body["conversation_id"]


def test_post_chat_reuses_conversation_id_and_grows_history():
    script = [
        FakeMessage(content=[FakeTextBlock(text="primera respuesta")], stop_reason="end_turn"),
        FakeMessage(content=[FakeTextBlock(text="segunda respuesta")], stop_reason="end_turn"),
    ]
    client = _client_with_script(script)

    first = client.post("/chat", json={"message": "hola"})
    conversation_id = first.json()["conversation_id"]

    second = client.post(
        "/chat", json={"message": "otra vez", "conversation_id": conversation_id}
    )

    assert second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id
    assert second.json()["reply"] == "segunda respuesta"


def test_post_chat_executes_tool_use_cycle():
    script = [
        FakeMessage(
            content=[
                FakeToolUseBlock(id="call_1", name="calculator", input={"expression": "12 * 7"})
            ],
            stop_reason="tool_use",
        ),
        FakeMessage(content=[FakeTextBlock(text="El resultado es 84")], stop_reason="end_turn"),
    ]
    client = _client_with_script(script)

    response = client.post("/chat", json={"message": "cuánto es 12 * 7"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "El resultado es 84"
    assert body["tool_calls"] == [
        {
            "name": "calculator",
            "input": {"expression": "12 * 7"},
            "result": '{"expression": "12 * 7", "result": 84}',
            "is_error": False,
        }
    ]


def test_post_chat_returns_empty_tool_calls_when_no_tool_is_used():
    client = _client_with_script(
        [FakeMessage(content=[FakeTextBlock(text="¡Hola!")], stop_reason="end_turn")]
    )

    response = client.post("/chat", json={"message": "hola"})

    assert response.json()["tool_calls"] == []


def test_post_chat_rejects_invalid_body():
    client = _client_with_script([])

    response = client.post("/chat", json={})

    assert response.status_code == 422


def test_post_chat_returns_502_when_tool_iteration_limit_is_reached():
    script = [
        FakeMessage(
            content=[
                FakeToolUseBlock(id=f"call_{i}", name="calculator", input={"expression": "1 + 1"})
            ],
            stop_reason="tool_use",
        )
        for i in range(2)
    ]
    client = _client_with_script(script, max_tool_iterations=2)

    response = client.post("/chat", json={"message": "x"})

    assert response.status_code == 502
