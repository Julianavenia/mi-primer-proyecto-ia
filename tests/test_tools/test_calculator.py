import pytest

from mi_primer_proyecto_ia.tools.calculator import CalculatorTool


@pytest.mark.parametrize(
    ("left", "operator", "right", "expected"),
    [
        (2, "+", 3, "5"),
        (10, "-", 4, "6"),
        (6, "*", 7, "42"),
        (9, "/", 2, "4.5"),
    ],
)
def test_calculator_basic_operations(left, operator, right, expected):
    tool = CalculatorTool()
    assert tool.run(left=left, operator=operator, right=right) == expected


def test_calculator_division_by_zero_raises():
    tool = CalculatorTool()
    with pytest.raises(ValueError, match="División por cero"):
        tool.run(left=1, operator="/", right=0)


def test_calculator_unsupported_operator_raises():
    tool = CalculatorTool()
    with pytest.raises(ValueError, match="Operador no soportado"):
        tool.run(left=1, operator="%", right=2)
