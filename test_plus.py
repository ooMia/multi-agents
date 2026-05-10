from model import Result, plus


def test_answer():
    assert plus(1, 1).value == 2
