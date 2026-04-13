from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer, QSize

from main_project.app.tests.dms_test.dms_generator import DMSGenerator
from main_project.app.tests.dms_test.dms_logic import DMSLogic


class DmsImageButton(QPushButton):
    def __init__(self, image_path, callback, parent=None):
        super().__init__(parent)
        self.setFixedSize(190, 190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(QIcon(str(image_path)))
        self.setIconSize(QSize(170, 170))
        self.clicked.connect(callback)

        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #d6d6d6;
                border-radius: 16px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                border: 3px solid #4a90e2;
            }
            QPushButton:pressed {
                background-color: #f2f7ff;
                border: 3px solid #2f6fc2;
            }
        """)


class DMSTaskScreen(QWidget):
    FIXATION_TIME = 500
    SAMPLE_TIME = 800

    def __init__(self, on_finish, parent=None):
        super().__init__(parent)
        self.on_finish = on_finish
        self.dataset_dir = Path("dms_dataset")

        self.logic = None
        self.info_label = None
        self.sample_label = None
        self.answers_layout = None

        self.init_ui()
        self.prepare_dataset()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(22)

        self.info_label = QLabel("Remember the pattern.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.info_label.setStyleSheet("""
            QLabel {
                color: #1f1f1f;
                padding: 6px 12px;
            }
        """)

        self.sample_label = QLabel("+")
        self.sample_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sample_label.setFixedSize(320, 320)
        self.sample_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #d8d8d8;
                border-radius: 22px;
                font-size: 46px;
                font-weight: bold;
                color: #222222;
            }
        """)

        answers_widget = QWidget()
        self.answers_layout = QGridLayout(answers_widget)
        self.answers_layout.setSpacing(24)
        self.answers_layout.setContentsMargins(0, 10, 0, 0)

        layout.addWidget(self.info_label)
        layout.addWidget(self.sample_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(answers_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def prepare_dataset(self):
        generator = DMSGenerator(output_dir=str(self.dataset_dir))
        generator.generate_dataset(10)
        self.logic = DMSLogic(str(self.dataset_dir))

    def reset_task(self):
        self.prepare_dataset()
        self.run_next_trial()

    def clear_answers(self):
        while self.answers_layout.count():
            item = self.answers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def run_next_trial(self):
        self.clear_answers()

        if not self.logic.has_next_trial():
            summary = self.logic.summary()
            self.on_finish(summary)
            return

        self.show_fixation()

    def show_fixation(self):
        self.sample_label.setPixmap(QPixmap())
        self.sample_label.setText("+")
        self.info_label.setText("Focus on the center")
        QTimer.singleShot(self.FIXATION_TIME, self.show_sample)

    def show_sample(self):
        sample_path = self.logic.get_sample_path()
        pixmap = QPixmap(str(sample_path))

        self.sample_label.setText("")
        self.sample_label.setPixmap(
            pixmap.scaled(
                240,
                240,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.info_label.setText("Remember this pattern")
        QTimer.singleShot(self.SAMPLE_TIME, self.show_choices)

    def show_choices(self):
        self.sample_label.setPixmap(QPixmap())
        self.sample_label.setText("")
        self.info_label.setText("Choose the identical pattern")

        answer_paths = self.logic.get_answer_paths()

        for i, answer_path in enumerate(answer_paths):
            button = DmsImageButton(
                answer_path,
                callback=lambda checked=False, p=answer_path: self.handle_answer(p)
            )
            self.answers_layout.addWidget(button, i // 2, i % 2)

        self.logic.start_response_timer()

    def handle_answer(self, answer_path: Path):
        self.logic.submit_answer(answer_path.name)
        QTimer.singleShot(250, self.run_next_trial)