import ollama
from pydantic import BaseModel, Field
from typing import Optional, Callable, Any
from tools.math import add, subtract, multiply, divide


class Result(BaseModel):
    value: Optional[float] = Field(default=None, description="도구 호출 결과값")


# --- 🛡️ 3. 방어적 인자 파서 (Resilience) ---
def parse_and_execute(func: Callable, raw_args: dict[str, Any]) -> Optional[float]:
    """Ollama의 중첩/변형된 인자를 파싱하여 안전하게 함수를 실행합니다."""
    args = []
    for v in raw_args.values():
        if v and (isinstance(v, str) or isinstance(v, float)):
            args.append(float(v))
    result = func(*args) if args else None
    print(f"{func.__name__}({raw_args}) = {result}")
    return result


def parse_numbers(message: str) -> list[str]:
    import re

    numbers = re.findall(r"[+-]?(?:\d*\.\d+|\d+)", message)
    print(numbers)
    return numbers


def chat_with_tools(message: str) -> Result:
    client = ollama.Client()
    available_tools = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    }
    SYSTEM_PROMPT = """
RULES
- 'INF' is an infinite state of a number.
- Expressions with 'inf', ALWAYS returns None.
- ALWAYS use the best tool which mets user's requirements.
- NEVER compute answers yourself.
- NEVER round or rewrite numbers.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"normal numbers: {parse_numbers(message)}"},
        {"role": "user", "content": f"original query: {message}"},
    ]

    # [Step 1] 도구 호출 (format 생략)
    response = client.chat(
        model="llama3.2",
        messages=messages,
        tools=[*available_tools.values()],
    )

    # [Step 2] 방어적 인자 파싱 및 실행
    if response.message.tool_calls:
        messages.append(response.message)
        for call in response.message.tool_calls:
            func = available_tools.get(call.function.name)
            if func:
                res = parse_and_execute(func, call.function.arguments)
                print(res)
                messages.append(
                    {
                        "role": "tool",
                        "content": Result(value=res).model_dump_json(),
                        "tool_name": call.function.name,
                    }
                )

    # [Step 3] 최종 결과 생성 (Ollama Native JSON Schema 강제)
    final_response = client.chat(
        model="llama3.2",
        messages=messages,
        format=Result.model_json_schema(),
        tools=[*available_tools.values()],
    )

    # Pydantic v2 기본 기능으로 즉시 객체화 반환
    return Result.model_validate_json(final_response.message.content)


def execute_math(expression: str) -> Optional[float]:
    result_obj = chat_with_tools(expression)
    return result_obj.value


if __name__ == "__main__":
    # print(f"✅ Final Value: {execute_math('15 더하기 27은?')}")
    # print(f"✅ Final Value: {execute_math('100을 4로 나누면?')}")
    print(f"✅ Final Value: {execute_math(f'4를 절반으로 나누면?')}")
    print(f"✅ Final Value: {execute_math(f'4를 절반은?')}")
    print(f"✅ Final Value: {execute_math(f'-2의 두 배는?')}")
    print(f"✅ Final Value: {execute_math(f'양의 무한대를 절반으로 나누면?')}")
    print(f"✅ Final Value: {execute_math(f'무한대에 0을 더하면 어떻게 돼?')}")
    print(f"✅ Final Value: {execute_math(f'{float("-inf")} 더하기 0은?')}")
    print(f"✅ Final Value: {execute_math(f'무한대 더하기 0은?')}")
