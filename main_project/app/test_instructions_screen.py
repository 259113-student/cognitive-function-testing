from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from app.translations import get_translator

class TestInstructionsScreen(QWidget):
    testReadyToStart = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._test_id = ""
        self._dms_sample_time_ms = 800
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)

        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.instructions_label = QLabel()
        self.instructions_label.setFont(QFont("Arial", 15))
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setFixedWidth(600)
        layout.addWidget(self.instructions_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.dms_settings_widget = QWidget()
        self.dms_settings_layout = QHBoxLayout(self.dms_settings_widget)
        self.dms_settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dms_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.dms_settings_layout.setSpacing(12)

        self.dms_sample_label = QLabel(self._tr.t('dms.sample_duration'))
        self.dms_sample_spinbox = QSpinBox()
        self.dms_sample_spinbox.setRange(100, 5000)
        self.dms_sample_spinbox.setSingleStep(50)
        self.dms_sample_spinbox.setValue(self._dms_sample_time_ms)
        self.dms_sample_spinbox.setSuffix(" ms")
        self.dms_sample_spinbox.valueChanged.connect(self._on_dms_sample_time_changed)

        self.dms_settings_layout.addWidget(self.dms_sample_label)
        self.dms_settings_layout.addWidget(self.dms_sample_spinbox)
        layout.addWidget(self.dms_settings_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()

        self.start_button = QPushButton(self._tr.t('common.start_test'))
        self.start_button.clicked.connect(self.start_button_clicked)
        self.start_button.setMinimumHeight(50)
        self.start_button.setMinimumWidth(300)
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("""
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
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self._update_dms_controls_visibility()

    def set_test_info(self, test_id):
        self._test_id = test_id
        self.retranslate()

    def start_button_clicked(self):
        self.testReadyToStart.emit(self._test_id)

    def get_dms_sample_time_ms(self):
        return self._dms_sample_time_ms

    def retranslate(self, lang=None):
        try:
            title = self._tr.t(f'tests.{self._test_id}.name') if self._test_id else ""
            instructions = self._tr.t(f'instructions.{self._test_id}') if self._test_id else ""
            self.title_label.setText(title)
            self.instructions_label.setText(instructions)
            self.dms_sample_label.setText(self._tr.t('dms.sample_duration'))
            self.dms_sample_spinbox.setSuffix(" ms")
            self.start_button.setText(self._tr.t('common.start_test'))
            self._update_dms_controls_visibility()
        except Exception:
            pass

    def _update_dms_controls_visibility(self):
        is_dms = self._test_id == 'dms'
        self.dms_settings_widget.setVisible(is_dms)

    def _on_dms_sample_time_changed(self, value):
        self._dms_sample_time_ms = int(value)

