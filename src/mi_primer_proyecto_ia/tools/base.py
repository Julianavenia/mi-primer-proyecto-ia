from typing import Any, Protocol


class Tool(Protocol):
    """Contrato que debe cumplir cualquier herramienta registrada para el agente."""

    name: str
    description: str
    input_schema: dict[str, Any]

    def run(self, **kwargs: Any) -> str: ...
