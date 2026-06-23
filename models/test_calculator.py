import math
import random
from contextlib import nullcontext as does_not_raise
from math import inf
from typing import Callable, Optional

import pytest

from models.calculator import Calculator, Operation


@pytest.fixture
def calculate():
    def _execute(expression: str) -> Optional[float]:
        return Calculator().calculate(expression)

    return _execute


add = Operation.add
subtract = Operation.subtract
multiply = Operation.multiply
divide = Operation.divide


@pytest.mark.parametrize(
    "func,expectation",
    [
        (add, does_not_raise()),
        (subtract, does_not_raise()),
        (multiply, does_not_raise()),
        (divide, does_not_raise()),
    ],
)
def test_common_not_throws(func: Callable, expectation):
    with expectation:
        assert func(1.3, 3.2) is not None


@pytest.mark.parametrize("func", [add, subtract, multiply, divide])
def test_inf_returns_none(func: Callable):
    assert func(inf, 1) is None
    assert func(1, inf) is None
    assert func(inf, inf) is None


@pytest.mark.parametrize("func", [add, subtract, multiply, divide])
def test_none_returns_none(func: Callable):
    assert func(None, 1) is None
    assert func(1, None) is None
    assert func(None, None) is None


@pytest.mark.parametrize("dividend", [0, inf])
def test_divide_by_zero_returns_none(dividend: float):
    with does_not_raise():
        assert divide(dividend, 0) is None


# INTEGRATION TESTS

FINITE_CASES = [
    (0, 0),
    (1, 1),
    (-1, 1),
    (1, -1),
    (-1, -1),
    (15, 27),
    (5.5, 2.8),
    (-99999999, 0.000001),
    (1e-9, 1e9),
]


@pytest.mark.slow
@pytest.mark.parametrize(
    "operator,expected",
    [
        ("+", add),
        ("-", subtract),
        ("*", multiply),
        ("/", divide),
    ],
)
@pytest.mark.parametrize("x,y", FINITE_CASES)
def test_finite_operations(calculate, operator, expected, x: float, y: float):
    result = calculate(f"{x} {operator} {y} = ?")
    if operator == "/" and y == 0:
        assert result is None
    else:
        assert result == pytest.approx(expected(x, y))


@pytest.mark.slow
@pytest.mark.parametrize(
    "query,expected",
    [
        ("100.4를 4로 나누면?", 25.1),
        ("5를 반으로 나누면?", 2.5),
        ("2.5의 절반은?", 1.25),
        ("-2.125의 두 배는??", -4.25),
        ("What is 100.4 divided by 4?", 25.1),
        ("Divide 5 in half.", 2.5),
        ("What is half of 2.5?", 1.25),
        ("What is twice of -2.125??", -4.25),
    ],
)
def test_natural_language(calculate, query: str, expected: float):
    assert calculate(query) == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "query",
    [
        "∞ 더하기 -8는?",
        "-∞ 곱하기 3은?",
        "무한대 더하기 -8는?",
        "無限大 더하기 -8는?",
    ],
)
@pytest.mark.xfail(reason="LLM output is probabilistic")
def test_infinity(calculate, query: str):
    assert calculate(query) is None


@pytest.mark.fuzz
@pytest.mark.slow
@pytest.mark.xfail(reason="LLM output is probabilistic")
@pytest.mark.parametrize("_", range(50))
def test_randomized_operations(calculate, _):
    RANDOM_OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}
    operator = random.choice(list(RANDOM_OPERATIONS.keys()))

    x = random.uniform(-1e12, 1e12)
    y = random.uniform(-1e12, 1e12)

    if operator == "/":
        while math.isclose(y, 0.0):
            y = random.uniform(-1e12, 1e12)

    expected = RANDOM_OPERATIONS[operator](x, y)
    query = f"{x} {operator} {y} = ?"
    result = calculate(query)

    assert result == pytest.approx(expected, rel=1e-9, abs=1e-9)
