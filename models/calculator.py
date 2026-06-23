import math
import operator
from types import FunctionType
from typing import Any, Callable, Optional

from ollama import ChatResponse, Client
from pydantic import BaseModel, Field

from utility import parse_arguments


class Result(BaseModel):
    func_name: str = Field(
        default="",
        description="호출 대상 함수 이름.",
    )
    args: dict[str, Any] = Field(
        default_factory=dict,
        description="함수에 전달된 인자.",
    )
    value: Optional[float] = Field(
        default=None,
        description="최종 계산된 도구 호출 결과값. 계산할 수 없는 경우 None입니다.",
    )


class Calculator:
    """계산기 에이전트 클래스"""

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
        self._context: list[dict[str, str]] = []
        self._client = Client()

    @staticmethod
    def _format_log(query: str, result: Result) -> str:
        args_str = ", ".join(f"{v}" for v in result.args.values())
        return f"[LOG] Query: '{query}' -> {result.func_name}({args_str}) = {result.value}"

    def _chat(
        self, format_schema: Optional[type[BaseModel]] = None
    ) -> ChatResponse:
        return self._client.chat(
            model=self.model,
            messages=self._context,
            format=(
                format_schema.model_json_schema() if format_schema else None
            ),
            tools=self.tools_list,
        )

    def _execute_tool_calls(self) -> Optional[Result]:
        response = self._chat()

        if not response.message.tool_calls:
            return None

        call = response.message.tool_calls[0]
        func_name = call.function.name
        args = dict(call.function.arguments)

        func = self.tools_map.get(func_name)
        if not func:
            return None

        return Operation.call(func, args)

    def calculate(self, query: str) -> Optional[float]:
        self._context.append({"role": "user", "content": query})

        result = self._execute_tool_calls()
        if not result:
            return None

        if self.verbose:
            print(self._format_log(query, result))

        return result.value


class Operation:
    @staticmethod
    def _safe_execute(
        x: Any, y: Any, op: Callable[[float, float], float]
    ) -> Optional[float]:
        """Helper to safely convert inputs to float and execute math operations."""
        try:
            fx, fy = float(x), float(y)
            if math.isinf(fx) or math.isinf(fy):
                return None

            res = op(fx, fy)
            return res if math.isfinite(res) else None
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def call(func: FunctionType, args: dict[str, Any]) -> Result:
        parsed_args = parse_arguments(func, args)
        try:
            result = func(**parsed_args)
        except Exception as e:
            raise ValueError(
                f"Invalid arguments for {func.__name__}: {parsed_args}"
            ) from e

        return Result(func_name=func.__name__, args=parsed_args, value=result)

    @staticmethod
    def add(x: float | str, y: float | str) -> Optional[float]:
        """Adds x and y together (x + y).

        Use this tool whenever the operation between the numbers is addition (+).
        This includes cases where numbers themselves are negative (e.g. `-A + -B`).
        DO NOT use this tool for subtraction queries (e.g. `-A - -B`).
        """

        return Operation._safe_execute(x, y, operator.add)

    @staticmethod
    def subtract(x: float | str, y: float | str) -> Optional[float]:
        """Subtracts y from x (x - y).

        Use this tool ONLY when the operation between the numbers is subtraction (-).
        DO NOT use this tool for addition queries just because a number starts with a minus sign (e.g. `-A + B`).
        """

        return Operation._safe_execute(x, y, operator.sub)

    @staticmethod
    def multiply(x: float | str, y: float | str) -> Optional[float]:
        """Multiplies two numbers (x * y)."""
        return Operation._safe_execute(x, y, operator.mul)

    @staticmethod
    def divide(x: float | str, y: float | str) -> Optional[float]:
        """
        'x' is a dividend and 'y' is a divisor.
        Divides the dividend by the divisor (dividend / divisor).
        - dividend: The number to be divided.
        - divisor: The number to divide by.
        Returns None if divisor is 0.
        """
        return Operation._safe_execute(x, y, operator.truediv)
