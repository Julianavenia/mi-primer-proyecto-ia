"""Cliente simulado del SDK de Anthropic.

Replica la misma "forma" que usa el código del agente contra el SDK real
(`client.messages.create(...)` devolviendo un objeto con `.content` y
`.stop_reason`), pero sin red, sin API key y sin coste. Esto permite
desarrollar y probar `agent/conversation.py` y `agent/loop.py` sin depender
de la API real de Anthropic; el día que se quiera usar la API real, solo
cambia qué cliente construye `agent/client.py` — el resto del código no se
entera de la diferencia.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class FakeToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: str = "tool_use"


@dataclass
class FakeMessage:
    content: list[FakeTextBlock | FakeToolUseBlock]
    stop_reason: str


_ARITHMETIC_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)")


def _last_user_text(messages: list[dict[str, Any]]) -> str | None:
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(message["content"], str):
            return message["content"]
    return None


def _last_message_tool_result_text(messages: list[dict[str, Any]]) -> str | None:
    if not messages:
        return None
    last = messages[-1]
    if last["role"] != "user" or isinstance(last["content"], str):
        return None
    for block in last["content"]:
        if block.get("type") == "tool_result":
            return str(block.get("content"))
    return None


class _FakeMessages:
    def __init__(self, script: list[FakeMessage] | None) -> None:
        self._script = list(script) if script is not None else None

    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **_: Any,
    ) -> FakeMessage:
        if self._script is not None:
            if not self._script:
                raise RuntimeError(
                    "FakeAnthropicClient: se agotó el guion de respuestas simuladas."
                )
            return self._script.pop(0)
        return self._heuristic_reply(messages)

    def _heuristic_reply(self, messages: list[dict[str, Any]]) -> FakeMessage:
        tool_result_text = _last_message_tool_result_text(messages)
        if tool_result_text is not None:
            return FakeMessage(
                content=[FakeTextBlock(text=f"(simulado) El resultado es {tool_result_text}.")],
                stop_reason="end_turn",
            )

        user_text = _last_user_text(messages) or ""
        match = _ARITHMETIC_RE.search(user_text)
        if match:
            left, operator, right = match.groups()
            return FakeMessage(
                content=[
                    FakeToolUseBlock(
                        id="fake_tool_use_1",
                        name="calculator",
                        input={"left": float(left), "operator": operator, "right": float(right)},
                    )
                ],
                stop_reason="tool_use",
            )

        return FakeMessage(
            content=[
                FakeTextBlock(
                    text=(
                        "(simulado) No hay ningún LLM real detrás de esta respuesta "
                        "(LLM_BACKEND=fake). Pídeme un cálculo como '12 * 7' para ver "
                        "el ciclo de tool use en acción."
                    )
                )
            ],
            stop_reason="end_turn",
        )


class FakeAnthropicClient:
    """Sustituto local de `anthropic.Anthropic`, sin red ni API key.

    - Con `script`: devuelve esas respuestas en orden, una por llamada (uso en tests,
      totalmente determinista).
    - Sin `script`: heurística que simula un ciclo de tool use para expresiones
      aritméticas y un texto fijo para cualquier otro mensaje (uso interactivo en
      `scripts/chat_cli.py`).
    """

    def __init__(self, script: list[FakeMessage] | None = None) -> None:
        self.messages = _FakeMessages(script)
