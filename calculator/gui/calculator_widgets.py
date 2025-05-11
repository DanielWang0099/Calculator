"""
Calculator widgets: buttons, display, input handling.
"""
from PyQt5.QtWidgets import QWidget

class CalculatorWidget(QWidget):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode  # CalculatorMode instance
        # TODO: Add buttons, display, and input handling
