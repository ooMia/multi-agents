from model import Calculator


def calculate(query: str):
    return Calculator().calculate(query)


if __name__ == "__main__":
    answer = calculate("2.5의 절반은?")
    print(answer)
