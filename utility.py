import inspect
import re
from typing import Any, Callable


def parse_numbers(message: str) -> list[float]:
    numbers = re.findall(r"[+-]?(?:\d*\.\d+|\d+)", message)
    print(numbers)

    return list(map(float, numbers))


def find_first(d: dict[str, Any], target_key: str) -> Any:
    if target_key in d:
        return d[target_key]
    return next(
        (find_first(v, target_key) for v in d.values() if isinstance(v, dict)),
        None,
    )


def parse_arguments(
    func: Callable, raw_args: dict[str, Any]
) -> dict[str, Any]:
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
    except ValueError:
        return None
