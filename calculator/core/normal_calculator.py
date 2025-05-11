"""
Normal calculator: basic operations (add, subtract, multiply, divide).
"""
from .base_calculator import CalculatorMode

class NormalCalculator(CalculatorMode):
    def calculate(self, expression: str) -> float:
        # Basic eval for demo; production code should use a safe parser
        try:
            return eval(expression, {"__builtins__": None}, {})
        except Exception:
            raise ValueError("Invalid expression")
