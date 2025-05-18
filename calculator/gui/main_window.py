"""
Main application window and mode switching.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QComboBox, QLabel, 
    QStackedWidget, QHBoxLayout, QPushButton, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from .calculator_widgets import CalculatorWidget, GraphicCalculatorWidget, HistoryWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Calculator")
        self.setMinimumSize(400, 500)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Left side (Calculator)
        self.calculator_widget = QWidget()
        self.calculator_layout = QVBoxLayout(self.calculator_widget)
        self.calculator_layout.setSpacing(10)
        self.calculator_layout.setContentsMargins(10, 10, 10, 10)

        # Mode selector and history button
        selector_layout = QHBoxLayout()
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Normal", "Scientific", "Graphic"])
        self.mode_selector.setFixedHeight(32)
        self.mode_selector.setMinimumWidth(120)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                background: #333;
                color: white;
                padding: 5px 10px;
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid none;
                border-right: 5px solid none;
                border-top: 5px solid #ff9500;
                width: 0;
                height: 0;
                margin-right: 5px;
            }
            QComboBox:hover {
                background: #444;
            }
        """)
        
        # History toggle button with consistent size
        self.history_btn = QPushButton("History")
        self.history_btn.setCheckable(True)
        self.history_btn.setFixedSize(80, 32)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                color: white;
                padding: 5px 10px;
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:checked {
                background: #ff9500;
                color: white;
            }
            QPushButton:hover {
                background: #444;
            }
            QPushButton:checked:hover {
                background: #ff8000;
            }
        """)
        self.history_btn.clicked.connect(self.toggle_history)
        
        selector_layout.addWidget(self.mode_selector)
        selector_layout.addStretch()
        selector_layout.addWidget(self.history_btn)
        selector_layout.setSpacing(10)
        self.calculator_layout.addLayout(selector_layout)

        # Calculator stack
        self.stack = QStackedWidget()
        self.normal_widget = CalculatorWidget("Normal")
        self.scientific_widget = CalculatorWidget("Scientific")
        self.graphic_widget = GraphicCalculatorWidget()
        
        self.stack.addWidget(self.normal_widget)
        self.stack.addWidget(self.scientific_widget)
        self.stack.addWidget(self.graphic_widget)
        self.calculator_layout.addWidget(self.stack)

        # Main splitter with sizing policy
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.calculator_widget)
        
        # History panel
        self.history_widget = HistoryWidget()
        self.history_widget.hide()
        self.splitter.addWidget(self.history_widget)
          # Set initial splitter sizes - calculator gets 70%, history 30%
        self.splitter.setStretchFactor(0, 7)  # Calculator side
        self.splitter.setStretchFactor(1, 3)  # History side
        
        self.main_layout.addWidget(self.splitter)
        
        # Connect signals
        self.mode_selector.currentTextChanged.connect(self.switch_mode)
        self.normal_widget.expression_evaluated.connect(self.add_to_history)
        self.scientific_widget.expression_evaluated.connect(self.add_to_history)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)
        
        # Store sizes
        self.normal_size = QSize(400, 500)
        self.scientific_size = QSize(600, 650)
        self.history_width = 250
        
        self.switch_mode("Normal")

    def switch_mode(self, mode):
        current_size = self.size()
        history_visible = not self.history_widget.isHidden()
        extra_width = self.history_width if history_visible else 0
        
        if mode == "Normal":
            self.stack.setCurrentWidget(self.normal_widget)
            if current_size.width() < self.normal_size.width() + extra_width or \
               current_size.height() < self.normal_size.height():
                self.resize(self.normal_size.width() + extra_width, self.normal_size.height())
                
        elif mode == "Scientific":
            self.stack.setCurrentWidget(self.scientific_widget)
            if current_size.width() < self.scientific_size.width() + extra_width or \
               current_size.height() < self.scientific_size.height():
                self.resize(self.scientific_size.width() + extra_width, self.scientific_size.height())
                
        elif mode == "Graphic":
            self.stack.setCurrentWidget(self.graphic_widget)

    def toggle_history(self):
        if self.history_widget.isHidden():
            current_width = self.width()
            self.history_widget.show()
            # Calculate appropriate history width and ensure integer values
            history_width = int(min(350, max(200, current_width * 0.3)))
            self.resize(current_width + history_width, self.height())
            self.splitter.setSizes([int(current_width), int(history_width)])
            # Update styles when showing
            self.history_widget.update_list_style()
            self.history_widget.update_clear_button_style()
        else:
            history_width = self.history_widget.width()
            self.history_widget.hide()
            self.resize(int(self.width() - history_width), self.height())
        self.history_btn.setChecked(not self.history_widget.isHidden())

    def add_to_history(self, expression, result):
        self.history_widget.add_entry(expression, result)    
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Auto-hide history if window becomes too small
        if self.width() < self.normal_size.width() + 100 and not self.history_widget.isHidden():
            self.history_widget.hide()
            self.history_btn.setChecked(False)
            return

        # Update history width based on window size
        if not self.history_widget.isHidden():
            total_width = self.width()
            min_calc_width = self.normal_size.width()
            max_history_width = int(min(350, total_width * 0.3))  # 30% of window width, max 350px
            min_history_width = int(min(200, total_width * 0.2))  # 20% of window width, min 200px
            
            if total_width >= min_calc_width + min_history_width:
                history_width = int(max(min_history_width, min(max_history_width, total_width - min_calc_width)))
                self.splitter.setSizes([int(total_width - history_width), int(history_width)])
                # Force style update after splitter resize
                self.history_widget.update_list_style()
                self.history_widget.update_clear_button_style()

    def on_splitter_moved(self, pos, index):
        # Update history panel styles when splitter is moved
        self.history_widget.update_list_style()
        self.history_widget.update_clear_button_style()
