from contextlib import nullcontext as does_not_raise
from math import inf
from typing import Any, Callable

import pytest

from models.calculator import Operation
from utility import find_first, parse_arguments

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


@pytest.mark.parametrize(
    "data", [{"x": 1}, {"y": {"x": 1}}, {"x": 1, "y": {"x": 2}}]
)
def test_find_first(data: dict[str, int]):
    assert find_first(data, "x") == 1


@pytest.mark.parametrize(
    "data", [{"x": 1, "y": 2}, {"x": "1", "y": "2"}, {"x": 1, "z": {"y": 2}}]
)
def test_parse_arguments(data: dict[str, Any]):
    d1 = {"x": 1, "y": 2}
    assert parse_arguments(add, d1) == d1
    d2 = {"x": "1", "y": "2"}
    assert parse_arguments(add, d2) == d2
