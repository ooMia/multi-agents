import math
from typing import Any, Callable, Optional


def add(
    x: str | float,
    y: str | float,
) -> Optional[float]:
    """Adds x and y together (x + y).

    Use this tool whenever the operation between the numbers is addition (+).
    This includes cases where numbers themselves are negative (e.g., -1 + 1).
    """

    try:
        x, y = float(x), float(y)
        if math.isinf(x) or math.isinf(y):
            return None
        res = float(x) + float(y)
        return res if math.isfinite(res) else None
    except Exception:
        return None


def subtract(
    x: str | float,
    y: str | float,
) -> Optional[float]:
    """Subtracts y from x (x - y).

    Use this tool ONLY when the operation between the numbers is subtraction (-).
    DO NOT use this tool for addition queries just because a number starts with a minus sign (e.g., '-1 + 1').
    """

    try:
        x, y = float(x), float(y)
        if math.isinf(x) or math.isinf(y):
            return None
        res = float(x) - float(y)
        return res if math.isfinite(res) else None
    except Exception:
        return None


def multiply(
    x: str | float,
    y: str | float,
) -> Optional[float]:
    """Multiplies two numbers (x * y)."""
    try:
        x, y = float(x), float(y)
        if math.isinf(x) or math.isinf(y):
            return None
        res = float(x) * float(y)
        return res if math.isfinite(res) else None
    except Exception:
        return None


def divide(
    x: str | float,
    y: str | float,
) -> Optional[float]:
    """
    'x' is a dividend and 'y' is a divisor.
    Divides the dividend by the divisor (dividend / divisor).
    - dividend: The number to be divided.
    - divisor: The number to divide by.
    Returns None if divisor is 0.
    """

    try:
        x, y = float(x), float(y)
        if math.isinf(x) or math.isinf(y):
            return None
        if float(y) == 0.0:
            return None
        res = float(x) / float(y)
        return res if math.isfinite(res) else None
    except Exception:
        return None


import re


def parse_numbers(message: str) -> list[float]:
    numbers = re.findall(r"[+-]?(?:\d*\.\d+|\d+)", message)
    print(numbers)

    return list(map(float, numbers))


def find_first(d: dict[str, Any], target_key: str) -> Any:
    if target_key in d:
        return d[target_key]
    return next(
        (find_first(v, target_key) for v in d.values() if isinstance(v, dict)), None
    )


import inspect


def parse_arguments(func: Callable, raw_args: dict[str, Any]) -> dict[str, Any]:
    """함수 명세를 참조해서 인자 키워드에 맞는 값을 정리합니다."""
    sig = inspect.signature(func)
    target_args = dict()
    for param_name in sig.parameters:
        if (v := find_first(raw_args, param_name)) is not None:
            target_args[param_name] = v
    return target_args


def typesafe_call(func, kwargs):
    try:
        return func(**kwargs)
    except:
        return None
