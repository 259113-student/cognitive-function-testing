from PyQt6.QtWidgets import (
    QStackedWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal


class BaseTestScreen(QStackedWidget):
    """
    A base class for test screens to reduce code duplication.
    It provides a title, a placeholder, and a back button.
    """
    backToSelection = pyqtSignal()

    def __init__(self, test_name, parent=None):
        super().__init__(parent)
        self.init_ui(test_name)

    def init_ui(self, test_name):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        title = QLabel(test_name + " - In Progress")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        placeholder = QLabel("Test logic will be implemented here.")
        placeholder.setFont(QFont("Arial", 12))
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()

        back_button = QPushButton("Back to Test Selection")
        back_button.clicked.connect(self.backToSelection.emit)
        back_button.setMinimumHeight(50)
        back_button.setMinimumWidth(300)
        back_button.setFont(QFont("Arial", 14))
        back_button.setStyleSheet("""
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
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)