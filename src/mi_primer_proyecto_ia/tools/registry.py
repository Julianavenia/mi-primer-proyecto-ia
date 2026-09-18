import logging
from typing import Any

from mi_primer_proyecto_ia.config import Settings
from mi_primer_proyecto_ia.tools.base import Tool
from mi_primer_proyecto_ia.tools.calculator import CalculatorTool
from mi_primer_proyecto_ia.tools.list_files import ListFilesTool
from mi_primer_proyecto_ia.tools.read_file import ReadFileTool
from mi_primer_proyecto_ia.tools.workspace import WorkspaceError, WorkspaceSandbox

logger = logging.getLogger(__name__)


def build_default_tools(settings: Settings) -> list[Tool]:
    """Tools activas según la configuración.

    Si el workspace no existe, las tools de archivos NO se registran (el agente
    sigue funcionando con el resto) en vez de fallar al importar el módulo.
    """
    tools: list[Tool] = [CalculatorTool()]
    try:
        sandbox = WorkspaceSandbox(
            root=settings.workspace_root,
            allowed_extensions=settings.workspace_allowed_extensions,
            max_read_bytes=settings.workspace_max_read_bytes,
            max_list_entries=settings.workspace_max_list_entries,
        )
    except WorkspaceError:
        logger.warning(
            "Workspace %r no disponible: tools list_files/read_file desactivadas.",
            settings.workspace_root,
        )
    else:
        tools.extend([ListFilesTool(sandbox), ReadFileTool(sandbox)])
    return tools


_TOOLS: dict[str, Tool] = {tool.name: tool for tool in build_default_tools(Settings())}


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
