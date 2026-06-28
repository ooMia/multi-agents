from agents.calculator.agent import CalculatorAgent

if __name__ == "__main__":

    def explain(query: str, verbose: bool = True):
        return CalculatorAgent(verbose=verbose).explain(query)

    def calculate(query: str, verbose: bool = True):
        return CalculatorAgent(verbose=verbose).calculate(query)

    test_queries = [
        "0.0 + 0.0 = ?",
        "-2.6095614418943385e-139 - -1.7976931348623157e+308 = ?",
        "-99999999 / 1e-06 = ?",
        "-1 - -1 = ?",
        "-1 + 1 = ?",
        "1 - -1 = ?",
    ]

    for q in test_queries:
        print(f"\n{'=' * 50}\nQuery: {q}")
        res = calculate(q)
        print(f"Result: {res}")
