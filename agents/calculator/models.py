import math
import operator
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class Arguments(BaseModel):
    x: float | str
    y: float | str


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


class Review(BaseModel):
    has_natural_language: bool = Field(
        description="쿼리에 자연어(예: '절반', '배')가 포함되어 있다면 True로 설정합니다."
    )


class FunctionCall(BaseModel):
    operation: OperationType = Field(description="가장 잘 매칭되는 연산 종류.")
    review: Review = Field(
        description="arguments 추출 전, 이 쿼리가 단순 규칙에 부합하는지 검증하는 블록."
    )
    arguments: Arguments = Field(
        description="표준 기호에서 추출한 피연산자 x와 y. 만약 규칙에 없는 모호한 쿼리라면 빈 객체{}로 비워두어도 좋습니다."
    )


class MathOperations:
    @staticmethod
    def _safe_execute(
        x: Any, y: Any, op: Callable[[float, float], float]
    ) -> Optional[float]:
        """안전하게 입력을 float로 변환하고 수학 연산을 수행하는 헬퍼 함수"""
        try:
            fx, fy = float(x), float(y)
            if math.isinf(fx) or math.isinf(fy):
                return None

            res = op(fx, fy)
            return res if math.isfinite(res) else None
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def add(x: float | str, y: float | str) -> Optional[float]:
        """Adds x and y together (x + y).

        Use this tool whenever the operation between the numbers is addition (+).
        This includes cases where numbers themselves are negative (e.g. `-A + -B`).
        DO NOT use this tool for subtraction queries (e.g. `-A - B`).
        """
        return MathOperations._safe_execute(x, y, operator.add)

    @staticmethod
    def subtract(x: float | str, y: float | str) -> Optional[float]:
        """Subtracts y from x (x - y).

        Use this tool ONLY when the operation between the numbers is subtraction (-).
        DO NOT use this tool for addition queries just because a number starts with a minus sign (e.g. `-A + B`).
        """
        return MathOperations._safe_execute(x, y, operator.sub)

    @staticmethod
    def multiply(x: float | str, y: float | str) -> Optional[float]:
        """Multiplies two numbers (x * y)."""
        return MathOperations._safe_execute(x, y, operator.mul)

    @staticmethod
    def divide(x: float | str, y: float | str) -> Optional[float]:
        """
        'x' is a dividend and 'y' is a divisor.
        Divides the dividend by the divisor (dividend / divisor).
        - dividend: The number to be divided.
        - divisor: The number to divide by.
        Returns None if divisor is 0.
        """
        return MathOperations._safe_execute(x, y, operator.truediv)
