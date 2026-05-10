from ollama import ChatResponse
from pydantic import BaseModel


class Result(BaseModel):
    value: int


def chat(message: str):
    from ollama import chat

    response = chat(
        model="llama3.2",
        messages=[{"role": "user", "content": message}],
        format=Result.model_json_schema(),
    )

    def _post_processing(response: ChatResponse) -> Result:
        from typing import cast

        content = cast(str, response.message.content)
        return Result.model_validate_json(content)

    return _post_processing(response)


def plus(x: float, y: float):
    return chat(f"{x} + {y} = ?")


if __name__ == "__main__":
    result = plus(1, 1)
    print(result.value)
