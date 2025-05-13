"""
Calculator widgets: buttons, display, input handling.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel, QSizePolicy, QHBoxLayout, QButtonGroup, QRadioButton, QListWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.normal_calculator import NormalCalculator
from core.scientific_calculator import ScientificCalculator
import math

class CalculatorWidget(QWidget):
    expression_evaluated = pyqtSignal(str, str)  # Signal for history (expression, result)
    
    def __init__(self, mode_name):
        super().__init__()
        self.mode_name = mode_name
        self.angle_mode = 'DEG'  # Default for scientific
        self.init_calculator()
        self.init_ui()

    def init_calculator(self):
        if self.mode_name == "Normal":
            self.calculator = NormalCalculator()
            self.buttons = [
                ['7', '8', '9', '/'],
                ['4', '5', '6', '*'],
                ['1', '2', '3', '-'],
                ['0', '.', '=', '+'],
                ['C']
            ]
        elif self.mode_name == "Scientific":
            self.calculator = ScientificCalculator()
            self.buttons = [
                ['Rad', 'Deg', 'x!', '(', ')', '%', 'AC'],
                ['Inv', 'sin', 'ln', '7', '8', '9', '/'],
                ['π', 'cos', 'log', '4', '5', '6', '*'],
                ['e', 'tan', '√', '1', '2', '3', '-'],
                ['Ans', 'EXP', 'x^', '0', '.', '=', '+']
            ]
        else:
            self.calculator = None
            self.buttons = []

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Display setup
        self.display = QLineEdit()
        self.display.setReadOnly(False)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(60)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                background: #222;
                color: #fff;
                border-radius: 8px;
                padding: 8px 15px;
                margin: 5px;
                border: 1px solid #444;
            }
        """)
        self.display.setCursorPosition(len(self.display.text()))
        layout.addWidget(self.display)

        # Grid for buttons with fixed spacing
        self.grid = QGridLayout()
        self.grid.setSpacing(10)  # Fixed spacing between buttons
        self.grid.setContentsMargins(10, 10, 10, 10)
        
        self.button_group = QButtonGroup(self)
        self.angle_buttons = {}
        
        # Create buttons
        for row, row_buttons in enumerate(self.buttons):
            for col, btn_text in enumerate(row_buttons):
                btn = QPushButton(btn_text)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setFocusPolicy(Qt.NoFocus)  # Prevent focus rectangle
                
                if btn_text in {"Rad", "Deg"}:
                    self.angle_buttons[btn_text] = btn
                    btn.clicked.connect(lambda _, t=btn_text: self.set_angle_mode_button(t))
                    btn.setStyleSheet(self.button_style(btn_text, selected=(self.angle_mode==btn_text.upper())))
                else:
                    btn.clicked.connect(lambda _, text=btn_text: self.on_button_click(text))
                    btn.setStyleSheet(self.button_style(btn_text))
                
                # Add pressed/released effects
                btn.pressed.connect(lambda b=btn: b.setStyleSheet(self.button_style(b.text(), pressed=True, selected=(self.angle_mode==b.text().upper()))))
                btn.released.connect(lambda b=btn: b.setStyleSheet(self.button_style(b.text(), selected=(self.angle_mode==b.text().upper()))))
                
                self.button_group.addButton(btn)
                self.grid.addWidget(btn, row, col)

        layout.addLayout(self.grid)
        
        # Set widget properties
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #181818;
                border: 1px solid #333;
                border-radius: 10px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def button_style(self, text, selected=False, pressed=False, font_size=18):
        # Base style with dynamic font size
        base = f"border-radius: 8px; font-size: {font_size}px;"
        if text in {'+', '-', '*', '/', '=', '%', 'x^', '√', 'EXP'}:
            if pressed:
                return f"background: #cc7a00; color: #fff; font-weight: bold; {base}"
            return f"background: #ff9500; color: #fff; font-weight: bold; {base}"
        elif text in {'sin', 'cos', 'tan', 'ln', 'log', 'π', 'e', 'x!', '(', ')', 'Inv', 'Ans'}:
            if pressed:
                return f"background: #222; color: #ff9500; {base}"
            return f"background: #333; color: #ff9500; {base}"
        elif text in {'AC', 'C'}:
            if pressed:
                return f"background: #a22; color: #fff; {base}"
            return f"background: #444; color: #ff3b30; {base}"
        elif text in {'Rad', 'Deg'}:
            if selected:
                if pressed:
                    return f"background: #cc7a00; color: #fff; font-weight: bold; {base}"
                return f"background: #ff9500; color: #fff; font-weight: bold; {base}"
            else:
                if pressed:
                    return f"background: #222; color: #ff9500; {base}"
                return f"background: #333; color: #ff9500; {base}"
        else:
            if pressed:
                return f"background: #111; color: #fff; {base}"
            return f"background: #222; color: #fff; {base}"

    def set_angle_mode_button(self, mode):
        self.angle_mode = mode.upper()
        self.update_angle_mode_buttons()

    def update_angle_mode_buttons(self):
        for mode, btn in self.angle_buttons.items():
            btn.setStyleSheet(self.button_style(mode, selected=(self.angle_mode==mode.upper())))

    def on_button_click(self, text):
        if text in {'C', 'AC'}:
            self.display.clear()
        elif text == '=':
            expr = self.display.text()
            try:
                expr = expr.replace('x^', '**').replace('√', 'sqrt').replace('π', str(math.pi)).replace('e', str(math.e))
                if self.mode_name == "Scientific":
                    result = self.eval_scientific(expr)
                else:
                    result = self.calculator.calculate(expr)
                self.display.setText(str(result))
                # Emit signal for history
                self.expression_evaluated.emit(expr, str(result))
            except Exception:
                self.display.setText("Error")
        elif text == 'x!':
            try:
                val = float(self.display.text())
                self.display.setText(str(math.factorial(int(val))))
            except Exception:
                self.display.setText("Error")
        elif text in {'sin', 'cos', 'tan'}:
            self.display.setText(self.display.text() + f"{text}(")
        elif text in {'ln', 'log', 'sqrt'}:
            self.display.setText(self.display.text() + f"{text}(")
        elif text == 'π':
            self.display.setText(self.display.text() + str(math.pi))
        elif text == 'e':
            self.display.setText(self.display.text() + str(math.e))
        elif text == 'Ans':
            pass  # Placeholder for answer memory
        elif text == 'Inv':
            pass  # Placeholder for inverse functions
        elif text in {'Rad', 'Deg'}:
            pass  # Handled by button click
        else:
            self.display.setText(self.display.text() + text)

    def eval_scientific(self, expr):
        # Add support for deg/rad for trig functions
        allowed = {
            'sin': lambda x: math.sin(math.radians(x)) if self.angle_mode == 'DEG' else math.sin(x),
            'cos': lambda x: math.cos(math.radians(x)) if self.angle_mode == 'DEG' else math.cos(x),
            'tan': lambda x: math.tan(math.radians(x)) if self.angle_mode == 'DEG' else math.tan(x),
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'pi': math.pi,
            'e': math.e,
            '__builtins__': None
        }
        return eval(expr, allowed)

    def keyPressEvent(self, event):
        key = event.key()
        key_map = {
            Qt.Key_0: '0', Qt.Key_1: '1', Qt.Key_2: '2', Qt.Key_3: '3', Qt.Key_4: '4',
            Qt.Key_5: '5', Qt.Key_6: '6', Qt.Key_7: '7', Qt.Key_8: '8', Qt.Key_9: '9',
            Qt.Key_Plus: '+', Qt.Key_Minus: '-', Qt.Key_Asterisk: '*', Qt.Key_Slash: '/',
            Qt.Key_ParenLeft: '(', Qt.Key_ParenRight: ')', Qt.Key_Period: '.',
            Qt.Key_Equal: '=', Qt.Key_Enter: '=', Qt.Key_Return: '=', Qt.Key_Backspace: 'C'
        }
        if key in key_map:
            self.on_button_click(key_map[key])
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update display font size
        w, h = self.width(), self.height()
        display_font_size = min(max(24, h // 15), 36)
        self.display.setStyleSheet(f"""
            QLineEdit {{
                font-size: {display_font_size}px;
                background: #222;
                color: #fff;
                border-radius: 8px;
                padding: 8px 15px;
                margin: 5px;
                border: 1px solid #444;
            }}
        """)

        # Calculate button dimensions based on available space
        if self.button_group:
            # Get grid dimensions
            cols = max(len(row) for row in self.buttons) if self.buttons else 1
            rows = len(self.buttons) if self.buttons else 1
            
            # Calculate available space (subtracting margins and spacing)
            spacing = self.grid.spacing()
            margins = self.grid.contentsMargins()
            available_w = w - margins.left() - margins.right() - (spacing * (cols - 1))
            available_h = h - self.display.height() - margins.top() - margins.bottom() - (spacing * (rows - 1))
            
            # Calculate button dimensions
            btn_w = available_w // cols
            btn_h = available_h // rows
            
            # Apply size to buttons
            for btn in self.button_group.buttons():
                btn.setFixedSize(btn_w, btn_h)
                # Update font size based on button size (keeping text readable)
                font_size = min(btn_h // 3, btn_w // 4)
                font_size = max(8, min(font_size, 24))  # Allow smaller font size but cap the maximum
                btn.setStyleSheet(self.button_style(btn.text(), 
                                                  selected=(self.angle_mode==btn.text().upper()),
                                                  font_size=font_size))

class GraphicCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Graphing calculator coming soon!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: #888;")
        layout.addWidget(label)
        self.setLayout(layout)

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Clear button in header
        header = QHBoxLayout()
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.setMinimumWidth(70)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                color: #ff3b30;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background: #444;
            }
            QPushButton:pressed {
                background: #222;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_history)
        header.addStretch()
        header.addWidget(self.clear_btn)
        layout.addLayout(header)
        
        # History list with improved styling
        self.history_list = QListWidget()
        self.update_list_style()
        layout.addWidget(self.history_list)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            background: #181818;
            border-left: 1px solid #333;
        """)
        self.setMinimumWidth(200)

    def update_list_style(self):
        width = self.width() if self.width() > 0 else 200
        # Dynamic font size calculation
        font_size = min(14, max(11, width // 20))
        # Dynamic padding calculation
        h_padding = min(12, max(8, width // 25))
        v_padding = min(10, max(6, width // 30))
        
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background: #222;
                border: 1px solid #444;
                border-radius: 4px;
                color: white;
                font-size: {font_size}px;
            }}
            QListWidget::item {{
                padding: {v_padding}px {h_padding}px;
                border-bottom: 1px solid #333;
            }}
            QListWidget::item:hover {{
                background: #333;
            }}
            QListWidget:item:selected {{
                background: #444;
                color: #ff9500;
            }}
            QScrollBar:vertical {{
                background: #222;
                width: {max(10, min(14, width // 25))}px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #444;
                min-height: 20px;
                border-radius: {max(3, min(6, width // 50))}px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #555;
            }}
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {{
                background: #222;
            }}
        """)

    def add_entry(self, expression, result):
        entry = f"{expression} = {result}"
        self.history_list.addItem(entry)
        self.history_list.scrollToBottom()
    
    def clear_history(self):
        self.history_list.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_list_style()
        
    def showEvent(self, event):
        super().showEvent(event)
        self.update_list_style()
