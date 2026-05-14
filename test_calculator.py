import pytest
from model import execute_math


@pytest.mark.parametrize("x,y", [(0, 0), (5.5, 2.8), (-1, 1), (15, 27)])
def test_add_finite(x: float, y: float):
    assert execute_math(f"{x} + {y} = ?") == x + y


@pytest.mark.parametrize("x,y", [(0, 0), (5.5, 2.8), (-1, 1), (15, 27)])
def test_subtract_finite(x: float, y: float):
    assert execute_math(f"{x} - {y} = ?") == x - y


@pytest.mark.parametrize("x,y", [(0, 0), (5.5, 2.8), (-1, 1), (15, 27)])
def test_multiply_finite(x: float, y: float):
    assert execute_math(f"{x} * {y} = ?") == x * y


@pytest.mark.parametrize("x,y", [(0, 0.1), (5.5, 2.8), (-1, 1), (15, 27)])
def test_divide_finite(x: float, y: float):
    assert execute_math(f"{x} / {y} = ?") == x / y


@pytest.mark.parametrize(
    "x,y",
    [
        (float("inf"), 8),
        (float("-inf"), 8),
        (-float("-inf"), 8),
        ("무한대", -8),
        ("∞", -8),
        ("無限大", -8),
    ],
)
def test_add_infinite(x: float, y: float):
    assert execute_math(f"{x} 더하기 {y}는?") is None


@pytest.mark.parametrize(
    "query,expected",
    [
        ("100.4를 4로 나누면?", 25.1),
        ("5를 반으로 나누면?", 2.5),
        ("2.5의 절반은?", 1.25),
        ("-2.125의 두 배는??", -4.25),
    ],
)
def test_natural_korean(query: str, expected: float | None):
    assert execute_math(query) == expected


@pytest.mark.parametrize(
    "query,expected",
    [
        ("What is 100.4 divided by 4?", 25.1),
        ("Divide 5 in half.", 2.5),
        ("What is half of 2.5?", 1.25),
        ("What is twice of -2.125??", -4.25),
    ],
)
def test_natural_english(query: str, expected: float | None):
    assert execute_math(query) == expected
