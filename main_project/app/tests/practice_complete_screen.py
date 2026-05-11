from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from app.translations import get_translator


class PracticeCompleteScreen(QWidget):
    """Pokazywany po rundzie próbnej, przed właściwym testem."""
    startRealTest = pyqtSignal()
    repeatPractice = pyqtSignal()

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

        self.title_label = QLabel(self._tr.t('practice.complete_title'))
        tf = QFont()
        tf.setPointSize(26)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setStyleSheet("color: #2c2c2c;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.message_label = QLabel(self._tr.t('practice.complete_message'))
        self.message_label.setFont(QFont("Arial", 14))
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #555;")
        self.message_label.setFixedWidth(640)
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(16)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(16)
        buttons_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.repeat_button = QPushButton(self._tr.t('practice.repeat'))
        self.repeat_button.clicked.connect(self.repeatPractice.emit)
        self.repeat_button.setMinimumHeight(50)
        self.repeat_button.setMinimumWidth(240)
        self.repeat_button.setFont(QFont("Arial", 13))
        self.repeat_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repeat_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #333;
                border: 1px solid #cccccc; border-radius: 15px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #f0f0f0; }
        """)
        buttons_row.addWidget(self.repeat_button)

        self.start_button = QPushButton(self._tr.t('practice.start_real'))
        self.start_button.clicked.connect(self.startRealTest.emit)
        self.start_button.setMinimumHeight(50)
        self.start_button.setMinimumWidth(260)
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #333; color: white;
                border-radius: 15px; padding: 10px 24px;
            }
            QPushButton:hover { background-color: #555; }
        """)
        buttons_row.addWidget(self.start_button)

        layout.addLayout(buttons_row)

    def retranslate(self, lang=None):
        try:
            self.title_label.setText(self._tr.t('practice.complete_title'))
            self.message_label.setText(self._tr.t('practice.complete_message'))
            self.repeat_button.setText(self._tr.t('practice.repeat'))
            self.start_button.setText(self._tr.t('practice.start_real'))
        except Exception:
            pass