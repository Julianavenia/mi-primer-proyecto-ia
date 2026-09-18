import pytest

from mi_primer_proyecto_ia.agent.fake_client import FakeAnthropicClient


def _ask(user_text: str):
    client = FakeAnthropicClient()
    return client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_text}],
        tools=[],
    )


@pytest.mark.parametrize(
    ("user_text", "expected_expression"),
    [
        ("cuánto es 2 ** 10", "2 ** 10"),
        ("calcula 10 % 3 por favor", "10 % 3"),
        ("necesito 10 // 3", "10 // 3"),
        ("resuelve (2 + 3) * 4", "(2 + 3) * 4"),
        ("cuánto da 2 + 3 * 4 - 1", "2 + 3 * 4 - 1"),
    ],
)
def test_heuristic_detects_expression_and_requests_calculator(user_text, expected_expression):
    response = _ask(user_text)

    assert response.stop_reason == "tool_use"
    tool_use_block = response.content[0]
    assert tool_use_block.name == "calculator"
    assert tool_use_block.input == {"expression": expected_expression}


def test_heuristic_ignores_plain_text_without_operator():
    response = _ask("tengo 3 gatos en casa")

    assert response.stop_reason == "end_turn"
    assert "no hay ningún llm real" in response.content[0].text.lower()


def test_heuristic_ignores_text_without_digits():
    response = _ask("hola, ¿cómo estás?")

    assert response.stop_reason == "end_turn"
    assert "no hay ningún llm real" in response.content[0].text.lower()


def test_heuristic_summarizes_successful_tool_result():
    client = FakeAnthropicClient()
    messages = [
        {"role": "user", "content": "cuánto es 2 ** 10"},
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "call_1",
                    "content": '{"expression": "2 ** 10", "result": 1024}',
                }
            ],
        },
    ]

    response = client.messages.create(
        model="claude-sonnet-5", max_tokens=1024, messages=messages, tools=[]
    )

    assert response.stop_reason == "end_turn"
    assert "1024" in response.content[0].text


def test_heuristic_shows_error_tool_result_as_is():
    client = FakeAnthropicClient()
    messages = [
        {"role": "user", "content": "cuánto es 1 / 0"},
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "call_1",
                    "content": "División por cero",
                    "is_error": True,
                }
            ],
        },
    ]

    response = client.messages.create(
        model="claude-sonnet-5", max_tokens=1024, messages=messages, tools=[]
    )

    assert response.stop_reason == "end_turn"
    assert "División por cero" in response.content[0].text
