"""
Scientific calculator: advanced operations (sin, cos, power, root, etc).
"""
import math
from .base_calculator import CalculatorMode

class ScientificCalculator(CalculatorMode):
    def calculate(self, expression: str) -> float:
        # Allow math functions in eval
        allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        try:
            return eval(expression, {"__builtins__": None}, allowed_names)
        except Exception:
            raise ValueError("Invalid scientific expression")
