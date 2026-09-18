import json

import pytest

from mi_primer_proyecto_ia.tools.calculator import CalculatorTool


def _result(expression: str) -> int | float:
    payload = json.loads(CalculatorTool().run(expression=expression))
    return payload["result"]


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 3", 5),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("9 / 2", 4.5),
        ("(3 + 4) * 2", 14),
        ("2 ** 10", 1024),
        ("-5 + 3", -2),
        ("10 % 3", 1),
        ("10 // 3", 3),
        ("7 // 2", 3),
        ("2 ** 0.5", 2**0.5),
        ("(2 + 3) * 4", 20),
    ],
)
def test_calculator_valid_expressions(expression, expected):
    assert _result(expression) == expected


def test_calculator_returns_structured_json():
    payload = json.loads(CalculatorTool().run(expression="12 * 7"))
    assert payload == {"expression": "12 * 7", "result": 84}


def test_calculator_division_by_zero_raises():
    with pytest.raises(ValueError, match="División por cero"):
        CalculatorTool().run(expression="1 / 0")


def test_calculator_empty_expression_raises():
    with pytest.raises(ValueError, match="vacía"):
        CalculatorTool().run(expression="   ")


def test_calculator_expression_too_long_raises():
    huge_expression = "1" + "+1" * 200
    with pytest.raises(ValueError, match="máximo"):
        CalculatorTool().run(expression=huge_expression)


def test_calculator_exponent_too_large_raises():
    with pytest.raises(ValueError, match="Exponente"):
        CalculatorTool().run(expression="2 ** 999999")


def test_calculator_result_too_large_raises():
    with pytest.raises(ValueError, match="máximo permitido"):
        CalculatorTool().run(expression="999999999999 * 999999999999 * 999999999999")


def test_calculator_invalid_expression_raises():
    with pytest.raises(ValueError, match="inválida"):
        CalculatorTool().run(expression="2 + ")


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo hi')",  # letras: bloqueado por el whitelist de caracteres
        "open('/etc/passwd').read()",
        "().__class__.__bases__",
        "[x for x in range(3)]",
        "lambda: 1",
        "print(1)",
        "a + 1",
        "1; 2",
        "1 2",  # sintaxis inválida (sin operador entre los números)
        "()",  # sintaxis inválida (tupla vacía)
    ],
)
def test_calculator_rejects_unsafe_or_invalid_expressions(expression):
    with pytest.raises(ValueError):
        CalculatorTool().run(expression=expression)
