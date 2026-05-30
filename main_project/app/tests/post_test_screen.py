from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from app.translations import get_translator


class PostTestScreen(QWidget):
    continueToResults = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        self.icon_label = QLabel("✓")
        icon_font = QFont()
        icon_font.setPointSize(72)
        icon_font.setBold(True)
        self.icon_label.setFont(icon_font)
        self.icon_label.setStyleSheet("color: #34a853;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(self._tr.t('post_test.complete_title'))
        title_font = QFont()
        title_font.setPointSize(26)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #2c2c2c;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.message_label = QLabel(self._tr.t('post_test.complete_message'))
        self.message_label.setFont(QFont("Arial", 14))
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #555;")
        self.message_label.setFixedWidth(700)
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.submessage_label = QLabel(self._tr.t('post_test.hand_over_message'))
        self.submessage_label.setFont(QFont("Arial", 13))
        self.submessage_label.setWordWrap(True)
        self.submessage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.submessage_label.setStyleSheet("color: #666;")
        self.submessage_label.setFixedWidth(700)
        layout.addWidget(self.submessage_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(20)

        self.continue_button = QPushButton(self._tr.t('post_test.continue_results'))
        self.continue_button.clicked.connect(self.continueToResults.emit)
        self.continue_button.setMinimumHeight(52)
        self.continue_button.setMinimumWidth(280)
        self.continue_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border-radius: 15px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

    def retranslate(self, lang=None):
        try:
            self.title_label.setText(self._tr.t('post_test.complete_title'))
            self.message_label.setText(self._tr.t('post_test.complete_message'))
            self.submessage_label.setText(self._tr.t('post_test.hand_over_message'))
            self.continue_button.setText(self._tr.t('post_test.continue_results'))
        except Exception:
            pass