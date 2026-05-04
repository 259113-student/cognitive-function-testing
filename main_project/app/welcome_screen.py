import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
)
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from app.translations import get_translator
from app.helper import resource_path
from app.sun_widget import SunWidget

class SmileyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        center = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2 - 5

        # Face
        painter.setBrush(QBrush(QColor("#FFD700"))) # Gold-like color
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(center, int(radius), int(radius))

        # Eyes
        eye_radius = int(radius * 0.1)
        eye_offset_x = int(radius * 0.4)
        eye_offset_y = int(radius * 0.2)
        painter.setBrush(QBrush(QColor("#333333")))
        
        left_eye_pos = QPointF(center.x() - eye_offset_x, center.y() - eye_offset_y)
        right_eye_pos = QPointF(center.x() + eye_offset_x, center.y() - eye_offset_y)
        
        painter.drawEllipse(left_eye_pos, eye_radius, eye_radius)
        painter.drawEllipse(right_eye_pos, eye_radius, eye_radius)

        # Smile
        smile_rect_size = int(radius * 1.2)
        
        pen = QPen(QColor("#333333"), int(radius * 0.1), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        bounding_rect = QPointF(center.x() - smile_rect_size / 2, center.y() - smile_rect_size / 2 + radius * 0.1)
        
        start_angle = -30 * 16
        span_angle = -120 * 16
        painter.drawArc(int(bounding_rect.x()), int(bounding_rect.y()), smile_rect_size, smile_rect_size, start_angle, span_angle)


class WelcomeScreen(QWidget):
    startAssessment = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.init_ui()

    def init_ui(self):
        # self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        language_row = QHBoxLayout()
        language_row.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.language_label = QLabel(self._tr.t('language.label'))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self._tr.t('language.polish'), 'pl')
        self.language_combo.addItem(self._tr.t('language.english'), 'en')
        current_lang = self._tr.language()
        current_index = 0 if current_lang == 'pl' else 1
        self.language_combo.setCurrentIndex(current_index)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.language_combo.setMinimumHeight(50)
        self.language_combo.setMinimumWidth(150)
        self.language_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.language_combo.setFont(QFont("Arial", 11))
        self.language_combo.setStyleSheet("""
        QComboBox {
            color: black;
            background-color: white;
            padding: 6px 14px;
        }
        QComboBox QAbstractItemView {
            color: black;
            background-color: white;
        }
        """)

        language_row.addWidget(self.language_label)
        language_row.addWidget(self.language_combo)
        layout.addLayout(language_row)

        # Title
        self.title = QLabel(self._tr.t('welcome.title'))
        font = QFont()
        font.setPointSize(26)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # Smiley Face
        sun = SunWidget(resource_path("assets/sun2.png"))
        layout.addWidget(sun, alignment=Qt.AlignmentFlag.AlignCenter)
        # smiley = SmileyWidget()
        # layout.addWidget(smiley, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacer
        layout.addSpacing(20)

        # "Before You Begin" Section
        self.before_title = QLabel(self._tr.t('welcome.before'))
        font_byb = QFont()
        font_byb.setPointSize(18)
        font_byb.setBold(True)
        self.before_title.setFont(font_byb)
        self.before_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.before_title)

        self.instructions = QLabel(self._tr.t('welcome.instructions'))
        # instructions.setStyleSheet("""
        #     QFrame {
        #         background-color: #ffffff;
        #         border-radius: 15px;
        #         padding: 25px;
        #     }
        # """)
        self.instructions.setFont(QFont("Arial", 12))
        self.instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.instructions.setWordWrap(True)
        self.instructions.setFixedWidth(450)
        layout.addWidget(self.instructions, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        # Start Button
        self.start_button = QPushButton(self._tr.t('welcome.start'))
        self.start_button.clicked.connect(self.startAssessment.emit)
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
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def retranslate(self, lang=None):
        try:
            self.title.setText(self._tr.t('welcome.title'))
            self.language_label.setText(self._tr.t('language.label'))
            self.language_combo.blockSignals(True)
            self.language_combo.setItemText(0, self._tr.t('language.polish'))
            self.language_combo.setItemText(1, self._tr.t('language.english'))
            self.language_combo.setCurrentIndex(0 if self._tr.language() == 'pl' else 1)
            self.language_combo.blockSignals(False)
            self.before_title.setText(self._tr.t('welcome.before'))
            self.instructions.setText(self._tr.t('welcome.instructions'))
            self.start_button.setText(self._tr.t('welcome.start'))
        except Exception:
            pass

    def on_language_changed(self, index):
        try:
            lang = self.language_combo.itemData(index)
            if lang:
                self._tr.set_language(lang)
        except Exception:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = WelcomeScreen()
    screen.setWindowTitle("Cognitive Assessment")
    screen.resize(800, 600)
    screen.show()
    sys.exit(app.exec())
