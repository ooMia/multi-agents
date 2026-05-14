from typing import Optional
from pydantic import BaseModel, Field
from ollama import Client, ChatResponse
from utility import (
    parse_arguments,
    add,
    subtract,
    multiply,
    divide,
    typesafe_call,
)


class Result(BaseModel):
    value: Optional[float] = Field(
        default=None,
        description="최종 계산된 도구 호출 결과값. 계산할 수 없는 경우 None입니다.",
    )


class Calculator:
    """계산기 에이전트 클래스"""

    def __init_llama(self):
        self.model = "llama3.2"

    def __init_qwen(self):
        self.model = "qwen3.5:0.8b"

    def __init__(self, think=False):
        self.__think = think
        if think:
            self.__init_qwen()
        else:
            self.__init_llama()

        self.__SYSTEM_PROMPT = """
CRITICAL RULES:
- ALWAYS call tools with arguments 'x' and 'y'.
- PRESERVE the exact data type and precision. If a number has decimals (e.g., '5.2'), NEVER drop them.
- NEVER invent or substitute numbers. Only use digits present in the query, unless translating natural language math terms listed below.

CRITICAL RULES FOR INFINITY:
- The following tokens represent positive infinity (+infinity): 'inf', '∞', '무한대', '無限大'.
    -> If any of these appear, you MUST pass 'INF' as the argument value.
- The following tokens represent negative infinity (-infinity): '-inf', '-∞', '마이너스 무한대'.
    -> If any of these appear, you MUST pass '-INF' as the argument value.
- NEVER drop, ignore, or strip unicode symbols like '∞'. They are critical mathematical tokens.
- Example: "∞ 더하기 -8는?" -> The query starts with '∞'. Do NOT drop it. Call tool with {'x': 'INF', 'y': '-8'}.
- NEVER substitute infinity tokens with random normal numbers or 0. You must explicitly use 'INF' or '-INF'.

CRITICAL MAPPING & OPERATOR RULES:
- For division ("A / B"), ALWAYS set x='A' and y='B'. Formula: x / y = A / B.
- For addition ("A + B"), call 'add' with x='A', y='B'.
- For subtraction ("A - B"), ALWAYS set x='A' and y='B'. Formula: x - y = A - B.
- For multiplication ("A * B"), call 'multiply' with x='A', y='B'.

NATURAL LANGUAGE PARSING RULES:
- English "Half of X" -> Call 'divide' with x='X', y='2' (e.g., "half of 5.2" -> x='5.2', y='2')
- English "Divide X in half" -> Call 'divide' with x='X', y='2'
- Korean "X의 절반" -> Call 'divide' with x='X', y='2'
- Korean "X를 반으로" -> Call 'divide' with x='X', y='2'
- Korean "X의 반" -> Call 'divide' with x='X', y='2'

- English "Twice of X" -> Call 'multiply' with x='X', y='2' (e.g., "twice of -2.125" -> x='-2.125', y='2')
- Korean "X의 두 배" -> Call 'multiply' with x='X', y='2'

- English "A quarter of X" -> Call 'divide' with x='X', y='4'
- Korean "X의 4분의 1" -> Call 'divide' with x='X', y='4'
"""

        self.tools_list = [add, subtract, multiply, divide]
        self.tools_map = {func.__name__: func for func in self.tools_list}

        self.__context = [{"role": "system", "content": self.__SYSTEM_PROMPT}]
        self.__client = Client()

    def __chat(self, format_schema: Optional[type[BaseModel]] = None) -> ChatResponse:
        return self.__client.chat(
            model=self.model,
            messages=self.__context,
            format=format_schema.model_json_schema() if format_schema else None,
            think=self.__think,
            tools=self.tools_list,
        )

    def __tool_calls(self) -> list[dict[str, str]]:
        response = self.__chat()
        contexts = []
        if calls := response.message.tool_calls:
            for call in calls:
                func_name = call.function.name
                if func := self.tools_map.get(func_name):
                    print(call.function.arguments)
                    args = parse_arguments(func, dict(call.function.arguments))
                    result = typesafe_call(func, args)
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
        contexts = self.__tool_calls()

        for msg in contexts:
            self.__context.append(dict(msg))
        import json

        try:
            if result_json := contexts[0].get("content"):
                value = json.loads(result_json).get("value")
                return float(value)
        except:
            return None


def execute_math(expression: str) -> Optional[float]:
    return Calculator(think=False).calculate(expression)
