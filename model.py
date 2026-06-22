import json
import math
from typing import Optional

from ollama import ChatResponse, Client
from pydantic import BaseModel, Field
from utility import log_calculate, parse_arguments, typesafe_call


class Result(BaseModel):
    value: Optional[float] = Field(
        default=None,
        description="최종 계산된 도구 호출 결과값. 계산할 수 없는 경우 None입니다.",
    )


class Calculator:
    """계산기 에이전트 클래스"""

    def __init__(self):
        self.model = "calc"
        self.tools_list = [self.add, self.subtract, self.multiply, self.divide]
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
                if func := self.tools_map.get(func_name):
                    args = parse_arguments(func, dict(call.function.arguments))
                    result = typesafe_call(func, args)
                    self.__log["result"] = log_calculate(
                        func_name, args["x"], args["y"], result
                    )
                    contexts.append(
                        {
                            "role": "tool",
                            "content": Result(value=result).model_dump_json(),
                            "name": func_name,
                        }
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
            return None
