import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from app.translations import get_translator
from app.helper import resource_path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QDialog, QComboBox, QSpinBox, QDialogButtonBox
)

class TestCard(QFrame):
    """A clickable card widget for displaying a test with an icon."""
    clicked = pyqtSignal(str)

    def __init__(self, test_id, display_name, description, measures, icon_path, parent=None):
        super().__init__(parent)
        self.test_id = test_id
        self.display_name = display_name
        self._tr = get_translator()
        self.init_ui(display_name, description, measures, icon_path)

    def init_ui(self, test_name, description, measures, icon_path):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
        TestCard {
            background-color: #ffffff;
            border: 1px solid #ffffff;
            border-radius: 15px;
        }

        TestCard:hover {
            background-color: #e6f7ff;
            border: 1px solid #e6f7ff;
        }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 15)

        # --- Icon Section ---
        icon_container = QWidget()
        icon_container.setMinimumHeight(100)
        icon_container.setStyleSheet("background-color:	#cceeff; border-top-left-radius: 15px; border-top-right-radius: 15px;")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        if icon_path:
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)

        # --- Content Section ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        self.name_label = QLabel(test_name)
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        content_layout.addWidget(self.name_label)

        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setFont(QFont("Arial", 15))
        content_layout.addWidget(self.desc_label)
        
        layout.addLayout(content_layout)
        
        # Add a stretch to push the measures section to the bottom
        layout.addStretch()

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(separator)

        # --- Measures Section ---
        measures_layout = QVBoxLayout()
        measures_layout.setContentsMargins(15, 5, 15, 0)
        measures_layout.setSpacing(2)

        self.measures_title_label = QLabel(self._tr.t('test_selection.measures'))
        self.measures_title_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        measures_layout.addWidget(self.measures_title_label)

        self.measures_label = QLabel(measures)
        self.measures_label.setFont(QFont("Arial", 12))
        self.measures_label.setStyleSheet("color: #555;")
        measures_layout.addWidget(self.measures_label)
        
        layout.addLayout(measures_layout)

    def retranslate(self):
        try:
            self.name_label.setText(self._tr.t(f'tests.{self.test_id}.name'))
            self.desc_label.setText(self._tr.t(f'tests.{self.test_id}.description'))
            self.measures_title_label.setText(self._tr.t('test_selection.measures'))
            self.measures_label.setText(self._tr.t(f'tests.{self.test_id}.measures'))
        except Exception:
            pass

    def mousePressEvent(self, event):
        self.clicked.emit(self.test_id)
        super().mousePressEvent(event)

class DoctorSettingsDialog(QDialog):
    def __init__(self, current_dms_time_ms: int, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self.setWindowTitle(self._tr.t('doctor_panel.title'))
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Język
        lang_row = QHBoxLayout()
        self.language_label = QLabel(self._tr.t('language.label'))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self._tr.t('language.polish'), 'pl')
        self.language_combo.addItem(self._tr.t('language.english'), 'en')
        self.language_combo.setCurrentIndex(0 if self._tr.language() == 'pl' else 1)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.language_label)
        lang_row.addWidget(self.language_combo)
        layout.addLayout(lang_row)

        # Czas próbki DMS
        dms_row = QHBoxLayout()
        self.dms_label = QLabel(self._tr.t('dms.sample_duration'))
        self.dms_spinbox = QSpinBox()
        self.dms_spinbox.setRange(100, 5000)
        self.dms_spinbox.setSingleStep(50)
        self.dms_spinbox.setSuffix(" ms")
        self.dms_spinbox.setValue(current_dms_time_ms)
        dms_row.addWidget(self.dms_label)
        dms_row.addWidget(self.dms_spinbox)
        layout.addLayout(dms_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_language_changed(self, idx):
        lang = self.language_combo.itemData(idx)
        if lang:
            self._tr.set_language(lang)

    def get_dms_time(self):
        return self.dms_spinbox.value()

class TestSelectionScreen(QWidget):
    testSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self.dms_sample_time_ms = 800
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 30, 50, 50)
        main_layout.setSpacing(20)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.setFont(QFont("Arial", 18))
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; }
            QPushButton:hover { background-color: #e0e0e0; border-radius: 20px; }
        """)
        self.settings_button.clicked.connect(self._open_doctor_settings)
        top_bar.addWidget(self.settings_button)
        main_layout.addLayout(top_bar)

        self.title_label = QLabel(self._tr.t('test_selection.title'))
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(self._tr.t('test_selection.subtitle'))
        self.subtitle_label.setFont(QFont("Arial", 12))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.subtitle_label)
        
        main_layout.addSpacing(20)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        self.cards = []
        
        tests = [
            ("stroop", resource_path("assets/brain-icon.png")),
            ("dms", resource_path("assets/pending-icon.png")),
        ]

        for test_id, icon in tests:
            name = self._tr.t(f'tests.{test_id}.name')
            desc = self._tr.t(f'tests.{test_id}.description')
            measures = self._tr.t(f'tests.{test_id}.measures')
            card = TestCard(test_id, name, desc, measures, icon)
            card.clicked.connect(self.testSelected.emit)
            cards_layout.addWidget(card)
            self.cards.append(card)
            
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        self.about_title_label = QLabel(self._tr.t('test_selection.about_title'))
        about_title_font = QFont()
        about_title_font.setPointSize(20)
        about_title_font.setBold(True)
        self.about_title_label.setFont(about_title_font)
        # self.about_title_label.setStyleSheet("color: #4da6ff;")
        self.about_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.about_title_label)

        self.about_text_label = QLabel(self._tr.t('test_selection.about_text'))
        self.about_text_label.setWordWrap(True)
        self.about_text_label.setFont(QFont("Arial", 10))
        self.about_text_label.setStyleSheet("color: #444;")
        self.about_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.about_text_label.setFixedWidth(900)
        main_layout.addWidget(self.about_text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(30)

        self.setLayout(main_layout)

    def retranslate(self, lang=None):
        try:
            self.title_label.setText(self._tr.t('test_selection.title'))
            self.subtitle_label.setText(self._tr.t('test_selection.subtitle'))
            self.about_title_label.setText(self._tr.t('test_selection.about_title'))
            self.about_text_label.setText(self._tr.t('test_selection.about_text'))
            for card in self.cards:
                card.retranslate()
        except Exception:
            pass

    def _open_doctor_settings(self):
        dlg = DoctorSettingsDialog(self.dms_sample_time_ms, self)
        if dlg.exec():
            self.dms_sample_time_ms = dlg.get_dms_time()

    def get_dms_sample_time_ms(self):
        return self.dms_sample_time_ms

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = TestSelectionScreen()
    screen.setWindowTitle("Select a Test")
    screen.resize(900, 700)
    screen.show()
    sys.exit(app.exec())