"""Herramienta calculator: evalúa una expresión aritmética controlada.

No usa `eval` ni `exec` en ningún momento. La expresión se parsea con
`ast.parse` y el árbol resultante se interpreta a mano, aceptando solo un
subconjunto muy reducido de nodos (números y operadores aritméticos).
Cualquier otra construcción de Python (llamadas a función, nombres,
atributos, colecciones, comprensiones, etc.) no tiene una rama que la
interprete y provoca un `ValueError` explícito antes de ejecutarse nada.

Como defensa adicional, antes incluso de parsear se valida que la expresión
solo contenga caracteres de un whitelist muy estricto (dígitos, operadores,
paréntesis y espacios) — sin letras ni comas, ese vocabulario ya es
insuficiente para construir una llamada, un nombre o una colección en
Python, así que bloquea la inmensa mayoría de intentos de inyección antes de
que el parser de `ast` entre en juego.

También se limita la magnitud del resultado (`_MAX_RESULT_MAGNITUDE`), tanto
en cada paso intermedio como en el resultado final, para evitar números
desproporcionadamente grandes generados por cadenas de operaciones (no solo
por `**`, que ya tiene su propio límite de exponente).
"""

from __future__ import annotations

import ast
import json
import operator
from typing import Any

_MAX_EXPRESSION_LENGTH = 200
_MAX_EXPONENT = 1000
_MAX_RESULT_MAGNITUDE = 10**15
_ALLOWED_CHARS = set("0123456789.+-*/()% \t\n")

_BIN_OPERATORS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorTool:
    """Evalúa una expresión aritmética controlada y devuelve un resultado estructurado.

    Sin I/O externo, sin `eval`/`exec` — el árbol de la expresión se interpreta
    a mano con una whitelist estricta de nodos permitidos.
    """

    name = "calculator"
    description = (
        "Evalúa una expresión aritmética: suma, resta, multiplicación, división, "
        "potencia (**), módulo (%) y paréntesis. Ejemplos válidos: '12 * 7', "
        "'100 / 4', '2 ** 10', '(3 + 4) * 2'. Úsala siempre que el usuario pida "
        "un cálculo."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expresión aritmética a evaluar, ej. '12 * (7 + 3) / 2'",
            },
        },
        "required": ["expression"],
        "additionalProperties": False,
    }

    def run(self, *, expression: str) -> str:
        result = _evaluate(expression)
        return json.dumps({"expression": expression, "result": result})


def _evaluate(expression: str) -> int | float:
    if not expression or not expression.strip():
        raise ValueError("La expresión no puede estar vacía")
    if len(expression) > _MAX_EXPRESSION_LENGTH:
        raise ValueError(f"La expresión supera el máximo de {_MAX_EXPRESSION_LENGTH} caracteres")
    if not set(expression) <= _ALLOWED_CHARS:
        raise ValueError("La expresión contiene caracteres no permitidos")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Expresión inválida: {exc.msg}") from exc

    try:
        result = _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise ValueError("División por cero") from exc
    except OverflowError as exc:
        raise ValueError("El resultado es demasiado grande para calcularse") from exc

    _check_magnitude(result)
    return result


def _check_magnitude(value: int | float) -> None:
    if abs(value) > _MAX_RESULT_MAGNITUDE:
        raise ValueError(f"El resultado supera el máximo permitido ({_MAX_RESULT_MAGNITUDE})")


def _eval_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, int | float):
            raise ValueError(f"Valor no permitido: {node.value!r}")
        return node.value

    if isinstance(node, ast.BinOp):
        op_func = _BIN_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Operador no soportado: {type(node.op).__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
            raise ValueError(f"Exponente demasiado grande (máximo {_MAX_EXPONENT})")
        result = op_func(left, right)
        _check_magnitude(result)
        return result

    if isinstance(node, ast.UnaryOp):
        op_func = _UNARY_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Operador unario no soportado: {type(node.op).__name__}")
        return op_func(_eval_node(node.operand))

    raise ValueError(f"Construcción no permitida en la expresión: {type(node).__name__}")
