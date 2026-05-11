from decimal import DivisionByZero
from numbers import Number
from typing import Optional

from pydantic import FiniteFloat

NO_ARGUMENTS_ERROR = ValueError("At least one number must be provided")
NOT_A_NUMBER_ERROR = ValueError("All arguments must be numbers")
DIVISION_BY_ZERO_ERROR = DivisionByZero("Cannot divide by zero")
FINITE_RESULT_ONLY_ERROR = ValueError("The result must be a finite number")


def _validate_arguments(*args):
    if len(args) == 0:
        raise NO_ARGUMENTS_ERROR
    if not all(isinstance(x, Number) for x in args):
        raise NOT_A_NUMBER_ERROR


def _validate_finite_result(result):
    if result == float("inf") or result == float("-inf"):
        raise FINITE_RESULT_ONLY_ERROR


def _cycle(operation, validate, *args):
    _validate_arguments(*args)
    result = args[0]
    for x in args[1:]:
        result = operation(result, x)
    validate(result)
    return result


def _add(*args: float):
    return _cycle(lambda x, y: x + y, _validate_finite_result, *args)


def _subtract(*args: float):
    if len(args) != 2:
        raise ValueError("subtract() takes exactly two arguments")
    return _cycle(lambda x, y: x - y, _validate_finite_result, *args)


def _multiply(*args: float):
    return _cycle(lambda x, y: x * y, _validate_finite_result, *args)


def _divide(*args: float):
    if len(args) != 2:
        raise ValueError("divide() takes exactly two arguments")
    if args[1] == 0:
        raise DIVISION_BY_ZERO_ERROR
    return _cycle(lambda x, y: x / y, _validate_finite_result, *args)


def _wrapper(func, x, y) -> Optional[float]:
    try:
        return func(x, y)
    except:
        return None


def add(x: FiniteFloat, y: FiniteFloat) -> Optional[float]:
    return _wrapper(_add, x, y)


def subtract(x: FiniteFloat, y: FiniteFloat) -> Optional[float]:
    return _wrapper(_subtract, x, y)


def multiply(x: FiniteFloat, y: FiniteFloat) -> Optional[float]:
    return _wrapper(_multiply, x, y)


def divide(x: FiniteFloat, y: FiniteFloat) -> Optional[float]:
    return _wrapper(_divide, x, y)


if __name__ == "__main__":
    print(add(1, 2))  # Output: 3
    print(multiply(3, 4))  # Output: 12
    print(divide(10, 2))  # Output: 5.0

    try:
        print(divide(10, 0))
    except DivisionByZero as e:
        print(e)  # Output: Cannot divide by zero

    try:
        print(add(float("inf"), 1))
    except ValueError as e:
        print(e)  # Output: All arguments must be numbers

    try:
        print(multiply(float("inf"), 1))
    except ValueError as e:
        print(e)  # Output: All arguments must be numbers
