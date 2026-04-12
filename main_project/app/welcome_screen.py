import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

class SmileyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)

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
        self.init_ui()

    def init_ui(self):
        # self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        # Title
        title = QLabel("Cognitive Function Assessment Suite")
        font = QFont()
        font.setPointSize(26)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Smiley Face
        smiley = SmileyWidget()
        layout.addWidget(smiley, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacer
        layout.addSpacing(20)

        # "Before You Begin" Section
        before_you_begin_title = QLabel("Before You Begin")
        font_byb = QFont()
        font_byb.setPointSize(18)
        font_byb.setBold(True)
        before_you_begin_title.setFont(font_byb)
        before_you_begin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(before_you_begin_title)

        instructions_text = """
        <p>&bull; Find a quiet, comfortable space free from distractions</p>
        <p>&bull; Each test includes clear instructions before starting</p>
        <p>&bull; Complete each test at your own pace</p>
        <p>&bull; Results are calculated immediately after each assessment</p>
        <p>&bull; You may take breaks between tests as needed</p>
        """
        instructions = QLabel(instructions_text)
        # instructions.setStyleSheet("""
        #     QFrame {
        #         background-color: #ffffff;
        #         border-radius: 15px;
        #         padding: 25px;
        #     }
        # """)
        instructions.setFont(QFont("Arial", 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        instructions.setWordWrap(True)
        instructions.setFixedWidth(450)
        layout.addWidget(instructions, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        # Start Button
        start_button = QPushButton("Begin Assessment")
        start_button.clicked.connect(self.startAssessment.emit)
        start_button.setMinimumHeight(50)
        start_button.setMinimumWidth(300)
        start_button.setFont(QFont("Arial", 14))
        start_button.setStyleSheet("""
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
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = WelcomeScreen()
    screen.setWindowTitle("Cognitive Assessment")
    screen.resize(800, 600)
    screen.show()
    sys.exit(app.exec())
