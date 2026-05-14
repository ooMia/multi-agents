import pytest
from math import inf
from typing import Any, Callable
from utility import (
    add,
    find_first,
    parse_arguments,
    parse_numbers,
    subtract,
    multiply,
    divide,
    typesafe_call,
)
from contextlib import nullcontext as does_not_raise


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


@pytest.mark.parametrize(
    "func",
    [add, subtract, multiply, divide],
)
def test_inf_returns_none(func: Callable):
    assert func(inf, 1) is None
    assert func(1, inf) is None
    assert func(inf, inf) is None


@pytest.mark.parametrize(
    "func",
    [add, subtract, multiply, divide],
)
def test_none_returns_none(func: Callable):
    assert func(None, 1) is None
    assert func(1, None) is None
    assert func(None, None) is None


@pytest.mark.parametrize(
    "dividend",
    [0, inf],
)
def test_divide_by_zero_returns_none(dividend: float):
    with does_not_raise():
        assert divide(dividend, 0) is None


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("100.4을 4로 나누면?", [100.4, 4]),
        ("5를 절반으로 나누면?", [5]),
        ("5.2의 절반은?", [5.2]),
        ("-2.125의 두 배는??", [-2.125]),
        ("양의 무한대를 절반으로 나누면?", []),
        ("무한대에 0을 더하면 어떻게 돼?", [0]),
    ],
)
def test_parse_numbers(expression: str, expected: list[float]):
    assert parse_numbers(expression) == expected


def test_add():
    assert add(0, 0) == 0


@pytest.mark.parametrize(
    "data",
    [{"x": 1}, {"y": {"x": 1}}, {"x": 1, "y": {"x": 2}}],
)
def test_find_first(data: dict[str, int]):
    assert find_first(data, "x") == 1


@pytest.mark.parametrize(
    "data",
    [{"x": 1, "y": 2}, {"x": "1", "y": "2"}, {"x": 1, "z": {"y": 2}}],
)
def test_parse_arguments(data: dict[str, Any]):
    d1 = {"x": 1, "y": 2}
    assert parse_arguments(add, d1) == d1
    d2 = {"x": "1", "y": "2"}
    assert parse_arguments(add, d2) == d2


def test_typesafe_call():
    arg = {"x": 1, "y": 2}
    assert typesafe_call(add, arg) == 3
