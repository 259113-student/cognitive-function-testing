from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer, QSize

from app.tests.dms_test.dms_generator import DMSGenerator
from app.tests.dms_test.dms_logic import DMSLogic
from app.translations import get_translator


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

    def __init__(self, on_finish, parent=None, practice_mode=False):
        super().__init__(parent)
        self.on_finish = on_finish
        self.practice_mode = practice_mode
        self.num_trials = 2 if practice_mode else 10
        self.dataset_dir = Path("dms_dataset_practice" if practice_mode else "dms_dataset")
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.sample_time_ms = self.SAMPLE_TIME

        self.logic = None
        self.info_label = None
        self.sample_label = None
        self.answers_layout = None
        self.feedback_label = None
        self.practice_banner = None
        self._awaiting_feedback = False

        self.init_ui()
        self.prepare_dataset()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(16)

        # Pasek "Runda próbna"
        self.practice_banner = QLabel(self._tr.t('practice.banner') if self.practice_mode else "")
        self.practice_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bf = self.practice_banner.font()
        bf.setPointSize(13)
        bf.setBold(True)
        self.practice_banner.setFont(bf)
        self.practice_banner.setStyleSheet(
            "color: #b06000; background-color: #fff4d6; "
            "border: 1px solid #f0d8a8; border-radius: 10px; padding: 6px 14px;"
        )
        self.practice_banner.setVisible(self.practice_mode)
        layout.addWidget(self.practice_banner, alignment=Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel(self._tr.t('dms.remember_pattern'))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.info_label.setStyleSheet("QLabel { color: #1f1f1f; padding: 6px 12px; }")

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

        # Etykieta informacji zwrotnej (tylko praktyka)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ff = self.feedback_label.font()
        ff.setPointSize(22)
        ff.setBold(True)
        self.feedback_label.setFont(ff)
        self.feedback_label.setVisible(False)

        answers_widget = QWidget()
        self.answers_layout = QHBoxLayout(answers_widget)
        self.answers_layout.setSpacing(24)
        self.answers_layout.setContentsMargins(0, 10, 0, 0)

        layout.addWidget(self.info_label)
        layout.addWidget(self.sample_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        layout.addWidget(answers_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_sample_time(self, sample_time_ms):
        self.sample_time_ms = max(100, int(sample_time_ms))

    def prepare_dataset(self):
        generator = DMSGenerator(output_dir=str(self.dataset_dir))
        generator.generate_dataset(self.num_trials)
        self.logic = DMSLogic(str(self.dataset_dir))

    def reset_task(self):
        self.prepare_dataset()
        self._awaiting_feedback = False
        self.feedback_label.setVisible(False)
        self.run_next_trial()

    def clear_answers(self):
        while self.answers_layout.count():
            item = self.answers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def run_next_trial(self):
        self.clear_answers()
        self.feedback_label.setVisible(False)

        if self.practice_mode and self.logic.current_trial_index >= self.num_trials:
            self.on_finish(None)
            return

        if not self.logic.has_next_trial():
            summary = self.logic.summary()
            self.on_finish(summary)
            return

        self.show_fixation()

    def show_fixation(self):
        self.sample_label.setPixmap(QPixmap())
        self.sample_label.setText("+")
        self.info_label.setText(self._tr.t('dms.focus_center'))
        QTimer.singleShot(self.FIXATION_TIME, self.show_sample)

    def show_sample(self):
        sample_path = self.logic.get_sample_path()
        pixmap = QPixmap(str(sample_path))
        self.sample_label.setText("")
        self.sample_label.setPixmap(
            pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
        )
        self.info_label.setText(self._tr.t('dms.remember_this_pattern'))
        QTimer.singleShot(self.sample_time_ms, self.show_choices)

    def show_choices(self):
        self.sample_label.setPixmap(QPixmap())
        self.sample_label.setText("")
        self.info_label.setText(self._tr.t('dms.choose_identical'))

        answer_paths = self.logic.get_answer_paths()
        for answer_path in answer_paths:
            button = DmsImageButton(
                answer_path,
                callback=lambda checked=False, p=answer_path: self.handle_answer(p)
            )
            self.answers_layout.addWidget(button)

        self.logic.start_response_timer()

    def handle_answer(self, answer_path: Path):
        if self._awaiting_feedback:
            return
        correct, _rt = self.logic.submit_answer(answer_path.name)

        if self.practice_mode:
            self._awaiting_feedback = True
            self.clear_answers()
            self._show_feedback(correct)
            QTimer.singleShot(1000, self._after_feedback)
        else:
            QTimer.singleShot(250, self.run_next_trial)

    def _show_feedback(self, correct):
        if correct:
            self.feedback_label.setText(self._tr.t('practice.correct'))
            self.feedback_label.setStyleSheet("color: #2e7d32;")
        else:
            self.feedback_label.setText(self._tr.t('practice.wrong'))
            self.feedback_label.setStyleSheet("color: #c62828;")
        self.info_label.setText("")
        self.feedback_label.setVisible(True)

    def _after_feedback(self):
        self._awaiting_feedback = False
        self.feedback_label.setVisible(False)
        self.run_next_trial()

    def retranslate(self, lang=None):
        try:
            if self.practice_mode:
                self.practice_banner.setText(self._tr.t('practice.banner'))
            current = self.info_label.text() if self.info_label else ""
            if current:
                if current in ("Remember the pattern.", self._tr.t('dms.remember_pattern')):
                    self.info_label.setText(self._tr.t('dms.remember_pattern'))
                elif current in ("Focus on the center", self._tr.t('dms.focus_center')):
                    self.info_label.setText(self._tr.t('dms.focus_center'))
                elif current in ("Remember this pattern", self._tr.t('dms.remember_this_pattern')):
                    self.info_label.setText(self._tr.t('dms.remember_this_pattern'))
                elif current in ("Choose the identical pattern", self._tr.t('dms.choose_identical')):
                    self.info_label.setText(self._tr.t('dms.choose_identical'))
        except Exception:
            pass