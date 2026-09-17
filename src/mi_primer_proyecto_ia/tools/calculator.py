from typing import Any

_OPERATORS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


class CalculatorTool:
    """Herramienta determinista: una operación aritmética simple de dos operandos.

    Sin I/O externo, sin dependencias de red — pensada para ser la primera tool
    del sistema, fácil de razonar y de testear.
    """

    name = "calculator"
    description = (
        "Realiza una operación aritmética simple entre dos números: suma, resta, "
        "multiplicación o división. Úsala siempre que el usuario pida un cálculo."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "left": {"type": "number", "description": "Operando izquierdo"},
            "operator": {"type": "string", "enum": ["+", "-", "*", "/"]},
            "right": {"type": "number", "description": "Operando derecho"},
        },
        "required": ["left", "operator", "right"],
        "additionalProperties": False,
    }

    def run(self, *, left: float, operator: str, right: float) -> str:
        if operator not in _OPERATORS:
            raise ValueError(f"Operador no soportado: {operator!r}")
        if operator == "/" and right == 0:
            raise ValueError("División por cero")
        result = _OPERATORS[operator](left, right)
        return str(result)
