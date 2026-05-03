from PyQt6.QtWidgets import (
    QStackedWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from app.translations import get_translator


class BaseTestScreen(QStackedWidget):
    """
    A base class for test screens to reduce code duplication.
    It provides a title, a placeholder, and a back button.
    """
    backToSelection = pyqtSignal()

    def __init__(self, test_name, parent=None):
        super().__init__(parent)
        self._test_id = test_name
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui(test_name)

    def init_ui(self, test_name):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # try to resolve a display name from translations (tests.<id>.name)
        display_name = self._tr.t(f'tests.{test_name}.name')
        if display_name.startswith('tests.'):
            display_name = test_name
        self.title_label = QLabel(f"{display_name} - {self._tr.t('common.in_progress')}")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.placeholder = QLabel(self._tr.t('common.placeholder'))
        self.placeholder.setFont(QFont("Arial", 12))
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder)

        layout.addStretch()

        self.back_button = QPushButton(self._tr.t('common.back_to_selection'))
        self.back_button.clicked.connect(self.backToSelection.emit)
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
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def retranslate(self, lang=None):
        try:
            # update placeholder and back button
            display_name = self._tr.t(f'tests.{self._test_id}.name')
            if display_name.startswith('tests.'):
                display_name = self._test_id
            self.title_label.setText(f"{display_name} - {self._tr.t('common.in_progress')}")
            self.placeholder.setText(self._tr.t('common.placeholder'))
            self.back_button.setText(self._tr.t('common.back_to_selection'))
        except Exception:
            pass