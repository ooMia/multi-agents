import pytest
from model import execute_math


@pytest.mark.parametrize("x,y", [(0, 0), (5.5, 2.8), (-1, 1)])
def test_add_finite(x: float, y: float):
    assert execute_math(f"{x} 더하기 {y}는?") == x + y


@pytest.mark.parametrize(
    "x,y", [(float("inf"), 0), (float("-inf"), 0), (-float("-inf"), 0)]
)
@pytest.mark.xfail(
    reason="Currently, the model does not handle infinite results correctly."
)
def test_add_infinite(x: float, y: float):
    assert execute_math(f"{x} 더하기 {y}는?") is None


@pytest.mark.parametrize(
    "x,y", [("무한대", 0), ("∞", 0), ("無限", 0)]
)
@pytest.mark.xfail(
    reason="Currently, the model does not handle infinite results correctly."
)
def test_add_infinite_as_chars(x: float, y: float):
    assert execute_math(f"{x} 더하기 {y}는?") is None
