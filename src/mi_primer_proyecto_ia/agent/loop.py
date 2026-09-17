from typing import Any

from anthropic.types import MessageParam

from mi_primer_proyecto_ia.config import Settings
from mi_primer_proyecto_ia.tools.registry import get_tool, get_tool_schemas


class ToolIterationLimitError(RuntimeError):
    """El agente superó el número máximo de iteraciones de tool use permitidas."""


def run_agent_turn(
    client: Any, settings: Settings, history: list[MessageParam], user_message: str
) -> str:
    """Ejecuta un turno completo del agente.

    Llama al modelo, ejecuta las tools que pida (si las pide), le devuelve los
    resultados, y repite hasta que responda con texto final
    (`stop_reason != "tool_use"`) o se alcance `settings.max_tool_iterations`
    (evita loops infinitos). `history` se muta in-place con los mensajes de este
    turno. Es agnóstico a si `client` es el `FakeAnthropicClient` o el SDK real.
    """
    history.append({"role": "user", "content": user_message})
    tool_schemas = get_tool_schemas()

    for _ in range(settings.max_tool_iterations):
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.max_tokens,
            messages=history,
            tools=tool_schemas,
        )
        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        tool_results = [
            _execute_tool_use(block) for block in response.content if block.type == "tool_use"
        ]
        history.append({"role": "user", "content": tool_results})

    raise ToolIterationLimitError(
        f"Se alcanzó el límite de {settings.max_tool_iterations} iteraciones de "
        "tool use sin una respuesta final."
    )


def _execute_tool_use(block: Any) -> dict[str, Any]:
    try:
        tool = get_tool(block.name)
        result = tool.run(**block.input)
        return {"type": "tool_result", "tool_use_id": block.id, "content": result}
    except Exception as exc:
        return {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(exc),
            "is_error": True,
        }
