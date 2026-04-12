from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt


class StartScreen(QWidget):
    def __init__(self, switch_callback):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Stroop Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 40px;")

        instructions = QLabel(
            "Press the key corresponding to the COLOR of the word.\n"
            "Ignore the text itself.\n\n"
            "R = Red, G = Green, B = Blue"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start")
        start_button.clicked.connect(switch_callback)

        layout.addWidget(title)
        layout.addWidget(instructions)
        layout.addWidget(start_button)

        self.setLayout(layout)
