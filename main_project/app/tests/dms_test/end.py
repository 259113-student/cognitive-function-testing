import csv
import json
import math
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QFrame, QScrollArea, QButtonGroup, QFileDialog, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QPointF

from app.translations import get_translator

# ── Palette ────────────────────────────────────────
C_BG      = "#f9f7f4"
C_CARD    = "#ffffff"
C_BORDER  = "#ede9e3"
C_TEXT    = "#2c2825"
C_MUTED   = "#9a9590"
C_FAINT   = "#e8e4de"

C_SAGE    = "#4dab83"   # correct / good
C_CORAL   = "#e06058"   # wrong / bad
C_SLATE   = "#5b8fd4"   # avg RT
C_LAVEND  = "#8b7ad9"   # fastest
C_AMBER   = "#e09a30"   # slowest
C_TEAL    = "#35b8ae"   # median
C_STONE   = "#8a96a8"   # std
C_MINT    = "#40c48a"   # consistency
C_ROSE    = "#d95878"   # learning


def shadow(blur=20, dy=2, alpha=12):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur)
    sh.setOffset(0, dy)
    sh.setColor(QColor(0, 0, 0, alpha))
    return sh


# ══════════════════════════════════════════════════
class AccuracyRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._v = 0.0
        self.setFixedSize(200, 200)
        self.setStyleSheet("background:transparent;")
        self._accuracy_label = "accuracy"
        self._anim = QPropertyAnimation(self, b"v")
        self._anim.setDuration(1400)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def animate(self, target):
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(target))
        self._anim.start()

    @pyqtProperty(float)
    def v(self): return self._v

    @v.setter
    def v(self, val):
        self._v = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 20

        # Track
        pen = QPen(QColor(C_FAINT), 10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Arc
        v = self._v
        arc_col = C_SAGE if v >= 80 else (C_AMBER if v >= 50 else C_CORAL)
        pen2 = QPen(QColor(arc_col), 10)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        span = int(v / 100.0 * 360 * 16)
        p.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), 90 * 16, -span)

        # Inner circle background
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#faf9f7")))
        p.drawEllipse(QRectF(cx - r + 14, cy - r + 14, (r - 14) * 2, (r - 14) * 2))

        # Text
        p.setPen(QPen(QColor(C_TEXT)))
        p.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        p.drawText(QRectF(0, cy - 22, w, 34), Qt.AlignmentFlag.AlignCenter, f"{v:.0f}%")
        p.setFont(QFont("Arial", 9))
        p.setPen(QPen(QColor(C_MUTED)))
        p.drawText(QRectF(0, cy + 14, w, 16), Qt.AlignmentFlag.AlignCenter, self._accuracy_label)


# ══════════════════════════════════════════════════
class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rts = []; self._oks = []
        self.setMinimumHeight(72)
        self.setStyleSheet("background:transparent;")

    def set_data(self, rts, oks):
        self._rts = rts; self._oks = oks; self.update()

    def paintEvent(self, event):
        if not self._rts: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad = 14
        n = len(self._rts)
        mn, mx = min(self._rts), max(self._rts)
        rng = mx - mn if mx != mn else 1.0

        def px(i): return pad + (w - 2 * pad) * i / (n - 1) if n > 1 else w / 2
        def py(v): return (h - pad) - (h - 2 * pad) * (v - mn) / rng

        # Horizontal average line
        avg = sum(self._rts) / n
        p.setPen(QPen(QColor(C_FAINT), 1, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(pad, py(avg)), QPointF(w - pad, py(avg)))

        # Line
        p.setPen(QPen(QColor(C_SLATE), 1.5))
        for i in range(1, n):
            p.drawLine(QPointF(px(i - 1), py(self._rts[i - 1])),
                       QPointF(px(i),     py(self._rts[i])))

        # Dots
        for i, (rt, ok) in enumerate(zip(self._rts, self._oks)):
            col = QColor(C_SAGE) if ok else QColor(C_CORAL)
            p.setPen(QPen(QColor(C_CARD), 1.5))
            p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(px(i), py(rt)), 4.5, 4.5)


# ══════════════════════════════════════════════════
class TrialRow(QWidget):
    def __init__(self, trial, correct, rt, max_rt, avg_rt, parent=None):
        super().__init__(parent)
        self.trial = trial; self.correct = correct
        self.rt = rt; self.max_rt = max_rt; self.avg_rt = avg_rt
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        lw, gap, rw = 36, 8, 48
        bx = lw + gap
        bw = w - bx - rw - gap

        # Trial label
        p.setPen(QPen(QColor(C_MUTED)))
        p.setFont(QFont("Arial", 10))
        p.drawText(QRectF(0, 0, lw, h),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                   f"{self.trial}")

        # Track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(C_FAINT)))
        p.drawRoundedRect(QRectF(bx, h / 2 - 3.5, bw, 7), 3.5, 3.5)

        # Fill – softer pastel tint
        fill = max(7.0, bw * min(1.0, self.rt / self.max_rt if self.max_rt else 0))
        col = QColor(C_SAGE) if self.correct else QColor(C_CORAL)
        col.setAlpha(200)
        p.setBrush(QBrush(col))
        p.drawRoundedRect(QRectF(bx, h / 2 - 3.5, fill, 7), 3.5, 3.5)

        # RT label
        p.setPen(QPen(QColor(C_TEXT)))
        p.setFont(QFont("Arial", 10))
        p.drawText(QRectF(bx + bw + gap, 0, rw, h),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   f"{self.rt:.2f}s")


# ══════════════════════════════════════════════════
class Chip(QPushButton):
    _on  = f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:7px;font-size:11px;font-weight:700;border:1.5px solid {C_TEXT};}}"
    _off = f"QPushButton{{background:{C_CARD};color:{C_MUTED};border-radius:7px;font-size:11px;font-weight:500;border:1.5px solid {C_BORDER};}}QPushButton:hover{{color:{C_TEXT};border-color:#aaa;}}"

    def __init__(self, label, ext, parent=None):
        super().__init__(label, parent)
        self.ext = ext
        self.setCheckable(True)
        self.setFixedSize(68, 30)
        self.toggled.connect(lambda c: self.setStyleSheet(self._on if c else self._off))
        self.setStyleSheet(self._off)


# ══════════════════════════════════════════════════
class EndScreen(QWidget):
    def __init__(self, on_restart, back_callback, parent=None):
        super().__init__(parent)
        self.on_restart = on_restart
        self.back_callback = back_callback
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self._summary = None
        self._grp = QButtonGroup(self)
        self._grp.setExclusive(True)
        self._build()

    # ── helpers ──────────────────────────────────
    def _card(self):
        f = QFrame()
        f.setStyleSheet(f"QFrame{{background:{C_CARD};border-radius:16px;border:1px solid {C_BORDER};}}")
        f.setGraphicsEffect(shadow())
        return f

    def _mini_stat(self, value, label, dot_color):
        """Compact stat: coloured value + grey label, no border."""
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lo = QVBoxLayout(w); lo.setContentsMargins(8, 6, 8, 6); lo.setSpacing(2)

        vl = QLabel(value)
        vl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{dot_color};background:transparent;border:none")

        dl = QLabel(label)
        dl.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")

        lo.addWidget(vl); lo.addWidget(dl)
        w.vl = vl; w.dl = dl; w.dot = None
        return w

    def _label(self, text, size=11, bold=False, color="#666666"):
        l = QLabel(text)
        l.setFont(QFont("Arial", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        l.setStyleSheet(f"color:{color};background:transparent;letter-spacing:0.5px;border:none")
        return l

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background:{C_BORDER};border:none;max-height:1px;")
        return line

    def _vdiv(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet(f"background:{C_BORDER};border:none;max-width:1px;")
        return line

    # ── build ─────────────────────────────────────
    def _build(self):
        self.setStyleSheet(f"QWidget{{background:{C_BG};}}")
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)

        sc = QScrollArea(); sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sc.setStyleSheet(f"QScrollArea{{border:none;background:transparent;}}"
                         f"QScrollBar:vertical{{width:4px;background:transparent;}}"
                         f"QScrollBar::handle:vertical{{background:{C_FAINT};border-radius:2px;}}")

        body = QWidget(); body.setStyleSheet("background:transparent;")
        lo = QVBoxLayout(body); lo.setContentsMargins(52, 44, 52, 56); lo.setSpacing(20)

        # ── Title ───────────────────────────────
        self.title_lbl = QLabel(self._tr.t('dms.results_title'))
        self.title_lbl.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet(f"color:{C_TEXT};background:transparent;border:none")
        lo.addWidget(self.title_lbl)

        # ── Hero card: ring + stats ──────────────
        hero = self._card()
        hl = QHBoxLayout(hero); hl.setContentsMargins(28, 28, 28, 28); hl.setSpacing(32)

        self.ring = AccuracyRing()
        hl.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignVCenter)

        # Vertical divider
        vd = QFrame(); vd.setFrameShape(QFrame.Shape.VLine)
        vd.setStyleSheet(f"background:{C_BORDER};border:none;max-width:1px;")
        hl.addWidget(vd)

        # 2×2 stats grid — no borders, just coloured values
        grid = QVBoxLayout(); grid.setSpacing(0)
        self.s_correct = self._mini_stat("—", self._tr.t('dms.correct_total'), C_SAGE)
        self.s_avg     = self._mini_stat("—", self._tr.t('dms.avg_rt_lbl'),           C_SLATE)
        self.s_fast    = self._mini_stat("—", self._tr.t('dms.fastest_rt_lbl'),       C_LAVEND)
        self.s_slow    = self._mini_stat("—", self._tr.t('dms.slowest_rt_lbl'),       C_AMBER)
        row1 = QHBoxLayout(); row1.setSpacing(0)
        row2 = QHBoxLayout(); row2.setSpacing(0)
        row1.addWidget(self.s_correct, 1); row1.addWidget(self._vdiv()); row1.addWidget(self.s_avg, 1)
        row2.addWidget(self.s_fast, 1);    row2.addWidget(self._vdiv()); row2.addWidget(self.s_slow, 1)
        grid.addLayout(row1); grid.addWidget(self._divider()); grid.addLayout(row2)
        hl.addLayout(grid, 1)
        lo.addWidget(hero)

        # ── Advanced metrics card ────────────────
        adv = self._card()
        al = QVBoxLayout(adv); al.setContentsMargins(24, 20, 24, 20); al.setSpacing(14)
        self.lbl_adv = self._label(self._tr.t('dms.section_advanced'), 11, True, C_TEXT)
        al.addWidget(self.lbl_adv)
        arow = QHBoxLayout(); arow.setSpacing(0)
        self.s_median  = self._mini_stat("—", self._tr.t('dms.median_rt'),       C_TEAL)
        self.s_std     = self._mini_stat("—", self._tr.t('dms.std_rt'),      C_STONE)
        self.s_consist = self._mini_stat("—", self._tr.t('dms.consistency'),     C_MINT)
        self.s_learn   = self._mini_stat("—", self._tr.t('dms.learning_effect'), C_ROSE)
        for i, w in enumerate((self.s_median, self.s_std, self.s_consist, self.s_learn)):
            arow.addWidget(w, 1)
            if i < 3:
                vd2 = QFrame(); vd2.setFrameShape(QFrame.Shape.VLine)
                vd2.setStyleSheet(f"background:{C_BORDER};border:none;max-width:1px;")
                arow.addWidget(vd2)
        al.addLayout(arow)
        lo.addWidget(adv)

        # ── Sparkline card ───────────────────────
        spark_card = self._card()
        sl = QVBoxLayout(spark_card); sl.setContentsMargins(24, 18, 24, 18); sl.setSpacing(10)
        shdr = QHBoxLayout()
        self.lbl_trend = self._label(self._tr.t('dms.section_trend'), 11, True, C_TEXT)
        shdr.addWidget(self.lbl_trend)
        shdr.addStretch()
        self.spark_legends = []
        for col, key in [(C_SAGE, 'dms.legend_correct'), (C_CORAL, 'dms.legend_wrong'), (C_SLATE, 'dms.legend_rt_line')]:
            d = QLabel("—"); d.setStyleSheet(f"color:{col};background:transparent;font-size:11px;font-weight:700;border:none")
            t = QLabel(self._tr.t(key)); t.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
            self.spark_legends.append((t, key))
            shdr.addWidget(d); shdr.addWidget(t); shdr.addSpacing(10)
        sl.addLayout(shdr)
        self.sparkline = Sparkline()
        sl.addWidget(self.sparkline)
        lo.addWidget(spark_card)

        # ── Trial bars card ──────────────────────
        bars_card = self._card()
        bl = QVBoxLayout(bars_card); bl.setContentsMargins(24, 18, 24, 18); bl.setSpacing(10)
        bhdr = QHBoxLayout()
        self.lbl_trials = self._label(self._tr.t('dms.section_trials'), 11, True, C_TEXT)
        bhdr.addWidget(self.lbl_trials)
        bhdr.addStretch()
        self.trial_legends = []
        for col, key in [(C_SAGE, 'dms.legend_correct'), (C_CORAL, 'dms.legend_wrong')]:
            d = QLabel("●"); d.setStyleSheet(f"color:{col};background:transparent;font-size:10px;border:none")
            t = QLabel(self._tr.t(key)); t.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
            self.trial_legends.append((t, key))
            bhdr.addWidget(d); bhdr.addWidget(t); bhdr.addSpacing(10)
        bl.addLayout(bhdr)
        self.bars_w = QWidget(); self.bars_w.setStyleSheet("background:transparent;")
        self.bars_lo = QVBoxLayout(self.bars_w)
        self.bars_lo.setSpacing(3); self.bars_lo.setContentsMargins(0, 0, 0, 0)
        bl.addWidget(self.bars_w)
        lo.addWidget(bars_card)

        # ── Export card ──────────────────────────
        exp_card = self._card()
        exl = QVBoxLayout(exp_card); exl.setContentsMargins(24, 20, 24, 20); exl.setSpacing(12)
        self.lbl_export = self._label(self._tr.t('dms.export_title'), 11, True, C_TEXT)
        exl.addWidget(self.lbl_export)
        self.exp_hint = QLabel(self._tr.t('dms.export_hint'))
        self.exp_hint.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
        exl.addWidget(self.exp_hint)

        fmt_row = QHBoxLayout(); fmt_row.setSpacing(6)
        self.b_csv  = Chip("CSV",  "csv")
        self.b_json = Chip("JSON", "json")
        self.b_txt  = Chip("TXT",  "txt")
        # self.b_pdf  = Chip("PDF",  "pdf")  # does not work
        self.b_csv.setChecked(True)
        for b in (self.b_csv, self.b_json, self.b_txt):
            self._grp.addButton(b); fmt_row.addWidget(b)
        fmt_row.addStretch()

        self.save_btn = QPushButton(self._tr.t('dms.save_report'))
        self.save_btn.setFont(QFont("Arial", 11))
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedHeight(34)
        self.save_btn.setStyleSheet(
            f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:8px;padding:0 20px;font-size:11px;font-weight:600;}}"
            f"QPushButton:hover{{background:#444;}}")
        self.save_btn.clicked.connect(self._save)
        fmt_row.addWidget(self.save_btn)
        exl.addLayout(fmt_row)
        lo.addWidget(exp_card)

        # ── Action buttons ───────────────────────
        br = QHBoxLayout(); br.setSpacing(10); br.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.restart_btn = QPushButton(self._tr.t('dms.restart'))
        self.back_btn    = QPushButton(self._tr.t('dms.back_main_menu'))
        self.restart_btn.setStyleSheet(
            f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:12px;padding:0 28px;font-size:13px;font-weight:600;}}"
            f"QPushButton:hover{{background:#444;}}")
        self.back_btn.setStyleSheet(
            f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:12px;padding:0 28px;font-size:13px;font-weight:600;}}"
            f"QPushButton:hover{{background:#444;}}")
        for b in (self.restart_btn, self.back_btn):
            b.setFont(QFont("Arial", 13)); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(46); b.setMinimumWidth(160); br.addWidget(b)
        self.restart_btn.clicked.connect(self.on_restart)
        self.back_btn.clicked.connect(self.back_callback)
        lo.addLayout(br)

        sc.setWidget(body); outer.addWidget(sc)

    # ── populate ──────────────────────────────────
    def set_results(self, s: dict):
        self._summary = s
        self.ring.animate(s['accuracy'])
        self.s_correct.vl.setText(f"{s['correct_count']} / {s['total']}")
        self.s_avg.vl.setText(f"{s['avg_rt']:.2f} s")
        self.s_fast.vl.setText(f"{s['min_rt']:.2f} s")
        self.s_slow.vl.setText(f"{s['max_rt']:.2f} s")
        self.s_median.vl.setText(f"{s['median_rt']:.2f} s")
        self.s_std.vl.setText(f"{s['std_rt']:.2f} s")
        self.s_consist.vl.setText(f"{s['consistency']:.0f}%")
        delta = s['second_half_accuracy'] - s['first_half_accuracy']
        sign = "▲" if delta >= 0 else "▼"
        self.s_learn.vl.setText(f"{sign} {abs(delta):.0f}%")
        col = C_SAGE if delta >= 0 else C_CORAL
        self.s_learn.vl.setStyleSheet(f"color:{col};background:transparent;font-size:15px;font-weight:700;border:none")

        rts = [r.rt for r in s['results']]
        oks = [r.correct for r in s['results']]
        self.sparkline.set_data(rts, oks)

        while self.bars_lo.count():
            item = self.bars_lo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        mx = s['max_rt'] if s['max_rt'] > 0 else 1.0
        avg = s['avg_rt']
        for r in s['results']:
            self.bars_lo.addWidget(TrialRow(r.trial, r.correct, r.rt, mx, avg))

    # ── export ────────────────────────────────────
    def _save(self):
        if not self._summary: return
        checked = self._grp.checkedButton()
        if not isinstance(checked, Chip): return
        ext = checked.ext
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self, self._tr.t('dms.save_report'), f"dms_results_{ts}.{ext}",
            f"{ext.upper()} Files (*.{ext});;All Files (*)")
        if not path: return
        try:
            {"csv": self._csv, "json": self._json, "txt": self._txt, "pdf": self._pdf}[ext](path)
            self.save_btn.setText("✓  " + self._tr.t('dms.saved'))
            QTimer.singleShot(2500, lambda: self.save_btn.setText(self._tr.t('dms.save_report')))
        except Exception as e:
            self.save_btn.setText("⚠  Error")
            QTimer.singleShot(3000, lambda: self.save_btn.setText(self._tr.t('dms.save_report')))

    def _csv(self, path):
        s = self._summary
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["DMS Test Results"])
            w.writerow(["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]); w.writerow([])
            for k, v in [
                ("total_trials", s['total']), ("correct", s['correct_count']),
                ("wrong", s['wrong_count']), ("accuracy_%", f"{s['accuracy']:.2f}"),
                ("avg_rt_s", f"{s['avg_rt']:.3f}"), ("median_rt_s", f"{s['median_rt']:.3f}"),
                ("std_rt_s", f"{s['std_rt']:.3f}"), ("min_rt_s", f"{s['min_rt']:.3f}"),
                ("max_rt_s", f"{s['max_rt']:.3f}"), ("consistency_%", f"{s['consistency']:.1f}"),
                ("first_half_acc_%", f"{s['first_half_accuracy']:.1f}"),
                ("second_half_acc_%", f"{s['second_half_accuracy']:.1f}"),
            ]: w.writerow([k, v])
            w.writerow([]); w.writerow(["trial", "result", "rt_s"])
            for r in s['results']:
                w.writerow([r.trial, "correct" if r.correct else "wrong", f"{r.rt:.3f}"])

    def _json(self, path):
        s = self._summary
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "test": "DMS", "date": datetime.now().isoformat(),
                "summary": {
                    "total": s['total'], "correct": s['correct_count'], "wrong": s['wrong_count'],
                    "accuracy_pct": round(s['accuracy'], 2),
                    "avg_rt_s": round(s['avg_rt'], 3), "median_rt_s": round(s['median_rt'], 3),
                    "std_rt_s": round(s['std_rt'], 3), "min_rt_s": round(s['min_rt'], 3),
                    "max_rt_s": round(s['max_rt'], 3), "consistency_pct": round(s['consistency'], 1),
                    "first_half_accuracy_pct": round(s['first_half_accuracy'], 1),
                    "second_half_accuracy_pct": round(s['second_half_accuracy'], 1),
                },
                "trials": [{"trial": r.trial, "correct": r.correct, "rt_s": round(r.rt, 3)}
                           for r in s['results']]
            }, f, indent=2, ensure_ascii=False)

    def _txt(self, path):
        s = self._summary
        delta = s['second_half_accuracy'] - s['first_half_accuracy']
        sep = "─" * 46
        lines = [
            "╔══════════════════════════════════════════════╗",
            "║          DMS TEST RESULTS REPORT             ║",
            "╚══════════════════════════════════════════════╝",
            f"  Date : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}",
            "", "  SUMMARY", f"  {sep}",
            f"  Total trials    : {s['total']}",
            f"  Correct         : {s['correct_count']}",
            f"  Wrong           : {s['wrong_count']}",
            f"  Accuracy        : {s['accuracy']:.1f}%",
            "", "  REACTION TIMES", f"  {sep}",
            f"  Average         : {s['avg_rt']:.3f} s",
            f"  Median          : {s['median_rt']:.3f} s",
            f"  Std deviation   : {s['std_rt']:.3f} s",
            f"  Fastest         : {s['min_rt']:.3f} s",
            f"  Slowest         : {s['max_rt']:.3f} s",
            "", "  ADVANCED", f"  {sep}",
            f"  Consistency     : {s['consistency']:.0f}%",
            f"  1st half acc.   : {s['first_half_accuracy']:.0f}%",
            f"  2nd half acc.   : {s['second_half_accuracy']:.0f}%",
            f"  Learning effect : {'+' if delta>=0 else ''}{delta:.0f}%",
            "", "  TRIALS", f"  {sep}",
            f"  {'#':<5}  {'Result':<10}  {'RT (s)':>7}  {'vs avg':>7}",
            f"  {sep}",
        ]
        for r in s['results']:
            diff = r.rt - s['avg_rt']
            lines.append(f"  {r.trial:<5}  {'✓ correct' if r.correct else '✗ wrong':<10}  {r.rt:>7.3f}  {diff:>+7.3f}")
        lines.append(f"  {sep}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")

    def _pdf(self, path):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas as rl_canvas

        s = self._summary
        W, H = A4
        c = rl_canvas.Canvas(path, pagesize=A4)
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

        # Palette
        CREAM  = colors.HexColor("#f9f7f4")
        WHITE  = colors.white
        DARK   = colors.HexColor("#2c2825")
        MUTED  = colors.HexColor("#9a9590")
        FAINT  = colors.HexColor("#ede9e3")
        SAGE   = colors.HexColor("#7aab93")
        CORAL  = colors.HexColor("#d4796a")
        SLATE  = colors.HexColor("#7b96b2")
        LAVEND = colors.HexColor("#9b8fc4")
        AMBER  = colors.HexColor("#c9953a")
        TEAL   = colors.HexColor("#5fa8a0")
        STONE  = colors.HexColor("#8a8a8a")
        MINT   = colors.HexColor("#6aab8e")
        ROSE   = colors.HexColor("#c47a8a")

        def rr(x, y, w, h, r=6, fill=WHITE, stroke_col=None):
            c.saveState()
            c.setFillColor(fill)
            if stroke_col:
                c.setStrokeColor(stroke_col); c.setLineWidth(0.4)
            else:
                c.setLineWidth(0)
            c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke_col else 0)
            c.restoreState()

        def txt(x, y, s_, size=9, bold=False, col=DARK, align="left"):
            c.saveState(); c.setFillColor(col)
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            if align == "center": c.drawCentredString(x, y, s_)
            elif align == "right": c.drawRightString(x, y, s_)
            else: c.drawString(x, y, s_)
            c.restoreState()

        def stat_block(x, y, w, h, value, label, dot_col):
            rr(x, y, w, h, fill=WHITE, stroke_col=FAINT)
            c.saveState(); c.setFillColor(dot_col)
            c.circle(x + 10, y + h - 12, 3, fill=1, stroke=0)
            c.restoreState()
            txt(x + 18, y + h - 16, value, 12, True, DARK)
            txt(x + 18, y + 6,      label,  7, False, MUTED)

        # Background
        c.setFillColor(CREAM); c.rect(0, 0, W, H, fill=1, stroke=0)

        # Header
        rr(0, H - 52, W, 52, r=0, fill=DARK)
        txt(W / 2, H - 28, "DMS TEST RESULTS", 16, True, WHITE, "center")
        txt(W / 2, H - 42, now_str, 7, False, MUTED, "center")

        y = H - 68
        M = 36  # margin
        IW = W - 2 * M  # inner width

        # Accuracy ring
        ring_cx = M + 46; ring_cy = y - 52; ring_r = 36
        acc = s['accuracy']
        ring_col = SAGE if acc >= 80 else (AMBER if acc >= 50 else CORAL)

        rr(M, y - 104, 104, 104, fill=WHITE, stroke_col=FAINT)
        c.saveState(); c.setStrokeColor(FAINT); c.setLineWidth(7)
        c.circle(ring_cx, ring_cy, ring_r, fill=0, stroke=1); c.restoreState()

        import math as _m
        steps = max(2, int(acc / 100 * 72))
        c.saveState(); c.setStrokeColor(ring_col); c.setLineWidth(7)
        for i in range(steps):
            a0 = _m.radians(90 - 360 * i / 72)
            a1 = _m.radians(90 - 360 * (i + 1) / 72)
            c.line(ring_cx + ring_r * _m.cos(a0), ring_cy + ring_r * _m.sin(a0),
                   ring_cx + ring_r * _m.cos(a1), ring_cy + ring_r * _m.sin(a1))
        c.restoreState()
        txt(ring_cx, ring_cy - 6,  f"{acc:.0f}%", 16, True,  DARK,  "center")
        txt(ring_cx, ring_cy - 17, self._tr.t('dms.accuracy_label'),     7, False, MUTED, "center")

        # 4 primary stats
        sw = (IW - 108 - 12) / 4
        sx0 = M + 112
        for i, (val, lbl, col) in enumerate([
            (f"{s['correct_count']}/{s['total']}", self._tr.t('dms.correct_total'), SAGE),
            (f"{s['avg_rt']:.2f} s",               self._tr.t('dms.avg_rt_lbl'),          SLATE),
            (f"{s['min_rt']:.2f} s",               self._tr.t('dms.fastest_rt_lbl'),      LAVEND),
            (f"{s['max_rt']:.2f} s",               self._tr.t('dms.slowest_rt_lbl'),      AMBER),
        ]):
            stat_block(sx0 + i * (sw + 4), y - 104, sw, 48, val, lbl, col)

        y -= 116

        # Advanced metrics
        rr(M, y - 52, IW, 52, fill=WHITE, stroke_col=FAINT)
        txt(M + 8, y - 12, "ADVANCED METRICS", 7, True, MUTED)
        aw = IW / 6
        delta = s['second_half_accuracy'] - s['first_half_accuracy']
        adv = [
            (f"{s['median_rt']:.2f} s",  self._tr.t('dms.median_rt'),       TEAL),
            (f"{s['std_rt']:.2f} s",     self._tr.t('dms.std_rt'),      STONE),
            (f"{s['consistency']:.0f}%", self._tr.t('dms.consistency'),     MINT),
            (f"{'+' if delta>=0 else ''}{delta:.0f}%", self._tr.t('dms.learning_effect'), SAGE if delta >= 0 else CORAL),
            (f"{s['first_half_accuracy']:.0f}%",  "1st Half",  SLATE),
            (f"{s['second_half_accuracy']:.0f}%", "2nd Half",  LAVEND),
        ]
        for i, (val, lbl, col) in enumerate(adv):
            ax = M + i * aw + aw / 2
            if i > 0:
                c.saveState(); c.setStrokeColor(FAINT); c.setLineWidth(0.4)
                c.line(M + i * aw, y - 46, M + i * aw, y - 8); c.restoreState()
            txt(ax, y - 28, val, 13, True,  col,  "center")
            txt(ax, y - 43, lbl,  8, False, MUTED, "center")

        y -= 64

        # RT bar chart
        rr(M, y - 118, IW, 118, fill=WHITE, stroke_col=FAINT)
        txt(M + 8, y - 12, "REACTION TIME - TRIAL BY TRIAL", 7, True, MUTED)

        results = s['results']
        n = len(results)
        max_rt = s['max_rt'] if s['max_rt'] > 0 else 1.0
        bx0 = M + 24; bw_ = IW - 80; bh = 7
        gap_ = min(13, (100 / max(1, n)))

        for i, r in enumerate(results):
            by = y - 28 - i * (bh + gap_)
            if by < y - 114: break
            fw = max(5, bw_ * r.rt / max_rt)
            c.setFillColor(FAINT); c.roundRect(bx0, by, bw_, bh, 3, fill=1, stroke=0)
            col_ = SAGE if r.correct else CORAL
            c.setFillColor(col_); c.roundRect(bx0, by, fw, bh, 3, fill=1, stroke=0)
            txt(bx0 - 4, by + 1, f"#{r.trial}", 6, False, MUTED, "right")
            txt(bx0 + fw + 4, by + 1, f"{r.rt:.2f}s", 6, False, STONE)

        y -= 130

        # Trial table
        if y > 80:
            cols = [M, M + 30, M + 100, M + 190, M + 280]
            rh = 14
            rr(M, y - rh, IW, rh, fill=DARK)
            for cx_, hd in zip(cols, ["#", "Result", "RT (s)", "vs Avg", ""]):
                txt(cx_ + 3, y - rh + 4, hd, 7, True, WHITE)

            for ri, r in enumerate(results):
                ry = y - rh - (ri + 1) * rh
                if ry < 30: break
                bg = colors.HexColor("#f0f8f4") if r.correct else colors.HexColor("#fdf2f1")
                rr(M, ry, IW, rh, fill=bg)
                diff = r.rt - s['avg_rt']
                fc_diff = SAGE if diff <= 0 else CORAL
                for cx_, v, fc in [
                    (cols[0], str(r.trial),                              MUTED),
                    (cols[1], "✓ correct" if r.correct else "✗ wrong",  SAGE if r.correct else CORAL),
                    (cols[2], f"{r.rt:.3f}",                             DARK),
                    (cols[3], f"{diff:+.3f}",                            fc_diff),
                ]:
                    txt(cx_ + 3, ry + 4, v, 7, False, fc)

        # Footer
        txt(W / 2, 18, f"Cognitive Function Assessment Suite  ·  {now_str}", 6, False, MUTED, "center")

        c.save()

    # ── i18n ──────────────────────────────────────
    def retranslate(self, lang=None):
        tr = self._tr.t
        widgets = [
            (self.title_lbl,      'dms.results_title'),
            (self.restart_btn,    'dms.restart'),
            (self.back_btn,       'dms.back_main_menu'),
            (self.save_btn,       'dms.save_report'),
            (self.exp_hint,       'dms.export_hint'),
            (self.lbl_adv,        'dms.section_advanced'),
            (self.lbl_trend,      'dms.section_trend'),
            (self.lbl_trials,     'dms.section_trials'),
            (self.lbl_export,     'dms.export_title'),
            (self.s_correct.dl,   'dms.correct_total'),
            (self.s_avg.dl,       'dms.avg_rt_lbl'),
            (self.s_fast.dl,      'dms.fastest_rt_lbl'),
            (self.s_slow.dl,      'dms.slowest_rt_lbl'),
            (self.s_median.dl,    'dms.median_rt'),
            (self.s_std.dl,       'dms.std_rt'),
            (self.s_consist.dl,   'dms.consistency'),
            (self.s_learn.dl,     'dms.learning_effect'),
        ]
        for widget, key in widgets:
            widget.setText(tr(key))
        self.ring._accuracy_label = tr('dms.accuracy_label')
        self.ring.update()
        for lbl, key in self.spark_legends:
            lbl.setText(tr(key))
        for lbl, key in self.trial_legends:
            lbl.setText(tr(key))