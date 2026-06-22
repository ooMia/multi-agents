import math
from types import FunctionType
from typing import Any, Optional

from ollama import ChatResponse, Client
from pydantic import BaseModel, Field

from utility import parse_arguments


class Result(BaseModel):
    func_name: str = Field(
        default="",
        description="호출 대상 함수 이름.",
    )
    args: dict[str, Any] = Field(
        default={},
        description="함수에 전달된 인자.",
    )
    value: Optional[float] = Field(
        default=None,
        description="최종 계산된 도구 호출 결과값. 계산할 수 없는 경우 None입니다.",
    )


class Calculator:
    """계산기 에이전트 클래스"""

    @staticmethod
    def __log_calculate(result: Result):
        return f"{result.func_name}({result.args["x"]},{result.args["y"]})={result.value}"

    def __init__(self, verbose: bool = False):
        self.model = "calc"
        self.tools_list: list[FunctionType] = [
            Operation.add,
            Operation.subtract,
            Operation.multiply,
            Operation.divide,
        ]
        self.tools_map = {func.__name__: func for func in self.tools_list}
        self.verbose = verbose
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

    def __tool_calls(self) -> Optional[Result]:
        response = self.__chat()
        if calls := response.message.tool_calls:
            call = calls[0]
            func_name = call.function.name
            args = dict(call.function.arguments)
            if func := self.tools_map.get(func_name):
                result = Operation.call(func, args)
                self.__log["result"] = self.__log_calculate(result)
                return result

    def calculate(self, query: str) -> Optional[float]:
        self.__context.append({"role": "user", "content": f"{query}"})
        self.__log["query"] = query

        if result := self.__tool_calls():
            if self.verbose:
                print(self.__log)
            return result.value


class Operation:
    @staticmethod
    def __typesafe_call(func: FunctionType, kwargs: dict) -> Optional[float]:
        try:
            return func(**kwargs)
        except ValueError:
            raise Exception(f"Invalid arguments: {func} {kwargs}")

    @staticmethod
    def call(func: FunctionType, args: dict[str, Any]) -> Result:
        args = parse_arguments(func, args)
        result = Operation.__typesafe_call(func, args)
        return Result(func_name=func.__name__, args=args, value=result)

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
