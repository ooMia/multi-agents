import json
import math
from types import FunctionType
from typing import Any, Optional

from ollama import ChatResponse, Client
from pydantic import BaseModel, Field

from utility import parse_arguments


class Result(BaseModel):
    value: Optional[float] = Field(
        default=None,
        description="최종 계산된 도구 호출 결과값. 계산할 수 없는 경우 None입니다.",
    )


class Calculator:
    """계산기 에이전트 클래스"""

    @staticmethod
    def __log_calculate(func_name: str, x: str, y: str, result: float | None):
        return f"{func_name}({x},{y})={result}"

    def __init__(self):
        self.model = "calc"
        self.tools_list: list[FunctionType] = [
            self.Operation.add,
            self.Operation.subtract,
            self.Operation.multiply,
            self.Operation.divide,
        ]
        self.tools_map = {func.__name__: func for func in self.tools_list}
        self.__log = {}
        self.__context = []
        self.__client = Client()

    def __chat(
        self, format_schema: Optional[type[BaseModel]] = None
    ) -> ChatResponse:
        return self.__client.chat(
            model=self.model,
            messages=self.__context,
            format=(
                format_schema.model_json_schema() if format_schema else None
            ),
            tools=self.tools_list,
        )

    def __tool_calls(self) -> list[dict[str, str]]:
        response = self.__chat()
        contexts = []
        if calls := response.message.tool_calls:
            for call in calls:
                func_name = call.function.name
                args = dict(call.function.arguments)
                if func := self.tools_map.get(func_name):
                    result = self.Operation.call(func, args)
                    contexts.append(
                        {
                            "role": "tool",
                            "content": Result(value=result).model_dump_json(),
                            "name": func_name,
                        }
                    )
                    self.__log["result"] = self.__log_calculate(
                        func_name, args["x"], args["y"], result
                    )
        return contexts

    def calculate(self, query: str) -> Optional[float]:
        self.__context.append({"role": "user", "content": f"{query}"})
        self.__log["query"] = query
        contexts = self.__tool_calls()
        print(self.__log)

        try:
            if result_json := contexts[0].get("content"):
                value = json.loads(result_json).get("value")
                return float(value)
        except TypeError:
            return None

    class Operation:

        @staticmethod
        def __typesafe_call(
            func: FunctionType, kwargs: dict
        ) -> Optional[float]:
            try:
                return func(**kwargs)
            except ValueError:
                raise Exception(f"Invalid arguments: {func} {kwargs}")

        @staticmethod
        def call(func: FunctionType, args: dict[str, Any]):
            args = parse_arguments(func, args)
            return Calculator.Operation.__typesafe_call(func, args)

        @staticmethod
        def add(
            x: float | str,
            y: float | str,
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

        @staticmethod
        def subtract(
            x: float | str,
            y: float | str,
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

        @staticmethod
        def multiply(
            x: float | str,
            y: float | str,
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

        @staticmethod
        def divide(
            x: float | str,
            y: float | str,
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
