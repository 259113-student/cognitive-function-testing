import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class TestCard(QFrame):
    """A clickable card widget for displaying a test with an icon."""
    clicked = pyqtSignal(str)

    def __init__(self, test_name, description, measures, icon_path, parent=None):
        super().__init__(parent)
        self.test_name = test_name
        self.init_ui(test_name, description, measures, icon_path)

    def init_ui(self, test_name, description, measures, icon_path):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        # Use setFixedSize to ensure all cards are identical in size
        self.setFixedSize(320, 350)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            TestCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
            }
            TestCard:hover {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 15)

        # --- Icon Section ---
        icon_container = QWidget()
        icon_container.setMinimumHeight(100)
        icon_container.setStyleSheet("background-color: #f8f8f8; border-top-left-radius: 15px; border-top-right-radius: 15px;")
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

        name_label = QLabel(test_name)
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        name_label.setFont(name_font)
        content_layout.addWidget(name_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Arial", 15))
        content_layout.addWidget(desc_label)
        
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

        measures_title_label = QLabel("Measures:")
        measures_title_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        measures_layout.addWidget(measures_title_label)

        measures_label = QLabel(measures)
        measures_label.setFont(QFont("Arial", 12))
        measures_label.setStyleSheet("color: #555;")
        measures_layout.addWidget(measures_label)
        
        layout.addLayout(measures_layout)

    def mousePressEvent(self, event):
        self.clicked.emit(self.test_name)
        super().mousePressEvent(event)


class TestSelectionScreen(QWidget):
    testSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 30, 50, 50)
        main_layout.setSpacing(20)

        title = QLabel("Cognitive Function Assessment")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("Select a test to begin cognitive evaluation")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        
        tests = [
            ("Stroop Test", "Identify the color of text while ignoring the word itself", "Attention & Processing Speed", "app/assets/brain-icon.png"),
            ("DMS Test", "Remember a sample stimulus and identify it after a delay", "Short-term Memory", "app/assets/pending-icon.png")
        ]

        for name, desc, measures, icon in tests:
            card = TestCard(name, desc, measures, icon)
            card.clicked.connect(self.testSelected.emit)
            cards_layout.addWidget(card)
            
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        about_title = QLabel("About these tests")
        about_title_font = QFont()
        about_title_font.setPointSize(16)
        about_title_font.setBold(True)
        about_title.setFont(about_title_font)
        about_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(about_title)

        about_text = QLabel(
            "This assessment suite evaluates various aspects of cognitive function including attention, "
            "memory, processing speed, and executive function. Each test is designed to measure specific "
            "cognitive abilities through standardized tasks. Results are calculated immediately upon "
            "completion of each test."
        )
        about_text.setWordWrap(True)
        about_text.setFont(QFont("Arial", 10))
        about_text.setStyleSheet("color: #444;")
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_text.setFixedWidth(700)
        main_layout.addWidget(about_text, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = TestSelectionScreen()
    screen.setWindowTitle("Select a Test")
    screen.resize(900, 700)
    screen.show()
    sys.exit(app.exec())