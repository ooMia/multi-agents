import operator

import pytest

from utility import find_first, parse_arguments

add = operator.add
subtract = operator.sub
multiply = operator.mul
divide = operator.truediv


@pytest.mark.parametrize("data", [{"x": 1}, {"y": {"x": 1}}, {"x": 1, "y": {"x": 2}}])
def test_find_first(data: dict[str, int]):
    assert find_first(data, "x") == 1


def test_parse_arguments():
    d1 = {"a": 1, "b": 2}
    assert parse_arguments(add, d1) == d1
    d2 = {"a": "1", "b": "2"}
    assert parse_arguments(add, d2) == d2
    d3 = {"a": 1, "z": {"b": 2}}
    assert parse_arguments(add, d3) == d1
