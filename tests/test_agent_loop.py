import json

import pytest

from mi_primer_proyecto_ia.agent.fake_client import (
    FakeAnthropicClient,
    FakeMessage,
    FakeTextBlock,
    FakeToolUseBlock,
)
from mi_primer_proyecto_ia.agent.loop import ToolIterationLimitError, run_agent_turn
from mi_primer_proyecto_ia.config import Settings


def test_run_agent_turn_without_tool_use_returns_text_directly():
    client = FakeAnthropicClient(
        script=[
            FakeMessage(
                content=[FakeTextBlock(text="Hola, ¿en qué te ayudo?")], stop_reason="end_turn"
            )
        ]
    )
    history = []

    reply = run_agent_turn(client, Settings(), history, "Hola")

    assert reply == "Hola, ¿en qué te ayudo?"
    assert history[0] == {"role": "user", "content": "Hola"}
    assert history[1]["role"] == "assistant"


def test_run_agent_turn_executes_tool_and_returns_final_reply():
    client = FakeAnthropicClient(
        script=[
            FakeMessage(
                content=[
                    FakeToolUseBlock(
                        id="call_1",
                        name="calculator",
                        input={"expression": "12 * 7"},
                    )
                ],
                stop_reason="tool_use",
            ),
            FakeMessage(content=[FakeTextBlock(text="El resultado es 84")], stop_reason="end_turn"),
        ]
    )
    history = []

    reply = run_agent_turn(client, Settings(), history, "cuánto es 12 * 7")

    assert reply == "El resultado es 84"
    # user, assistant(tool_use), user(tool_result), assistant(end_turn)
    assert len(history) == 4
    tool_result_block = history[2]["content"][0]
    assert tool_result_block["type"] == "tool_result"
    assert tool_result_block["tool_use_id"] == "call_1"
    assert json.loads(tool_result_block["content"]) == {"expression": "12 * 7", "result": 84}


def test_run_agent_turn_reports_error_for_unknown_tool():
    client = FakeAnthropicClient(
        script=[
            FakeMessage(
                content=[FakeToolUseBlock(id="call_1", name="tool_inexistente", input={})],
                stop_reason="tool_use",
            ),
            FakeMessage(
                content=[FakeTextBlock(text="No pude usar esa herramienta.")],
                stop_reason="end_turn",
            ),
        ]
    )
    history = []

    run_agent_turn(client, Settings(), history, "usa una tool que no existe")

    tool_result_block = history[2]["content"][0]
    assert tool_result_block["is_error"] is True


def test_run_agent_turn_raises_after_max_iterations():
    # El fake siempre vuelve a pedir la misma tool: nunca llega a end_turn.
    keeps_calling_tool = [
        FakeMessage(
            content=[
                FakeToolUseBlock(
                    id=f"call_{i}",
                    name="calculator",
                    input={"expression": "1 + 1"},
                )
            ],
            stop_reason="tool_use",
        )
        for i in range(3)
    ]
    client = FakeAnthropicClient(script=keeps_calling_tool)
    history = []

    with pytest.raises(ToolIterationLimitError):
        run_agent_turn(client, Settings(max_tool_iterations=3), history, "x")
