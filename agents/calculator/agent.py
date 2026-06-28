import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from types import FunctionType
from typing import Any, Optional

from ollama import Client

from utility import parse_arguments

from .models import Arguments, FunctionCall, MathOperations, Result

logger = logging.getLogger("CalculatorAgent")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass(frozen=True)
class ParsedExpression:
    x: str
    operator: str
    y: str


class QueryVerifier:
    """LLM이 추출한 연산과 피연산자의 무결성을 검증한다."""

    OPERAND_PATTERN = r"""
        [+-]?
        (?:
            (?:\d+(?:\.\d+)?)   # 1, 1.23
            |
            (?:\.\d+)           # .5
        )
        (?:[eE][+-]?\d+)?       # optional scientific notation
    """

    COMMON_EXPRESSION = re.compile(
        rf"""
        ^\s*
        \(?
        (?P<x>{OPERAND_PATTERN})
        \)?
        \s*
        (?P<op>[+\-*/xX])
        \s*
        \(?
        (?P<y>{OPERAND_PATTERN})
        \)?
        \s*
        (?:=\s*\?)?
        \s*$
        """,
        re.VERBOSE,
    )

    OPERATOR_MAPPING = {
        "+": "add",
        "-": "subtract",
        "*": "multiply",
        "x": "multiply",
        "X": "multiply",
        "/": "divide",
    }

    @staticmethod
    def parse(query: str) -> ParsedExpression | None:
        """
        수식을 파싱한다.

        성공 시 ParsedExpression 반환
        실패 시 None 반환
        """
        match = QueryVerifier.COMMON_EXPRESSION.match(query)
        if match is None:
            return None

        return ParsedExpression(
            x=match.group("x"),
            operator=match.group("op"),
            y=match.group("y"),
        )

    @staticmethod
    def is_valid_expression(query: str) -> bool:
        """지원하는 산술식인지 여부를 반환한다."""
        return QueryVerifier.parse(query) is not None

    @staticmethod
    def _is_equivalent(val1: str, val2: str) -> bool:
        """
        숫자 표현이 달라도 같은 값이면 True.
        예)
            -1 == -1.0
            1e3 == 1000
        """
        try:
            return Decimal(val1) == Decimal(val2)
        except InvalidOperation:
            return val1.strip().lower() == val2.strip().lower()

    @staticmethod
    def verify_operand_order(
        query: str,
        op_type: str,
        x_str: str,
        y_str: str,
    ) -> bool:
        """
        LLM이 추출한 operation/x/y가 원본 수식과 일치하는지 검증한다.
        """

        parsed = QueryVerifier.parse(query)
        if parsed is None:
            return False

        expected_operation = QueryVerifier.OPERATOR_MAPPING.get(parsed.operator)
        if expected_operation != op_type:
            return False

        eq = QueryVerifier._is_equivalent

        # 덧셈/곱셈은 교환법칙 허용
        if op_type in ("add", "multiply"):
            return (eq(parsed.x, x_str) and eq(parsed.y, y_str)) or (
                eq(parsed.x, y_str) and eq(parsed.y, x_str)
            )

        # 뺄셈/나눗셈은 순서 중요
        return eq(parsed.x, x_str) and eq(parsed.y, y_str)


class CalculatorAgent:
    """교차 검증(Validator)을 통합 수행하는 계산기 에이전트"""

    @staticmethod
    def __call(func: FunctionType, args: dict[str, Any] | Arguments) -> Result:
        parsed_args = dict()
        if isinstance(args, dict):
            parsed_args = parse_arguments(func, args)
        else:
            parsed_args = {"x": args.x, "y": args.y}

        try:
            result = func(**parsed_args)
        except Exception as e:
            raise ValueError(
                f"Invalid arguments for {func.__name__}: {parsed_args}"
            ) from e

        return Result(func_name=func.__name__, args=parsed_args, value=result)

    def __init__(
        self,
        primary_model: str = "calc",
        validator_model: str = "calc-qwen",
        verbose: bool = False,
    ):
        self.primary_model = primary_model
        self.validator_model = validator_model
        self.verbose = verbose
        self._client = Client()

        # 도구 목록 로드
        self.tools_list = [
            MathOperations.add,
            MathOperations.subtract,
            MathOperations.multiply,
            MathOperations.divide,
        ]
        self.tools_map = {func.__name__: func for func in self.tools_list}

    def _verify(self, query: str, explanation: FunctionCall) -> bool:
        try:
            arguments = explanation.arguments
            x_str = str(arguments.x)
            y_str = str(arguments.y)
            op_type = explanation.operation.value
            return QueryVerifier.verify_operand_order(query, op_type, x_str, y_str)
        except Exception as e:
            if self.verbose:
                logger.error(f"무결성 검증 중 에러 발생: {e}")
            return False

    def _safe_parse_json(self, content: str) -> Optional[FunctionCall]:
        """정규식을 이용해 순수 JSON만 추출"""
        try:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                if self.verbose:
                    logger.error(f"JSON 구조를 찾을 수 없습니다: {content}")
                return None
            return FunctionCall.model_validate_json(match.group(0))
        except Exception as e:
            if self.verbose:
                logger.error(f"Pydantic 스키마 검증 실패: {e}")
            return None

    def explain(self, query: str) -> Optional[FunctionCall]:
        """쿼리의 의도를 분석하여 구조화된 설명 객체 반환"""
        try:
            response = self._client.chat(
                model=self.primary_model,
                messages=[{"role": "user", "content": query}],
                format=FunctionCall.model_json_schema(),
            )

            if content := response.message.content:
                if self.verbose:
                    print(f"\n[LLM Raw Response for: '{query}']\n{content}")
                return self._safe_parse_json(content)

        except Exception as e:
            logger.error(f"Primary 모델(calc) 요청 중 오류 발생: {e}")
        return None

    def _validate_with_tools(self, query: str) -> Optional[float]:
        """calc-qwen을 통한 엄격한 도구 호출(Tool Calling) 교차 검증"""
        context = [{"role": "user", "content": query}]

        try:
            response = self._client.chat(
                model=self.validator_model,
                messages=context,
                tools=self.tools_list,
            )

            # 도구 호출이 정상적으로 들어온 경우
            if response.message.tool_calls:
                call = response.message.tool_calls[0]
                return self.call_operation(
                    call.function.name, dict(call.function.arguments)
                )

            # 도구 호출 대신 JSON 텍스트로 응답을 준 경우의 Fallback
            elif response.message.content:
                if self.verbose:
                    print(
                        "⚠️ [Validation] Tool Calls 대신 텍스트 응답이 반환되었습니다. Fallback을 시도합니다."
                    )
                obj = self._safe_parse_json(response.message.content)
                if obj:
                    return self.call_operation(obj.operation.value, obj.arguments)

        except Exception as e:
            logger.error(f"Validator 모델(calc-qwen) 요청 중 오류 발생: {e}")

        return None

    def call_operation(self, func_name: str, args: dict | Arguments) -> Optional[float]:
        """안전하게 도구를 실행하고 결과를 반환합니다."""
        func = self.tools_map.get(func_name)
        if not func:
            if self.verbose:
                print(f"⚠️ [Validation Failed] 도구 목록에 없는 함수 호출: {func_name}")
            return None

        try:
            result = CalculatorAgent.__call(func, args)
            if self.verbose:
                print(f"[Execute Tool] {func_name}({args}) = {result.value}")
            return result.value
        except Exception as e:
            if self.verbose:
                logger.error(f"도구 실행 중 에러 발생: {e}")
            return None

    def __need_escalation(self, query: str, explanation: FunctionCall) -> bool:
        """에스컬레이션 여부를 종합 판단합니다."""

        if not QueryVerifier.is_valid_expression(query):
            return True

        # 추출 상태 및 순서 무결성 검증
        if not self._verify(query, explanation):
            if self.verbose:
                print("⚠️ [Escalation] 부정확한 응답 감지")
            return True

        # 모델이 스스로 규칙 외의 것으로 판별했는지 확인
        if explanation.review.has_natural_language:
            if self.verbose:
                print("⚠️ [Escalation] 모델 자체 위임 요청")
            return True

        return False

    def calculate(self, query: str) -> Optional[float]:
        # 1. 1차 필터 모델(calc)에게 규격 검증 요청
        explanation = self.explain(query)
        if not explanation:
            return self._validate_with_tools(query)

        # 2. 깐깐한 조건 통과 여부 검사
        if self.__need_escalation(query, explanation):
            if self.verbose:
                print(
                    f"🔄 [Redirect] '{query}' 처리를 위해 고급 모델(calc-qwen)을 호출합니다."
                )
            return self._validate_with_tools(query)

        # 3. 완벽히 규칙에 부합하는 식은 직행 (Fast Path)
        if self.verbose:
            print(f"🚀 [Fast Path] '{query}' 규격 완벽 일치. 즉시 계산합니다.")
        return self.call_operation(explanation.operation.value, explanation.arguments)
