from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.translations import get_translator


class EndScreen(QWidget):
    def __init__(self, back_callback, on_restart):
        super().__init__()
        self.back_callback = back_callback
        self.on_restart = on_restart
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)

        self.layout = QVBoxLayout()

        self.title = QLabel(self._tr.t('stroop.results_title'))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 40px; font-weight: bold;")

        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.setStyleSheet("font-size: 24px;")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.results_label)

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_row.setSpacing(30)

        self.restart_button = QPushButton(self._tr.t('stroop.restart'))
        self.restart_button.clicked.connect(self.on_restart)
        self.restart_button.setMinimumHeight(50)
        self.restart_button.setMinimumWidth(300)
        self.restart_button.setFont(QFont("Arial", 14))
        self.restart_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_button.setStyleSheet("""
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

        button_row.addWidget(self.restart_button)

        self.back_button = QPushButton(self._tr.t('stroop.back_main_menu'))
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
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
        button_row.addWidget(self.back_button)
        self.layout.addLayout(button_row)
        self.setLayout(self.layout)

    def set_results(self, accuracy, avg_crt, avg_icrt):
        self.results_label.setText(
            f"{self._tr.t('stroop.accuracy_percent').format(percent=accuracy)}\n"
            f"{self._tr.t('stroop.avg_consistent_rt').format(value=avg_crt)}\n"
            f"{self._tr.t('stroop.avg_inconsistent_rt').format(value=avg_icrt)}"
        )

    def go_back(self):
        self.back_callback()

    def retranslate(self, lang=None):
        try:
            self.title.setText(self._tr.t('stroop.results_title'))
            self.back_button.setText(self._tr.t('stroop.back_main_menu'))
            self.restart_button.setText(self._tr.t('stroop.restart'))
        except Exception:
            pass

