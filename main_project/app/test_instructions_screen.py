from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from app.translations import get_translator
from app.helper import resource_path
from app.sun_widget import SunWidget


class TestInstructionsScreen(QWidget):
    testReadyToStart = pyqtSignal(str)
    backToSelection = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._test_id = ""
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(14)

        # Animowane słońce (jak na ekranie startowym)
        self.sun = SunWidget(resource_path("assets/sun2.png"))
        self.sun.setMinimumSize(200, 200)
        self.sun.setMaximumSize(220, 220)
        layout.addWidget(self.sun, alignment=Qt.AlignmentFlag.AlignCenter)

        # Tytuł testu
        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(26)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #2c2c2c;")
        layout.addWidget(self.title_label)

        # Karta: ogólne instrukcje dla pacjenta ("Przed rozpoczęciem")
        before_card = QFrame()
        before_card.setObjectName("instructionCard")
        before_card.setStyleSheet("""
            #instructionCard {
                background-color: #ffffff;
                border: 1px solid #f0e8c8;
                border-radius: 16px;
            }
        """)
        before_card_layout = QVBoxLayout(before_card)
        before_card_layout.setContentsMargins(28, 20, 28, 20)
        before_card_layout.setSpacing(8)

        self.before_title_label = QLabel(self._tr.t('welcome.before'))
        before_font = QFont()
        before_font.setPointSize(16)
        before_font.setBold(True)
        self.before_title_label.setFont(before_font)
        self.before_title_label.setStyleSheet("color: #444;")
        before_card_layout.addWidget(self.before_title_label)

        self.general_instructions_label = QLabel(self._tr.t('welcome.instructions'))
        self.general_instructions_label.setFont(QFont("Arial", 12))
        self.general_instructions_label.setWordWrap(True)
        self.general_instructions_label.setStyleSheet("color: #555;")
        before_card_layout.addWidget(self.general_instructions_label)

        before_card.setFixedWidth(660)
        layout.addWidget(before_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Karta: instrukcje konkretnego testu
        test_card = QFrame()
        test_card.setObjectName("testCard")
        test_card.setStyleSheet("""
            #testCard {
                background-color: #ffffff;
                border: 1px solid #cce6ff;
                border-radius: 16px;
            }
        """)
        test_card_layout = QVBoxLayout(test_card)
        test_card_layout.setContentsMargins(28, 20, 28, 20)
        test_card_layout.setSpacing(8)

        self.instructions_label = QLabel()
        self.instructions_label.setFont(QFont("Arial", 14))
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setStyleSheet("color: #333;")
        test_card_layout.addWidget(self.instructions_label)

        test_card.setFixedWidth(660)
        layout.addWidget(test_card, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(8)

        # Rząd przycisków: Powrót + Rozpocznij test
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(16)
        buttons_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.back_button = QPushButton(self._tr.t('common.back_to_selection'))
        self.back_button.clicked.connect(self.backToSelection.emit)
        self.back_button.setMinimumHeight(50)
        self.back_button.setMinimumWidth(220)
        self.back_button.setFont(QFont("Arial", 13))
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333;
                border: 1px solid #cccccc;
                border-radius: 15px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        buttons_row.addWidget(self.back_button)

        self.start_button = QPushButton(self._tr.t('common.start_test'))
        self.start_button.clicked.connect(self.start_button_clicked)
        self.start_button.setMinimumHeight(50)
        self.start_button.setMinimumWidth(260)
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet("""
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
        buttons_row.addWidget(self.start_button)

        layout.addLayout(buttons_row)

        self.setLayout(layout)

    def set_test_info(self, test_id):
        self._test_id = test_id
        self.retranslate()

    def start_button_clicked(self):
        self.testReadyToStart.emit(self._test_id)

    def retranslate(self, lang=None):
        try:
            title = self._tr.t(f'tests.{self._test_id}.name') if self._test_id else ""
            instructions = self._tr.t(f'instructions.{self._test_id}') if self._test_id else ""
            self.title_label.setText(title)
            self.before_title_label.setText(self._tr.t('welcome.before'))
            self.general_instructions_label.setText(self._tr.t('welcome.instructions'))
            self.instructions_label.setText(instructions)
            self.back_button.setText(self._tr.t('common.back_to_selection'))
            self.start_button.setText(self._tr.t('common.start_test'))
        except Exception:
            pass