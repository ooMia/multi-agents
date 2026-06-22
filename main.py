from model import Calculator

global calculator
calculator = None
if calculator is None:
    calculator = Calculator()
calculate = calculator.calculate

if __name__ == "__main__":
    calculate("32가 여덟 번 반복되면?")
