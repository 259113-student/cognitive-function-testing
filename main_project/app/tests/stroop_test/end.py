from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt


class EndScreen(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback

        self.layout = QVBoxLayout()

        self.title = QLabel("Results")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")

        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.setStyleSheet("font-size: 24px;")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.results_label)

        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setMinimumHeight(50)
        self.back_button.setMinimumWidth(300)
        self.back_button.setFont(QFont("Arial", 14))
        self.back_button.setStyleSheet("""
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
        self.layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

    def set_results(self, accuracy, avg_crt, avg_icrt):
        self.results_label.setText(
            f"Accuracy: {accuracy:.1f}%\nAverage consistent RT: {avg_crt:.3f} s\nAverage inconsistent RT: {avg_icrt:.3f} s"
        )

    def go_back(self):
        self.back_callback()

