import random
import time
import math
from dataclasses import dataclass
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from app.translations import get_translator
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation


@dataclass
class StroopTrial:
    trial: int
    congruent: bool   # True = word colour matches (W-like), False = incongruent (CW-like)
    correct: bool
    rt: float


class StroopScreen(QWidget):
    def __init__(self, finish_callback):
        super().__init__()
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)

        self.word = None
        self.color = None
        self.start_time = None
        self.consistent = None

        self._word_map = {
            'red':   self._tr.t('stroop.red'),
            'green': self._tr.t('stroop.green'),
            'blue':  self._tr.t('stroop.blue'),
        }
        self.colors = {
            'red':   self._tr.t('stroop.r'),
            'green': self._tr.t('stroop.g'),
            'blue':  self._tr.t('stroop.b'),
        }

        self.setWindowTitle(self._tr.t('stroop.window_title'))
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 48px;")

        self.opacity_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.trial = 0
        self.max_trials = 20
        self.results = []          # list of StroopTrial
        self.finish_callback = finish_callback

        self.next_trial()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def next_trial(self):
        if self.trial >= self.max_trials:
            self.finish_callback(self.compute_summary())
            return

        self.word  = random.choice(list(self._word_map.keys()))
        self.color = random.choice(list(self.colors.keys()))
        self.consistent = (self.word == self.color)

        self.label.setText(self._word_map[self.word])
        self.label.setStyleSheet(f"color: {self.color}; font-size: 60px;")
        self.start_time = time.perf_counter()
        self.trial += 1

    def keyPressEvent(self, event):
        key_map_en = {Qt.Key.Key_R: 'r', Qt.Key.Key_G: 'g', Qt.Key.Key_B: 'b'}
        key_map_pl = {Qt.Key.Key_C: 'r', Qt.Key.Key_Z: 'g', Qt.Key.Key_N: 'b'}
        key_map = key_map_en if self._word_map['red'] == 'RED' else key_map_pl

        if event.key() in key_map:
            rt = time.perf_counter() - self.start_time
            response = key_map[event.key()]
            correct = (response == self.color[0])
            self.results.append(StroopTrial(
                trial=self.trial,
                congruent=self.consistent,
                correct=correct,
                rt=rt
            ))
            self.flash_fade()
            self.next_trial()

    def compute_summary(self):
        trials = self.results
        total = len(trials)
        if total == 0:
            return {}

        cong  = [t for t in trials if t.congruent]
        incong = [t for t in trials if not t.congruent]

        def stats(group):
            if not group: return 0.0, 0.0, 0.0, 0
            rts = [t.rt for t in group]
            acc = sum(1 for t in group if t.correct) / len(group) * 100
            avg = sum(rts) / len(rts)
            errors = sum(1 for t in group if not t.correct)
            return acc, avg, errors, len(group)

        acc_w,  avg_rt_w,  err_w,  n_w  = stats(cong)
        acc_cw, avg_rt_cw, err_cw, n_cw = stats(incong)
        acc_all = sum(1 for t in trials if t.correct) / total * 100

        # Interference RT (Stroop effect in ms)
        interference_rt = avg_rt_cw - avg_rt_w

        # IG score — Golden (1978), adapted for accuracy-based version
        # IG = acc_CW - (acc_W * acc_C) / (acc_W + acc_C)
        # We use congruent as W proxy; no pure C condition in this version
        ig = acc_cw - (acc_w * acc_cw) / (acc_w + acc_cw) if (acc_w + acc_cw) > 0 else 0.0

        # Stroop effect % = relative RT slowdown
        stroop_pct = (interference_rt / avg_rt_w * 100) if avg_rt_w > 0 else 0.0

        # Error interference = extra errors in incongruent vs congruent (rate)
        err_rate_w  = err_w  / n_w  * 100 if n_w  else 0.0
        err_rate_cw = err_cw / n_cw * 100 if n_cw else 0.0
        error_interference = err_rate_cw - err_rate_w

        all_rts = [t.rt for t in trials]
        avg_rt  = sum(all_rts) / total
        sorted_rt = sorted(all_rts)
        n = len(sorted_rt)
        median_rt = sorted_rt[n//2] if n%2==1 else (sorted_rt[n//2-1]+sorted_rt[n//2])/2
        variance = sum((r-avg_rt)**2 for r in all_rts)/total
        std_rt = math.sqrt(variance)

        return {
            "total":            total,
            "n_congruent":      n_w,
            "n_incongruent":    n_cw,
            "accuracy":         acc_all,
            "acc_congruent":    acc_w,
            "acc_incongruent":  acc_cw,
            "avg_rt":           avg_rt,
            "avg_rt_congruent": avg_rt_w,
            "avg_rt_incongruent": avg_rt_cw,
            "median_rt":        median_rt,
            "std_rt":           std_rt,
            "interference_rt":  interference_rt,
            "stroop_effect_pct": stroop_pct,
            "ig_score":         ig,
            "error_interference": error_interference,
            "err_rate_congruent":   err_rate_w,
            "err_rate_incongruent": err_rate_cw,
            "trials":           trials,
        }

    def retranslate(self, lang=None):
        try:
            self.setWindowTitle(self._tr.t('stroop.window_title'))
            self._word_map = {
                'red':   self._tr.t('stroop.red'),
                'green': self._tr.t('stroop.green'),
                'blue':  self._tr.t('stroop.blue'),
            }
            if self.word in self._word_map:
                self.label.setText(self._word_map[self.word])
        except Exception:
            pass

    def flash_fade(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(50)
        self.anim.setStartValue(1.0)
        self.anim.setKeyValueAt(0.5, 0.2)
        self.anim.setEndValue(1.0)
        self.anim.start()