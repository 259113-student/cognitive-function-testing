import random
import time
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from app.translations import get_translator

colors = {'red': 'r', 'green': 'g', 'blue': 'b'}


class StroopScreen(QWidget):
    def __init__(self, finish_callback):
        super().__init__()
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)

        self.word = None
        self.color = None
        self.start_time = None
        self.consistent = None

        self.consistent_rt_sum = 0
        self.inconsistent_rt_sum = 0
        self._word_map = {
            'red': self._tr.t('stroop.red'),
            'green': self._tr.t('stroop.green'),
            'blue': self._tr.t('stroop.blue'),
        }

        self.setWindowTitle(self._tr.t('stroop.window_title'))
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 48px;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.trial = 0
        self.max_trials = 5

        self.next_trial()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.results = []

        self.finish_callback = finish_callback

    def next_trial(self):
        if self.trial >= self.max_trials:
            accuracy, avg_crt, avg_icrt = self.compute_results()
            self.finish_callback(accuracy, avg_crt, avg_icrt)
            return

        self.word = random.choice(list(self._word_map.keys()))
        self.color = random.choice(list(colors.keys()))
        self.consistent = self.word == self.color

        self.label.setText(self._word_map[self.word])
        self.label.setStyleSheet(f"color: {self.color}; font-size: 48px;")

        self.start_time = time.perf_counter()
        self.trial += 1

    def keyPressEvent(self, event):
        key_map = {
            Qt.Key.Key_R: 'r',
            Qt.Key.Key_G: 'g',
            Qt.Key.Key_B: 'b'
        }

        if event.key() in key_map:
            response = key_map[event.key()]
            if self.consistent:
                self.consistent_rt_sum += time.perf_counter() - self.start_time
            else:
                self.inconsistent_rt_sum += time.perf_counter() - self.start_time

            correct = (response == self.color[0])
            self.results.append(correct)

            self.next_trial()

    def compute_results(self):
        total = len(self.results)
        correct = sum(1 for r in self.results if r)

        accuracy = (correct / total) * 100 if total > 0 else 0

        avg_consistent_rt = self.consistent_rt_sum / total if total > 0 else 0
        avg_inconsistent_rt = self.inconsistent_rt_sum / total if total > 0 else 0

        return accuracy, avg_consistent_rt, avg_inconsistent_rt

    def retranslate(self, lang=None):
        try:
            self.setWindowTitle(self._tr.t('stroop.window_title'))
            self._word_map = {
                'red': self._tr.t('stroop.red'),
                'green': self._tr.t('stroop.green'),
                'blue': self._tr.t('stroop.blue'),
            }
            if self.word in self._word_map:
                self.label.setText(self._word_map[self.word])
        except Exception:
            pass
