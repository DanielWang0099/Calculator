"""
Abstract base classes for calculator modes.
"""
from abc import ABC, abstractmethod

class CalculatorMode(ABC):
    @abstractmethod
    def calculate(self, expression: str) -> float:
        """Evaluate the given expression and return the result."""
        pass
