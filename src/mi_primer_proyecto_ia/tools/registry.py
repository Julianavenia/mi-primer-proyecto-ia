from typing import Any

from mi_primer_proyecto_ia.tools.base import Tool
from mi_primer_proyecto_ia.tools.calculator import CalculatorTool

_TOOLS: dict[str, Tool] = {tool.name: tool for tool in [CalculatorTool()]}


def get_tool_schemas() -> list[dict[str, Any]]:
    """Lo que se envía a la Messages API en el parámetro `tools`."""
    return [
        {"name": tool.name, "description": tool.description, "input_schema": tool.input_schema}
        for tool in _TOOLS.values()
    ]


def get_tool(name: str) -> Tool:
    try:
        return _TOOLS[name]
    except KeyError:
        raise KeyError(f"Tool desconocida: {name!r}") from None
