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

import json
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


_CANDIDATE_CHARS_RE = re.compile(r"[0-9+\-*/%().\s]+")
_OPERATOR_RE = re.compile(r"[+\-*/%]")


def _extract_expression_candidate(text: str) -> str | None:
    """Busca en `text` la primera racha de caracteres que "parece" una expresión
    aritmética: dígitos, operadores (`+ - * / % **`), paréntesis y espacios, con
    al menos un dígito y al menos un operador.

    Deliberadamente simple: no intenta extraer operandos ni validar la
    expresión, solo decide si vale la pena pedirle a `calculator` que la
    evalúe. La validación real (sintaxis, seguridad, límites) vive por
    completo en `tools/calculator.py` — este módulo nunca la importa ni
    duplica esa lógica.
    """
    for match in _CANDIDATE_CHARS_RE.finditer(text):
        candidate = match.group().strip()
        if any(char.isdigit() for char in candidate) and _OPERATOR_RE.search(candidate):
            return candidate
    return None


_READ_VERB_RE = re.compile(
    r"\b(lee|leer|lea|abre|abrir|muestra|mostrar|read|open|show|cat|contenido)\b", re.IGNORECASE
)
_LIST_VERB_RE = re.compile(r"\b(lista|listar|listame|list|ls|archivos|files)\b", re.IGNORECASE)
_PATH_ENDING_RE = re.compile(r"\.[A-Za-z]\w{0,4}$")


def _extract_path_candidate(text: str) -> str | None:
    """Primer token que "parece" una ruta: contiene '/' o termina en `.ext`.

    No valida nada -- se pasa tal cual a `read_file`, y es el sandbox de
    `tools/workspace.py` quien acepta o rechaza (así, "lee ../.env" muestra el
    rechazo real). Este módulo nunca importa `tools/`.
    """
    for raw in text.split():
        token = raw.strip("\"'`()[]{}").rstrip(".,;:!?")
        # Sin letras (`//`, `12/3`, `1.5`) es aritmética, no una ruta.
        if not re.search(r"[A-Za-z]", token):
            continue
        if "/" in token or _PATH_ENDING_RE.search(token):
            return token
    return None


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


def _display_result(tool_result_text: str) -> str:
    """Extrae un valor legible de un tool_result para el mensaje simulado.

    Las tools "estructuradas" (como calculator) devuelven JSON, ej.
    `{"expression": "12 * 7", "result": 84}`; aquí solo mostramos el campo
    `result`. Si el tool_result no es JSON (ej. un mensaje de error de texto
    plano), se muestra tal cual.
    """
    try:
        payload = json.loads(tool_result_text)
    except (json.JSONDecodeError, TypeError):
        return tool_result_text
    if isinstance(payload, dict) and "result" in payload:
        return str(payload["result"])
    return tool_result_text


_MAX_PREVIEW_CHARS = 400


def _summarize_tool_result(tool_result_text: str) -> str:
    """Frase del agente simulado según la forma del JSON devuelto por la tool."""
    try:
        payload = json.loads(tool_result_text)
    except (json.JSONDecodeError, TypeError):
        payload = None

    if isinstance(payload, dict) and isinstance(payload.get("files"), list):
        paths = [str(entry.get("path")) for entry in payload["files"] if isinstance(entry, dict)]
        if not paths:
            return "(simulado) No encontré archivos en el workspace."
        suffix = " (lista truncada)" if payload.get("truncated") else ""
        return f"(simulado) Encontré {len(paths)} archivo(s): {', '.join(paths)}{suffix}."

    if isinstance(payload, dict) and "content" in payload:
        content = str(payload["content"])
        preview = content[:_MAX_PREVIEW_CHARS]
        cut = " [...]" if len(content) > _MAX_PREVIEW_CHARS or payload.get("truncated") else ""
        return f"(simulado) Contenido de {payload.get('path')}:\n{preview}{cut}"

    return f"(simulado) El resultado es {_display_result(tool_result_text)}."


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
                content=[FakeTextBlock(text=_summarize_tool_result(tool_result_text))],
                stop_reason="end_turn",
            )

        user_text = _last_user_text(messages) or ""

        # Intención de archivos ANTES que la de cálculo: un nombre como
        # `datos-2024.csv` contiene '-' y dígitos y parecería una resta.
        path = _extract_path_candidate(user_text)
        if path and _READ_VERB_RE.search(user_text):
            return FakeMessage(
                content=[
                    FakeToolUseBlock(id="fake_tool_use_1", name="read_file", input={"path": path})
                ],
                stop_reason="tool_use",
            )
        if not path and _LIST_VERB_RE.search(user_text):
            return FakeMessage(
                content=[FakeToolUseBlock(id="fake_tool_use_1", name="list_files", input={})],
                stop_reason="tool_use",
            )

        candidate = None if path else _extract_expression_candidate(user_text)
        if candidate:
            return FakeMessage(
                content=[
                    FakeToolUseBlock(
                        id="fake_tool_use_1",
                        name="calculator",
                        input={"expression": candidate},
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
