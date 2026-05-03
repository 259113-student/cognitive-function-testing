from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
from app.translations import get_translator


class StartScreen(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self._switch_callback = switch_callback
        self.title = None
        self.instructions = None
        self.start_button = None

        self.layout = QVBoxLayout()

        self.title = QLabel(self._tr.t('stroop.start_title'))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 40px;")

        self.instructions = QLabel(self._format_instructions())
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions.setWordWrap(True)

        self.start_button = QPushButton(self._tr.t('stroop.start_button'))
        self.start_button.clicked.connect(self._switch_callback)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.instructions)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

    def retranslate(self, lang=None):
        try:
            self.title.setText(self._tr.t('stroop.start_title'))
            self.instructions.setText(self._format_instructions())
            self.start_button.setText(self._tr.t('stroop.start_button'))
        except Exception:
            pass

    def _format_instructions(self):
        return self._tr.t('stroop.instructions').format(
            red=self._tr.t('stroop.red'),
            green=self._tr.t('stroop.green'),
            blue=self._tr.t('stroop.blue'),
        )
