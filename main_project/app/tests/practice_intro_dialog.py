from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.translations import get_translator


class PracticeIntroDialog(QDialog):
    """Modalny popup informujący, że za chwilę rozpocznie się runda próbna."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self.setWindowTitle(self._tr.t('practice.intro_title'))
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet("QDialog { background-color: #fffdf5; }")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 24)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ikona
        self.icon_label = QLabel("🎯")
        icon_font = QFont()
        icon_font.setPointSize(48)
        self.icon_label.setFont(icon_font)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Tytuł
        self.title_label = QLabel(self._tr.t('practice.intro_title'))
        tf = QFont()
        tf.setPointSize(20)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setStyleSheet("color: #2c2c2c;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Treść
        self.message_label = QLabel(self._tr.t('practice.intro_message'))
        self.message_label.setFont(QFont("Arial", 13))
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #555;")
        layout.addWidget(self.message_label)

        layout.addSpacing(8)

        # Przycisk
        self.start_button = QPushButton(self._tr.t('practice.intro_button'))
        self.start_button.clicked.connect(self.accept)
        self.start_button.setMinimumHeight(48)
        self.start_button.setMinimumWidth(240)
        self.start_button.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #333; color: white;
                border-radius: 14px; padding: 10px 20px;
            }
            QPushButton:hover { background-color: #555; }
        """)
        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_row.addWidget(self.start_button)
        layout.addLayout(button_row)