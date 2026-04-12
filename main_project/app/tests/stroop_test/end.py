from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class EndScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.title = QLabel("Results")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")

        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.setStyleSheet("font-size: 24px;")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.results_label)

        self.setLayout(self.layout)

    def set_results(self, accuracy, avg_crt, avg_icrt):
        self.results_label.setText(
            f"Accuracy: {accuracy:.1f}%\nAverage consistent RT: {avg_crt:.3f} s\nAverage inconsistent RT: {avg_icrt:.3f} s"
        )
