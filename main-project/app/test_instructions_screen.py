from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

class TestInstructionsScreen(QWidget):
    testReadyToStart = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._test_name = ""
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #f0f0f0;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)

        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.instructions_label = QLabel()
        self.instructions_label.setFont(QFont("Arial", 15))
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setFixedWidth(600)
        layout.addWidget(self.instructions_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()

        start_button = QPushButton("Start Test")
        start_button.clicked.connect(self.start_button_clicked)
        start_button.setMinimumHeight(50)
        start_button.setMinimumWidth(300)
        start_button.setFont(QFont("Arial", 14))
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def set_test_info(self, test_name, instructions):
        self._test_name = test_name
        self.title_label.setText(test_name)
        self.instructions_label.setText(instructions)

    def start_button_clicked(self):
        self.testReadyToStart.emit(self._test_name)

