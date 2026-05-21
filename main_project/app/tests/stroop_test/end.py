import csv
import json
import math
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QHBoxLayout,
    QFrame, QScrollArea, QButtonGroup, QFileDialog, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QPointF

from app.translations import get_translator

# ── Palette (same warm cream as DMS) ──────────────
C_BG     = "#fffbf0"
C_CARD   = "#ffffff"
C_BORDER = "#f0e8d0"
C_TEXT   = "#2c2825"
C_MUTED  = "#9a9590"
C_FAINT  = "#f0ebe0"

# Stroop-specific colours
C_CONG   = "#5b8fd4"   # congruent  (blue — "easy")
C_INCONG = "#e09a30"   # incongruent (coral — "hard")
C_INTER  = "#d95878"   # interference
C_GOOD   = "#4dab83"   # correct
C_WRONG  = "#e06058"   # wrong
C_AMBER  = "#e09a30"
C_LAVEND = "#8b7ad9"
C_TEAL   = "#35b8ae"
C_STONE  = "#8a96a8"
C_MINT   = "#40c48a"


def _shadow():
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(20); sh.setOffset(0, 2); sh.setColor(QColor(0,0,0,12))
    return sh


# ══════════════════════════════════════════════════
class AccuracyRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._v = 0.0
        self._label = "accuracy"
        self.setFixedSize(200, 200)
        self.setStyleSheet("background:transparent;")
        self._anim = QPropertyAnimation(self, b"v")
        self._anim.setDuration(1300); self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def animate(self, target):
        self._anim.setStartValue(0.0); self._anim.setEndValue(float(target)); self._anim.start()

    @pyqtProperty(float)
    def v(self): return self._v

    @v.setter
    def v(self, val): self._v = val; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2; r = min(w,h)/2 - 20
        pen = QPen(QColor(C_FAINT), 10); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))
        v = self._v
        arc_col = C_GOOD if v >= 80 else (C_AMBER if v >= 50 else C_WRONG)
        pen2 = QPen(QColor(arc_col), 10); pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2); p.drawArc(QRectF(cx-r, cy-r, r*2, r*2), 90*16, -int(v/100*360*16))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#fdfcf8")))
        p.drawEllipse(QRectF(cx-r+14, cy-r+14, (r-14)*2, (r-14)*2))
        p.setPen(QPen(QColor(C_TEXT))); p.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        p.drawText(QRectF(0, cy-22, w, 34), Qt.AlignmentFlag.AlignCenter, f"{v:.0f}%")
        p.setFont(QFont("Arial", 9)); p.setPen(QPen(QColor(C_MUTED)))
        p.drawText(QRectF(0, cy+14, w, 16), Qt.AlignmentFlag.AlignCenter, self._label)


# ══════════════════════════════════════════════════
class InterferenceBar(QWidget):
    """Horizontal bar showing congruent RT vs incongruent RT side by side."""
    def __init__(self, rt_cong, rt_incong, parent=None):
        super().__init__(parent)
        self.rt_cong = rt_cong; self.rt_incong = rt_incong
        self.setFixedHeight(52); self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        mx = max(self.rt_cong, self.rt_incong, 0.001)
        bh, pad = 16, 4
        bar_w = w - 80

        for i, (rt, col, label) in enumerate([
            (self.rt_cong,   C_CONG,   "Congruent"),
            (self.rt_incong, C_INCONG, "Incongruent"),
        ]):
            y = pad + i * (bh + pad*2)
            fill = max(8, bar_w * rt / mx)
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor(C_FAINT)))
            p.drawRoundedRect(QRectF(0, y, bar_w, bh), bh/2, bh/2)
            p.setBrush(QBrush(QColor(col)))
            p.drawRoundedRect(QRectF(0, y, fill, bh), bh/2, bh/2)
            p.setPen(QPen(QColor(C_TEXT))); p.setFont(QFont("Arial", 9))
            p.drawText(QRectF(bar_w+6, y, 74, bh), Qt.AlignmentFlag.AlignVCenter, f"{rt:.2f}s")


# ══════════════════════════════════════════════════
class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []; self._congs = []; self._oks = []
        self.setMinimumHeight(72); self.setStyleSheet("background:transparent;")

    def set_data(self, rts, congs, oks):
        self._data = rts; self._congs = congs; self._oks = oks; self.update()

    def paintEvent(self, event):
        if not self._data: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height(); pad = 14
        n = len(self._data); mn, mx = min(self._data), max(self._data)
        rng = mx - mn if mx != mn else 1.0
        def px(i): return pad + (w-2*pad)*i/(n-1) if n>1 else w/2
        def py(v): return (h-pad) - (h-2*pad)*(v-mn)/rng
        avg = sum(self._data)/n
        p.setPen(QPen(QColor(C_FAINT), 1, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(pad, py(avg)), QPointF(w-pad, py(avg)))
        p.setPen(QPen(QColor(C_STONE), 1.5))
        for i in range(1, n):
            p.drawLine(QPointF(px(i-1), py(self._data[i-1])), QPointF(px(i), py(self._data[i])))
        for i, (rt, cong, ok) in enumerate(zip(self._data, self._congs, self._oks)):
            col = QColor(C_CONG) if cong else QColor(C_INCONG)
            if not ok: col = QColor(C_WRONG)
            p.setPen(QPen(QColor(C_CARD), 1.5)); p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(px(i), py(rt)), 4.5, 4.5)


# ══════════════════════════════════════════════════
class TrialRow(QWidget):
    def __init__(self, trial, congruent, correct, rt, max_rt, parent=None):
        super().__init__(parent)
        self.trial = trial; self.congruent = congruent
        self.correct = correct; self.rt = rt; self.max_rt = max_rt
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        lw, gap, rw = 36, 8, 48
        bx = lw+gap; bw = w-bx-rw-gap
        p.setPen(QPen(QColor(C_MUTED))); p.setFont(QFont("Arial", 10))
        p.drawText(QRectF(0,0,lw,h), Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignRight, f"{self.trial}")
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor(C_FAINT)))
        p.drawRoundedRect(QRectF(bx, h/2-3.5, bw, 7), 3.5, 3.5)
        fill = max(7.0, bw*min(1.0, self.rt/self.max_rt if self.max_rt else 0))
        col = QColor(C_CONG if self.congruent else C_INCONG)
        if not self.correct: col = QColor(C_WRONG)
        col.setAlpha(200)
        p.setBrush(QBrush(col))
        p.drawRoundedRect(QRectF(bx, h/2-3.5, fill, 7), 3.5, 3.5)
        p.setPen(QPen(QColor(C_TEXT))); p.setFont(QFont("Arial", 10))
        p.drawText(QRectF(bx+bw+gap, 0, rw, h), Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft, f"{self.rt:.2f}s")


# ══════════════════════════════════════════════════
class Chip(QPushButton):
    _on  = f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:7px;font-size:11px;font-weight:700;border:1.5px solid {C_TEXT};}}"
    _off = f"QPushButton{{background:{C_CARD};color:{C_MUTED};border-radius:7px;font-size:11px;font-weight:500;border:1.5px solid {C_BORDER};}}QPushButton:hover{{color:{C_TEXT};border-color:#aaa;}}"
    def __init__(self, label, ext, parent=None):
        super().__init__(label, parent); self.ext = ext
        self.setCheckable(True); self.setFixedSize(68, 30)
        self.toggled.connect(lambda c: self.setStyleSheet(self._on if c else self._off))
        self.setStyleSheet(self._off)


# ══════════════════════════════════════════════════
class EndScreen(QWidget):
    def __init__(self, back_callback, on_restart, parent=None):
        super().__init__(parent)
        self.back_callback = back_callback
        self.on_restart = on_restart
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self._summary = None
        self._grp = QButtonGroup(self); self._grp.setExclusive(True)
        self._build()

    def _card(self):
        f = QFrame()
        f.setStyleSheet(f"QFrame{{background:{C_CARD};border-radius:16px;border:1px solid {C_BORDER};}}")
        f.setGraphicsEffect(_shadow()); return f

    def _mini_stat(self, value, label, color):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        w.setMinimumSize(100, 64)
        lo = QVBoxLayout(w); lo.setContentsMargins(12,10,12,10); lo.setSpacing(4)
        lo.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        vl = QLabel(value); vl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color};background:transparent;border:none")
        vl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        dl = QLabel(label); dl.setWordWrap(True)
        dl.setStyleSheet(f"color:{C_MUTED};font-size:10px;background:transparent;border:none")
        dl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        lo.addWidget(vl); lo.addWidget(dl)
        w.vl = vl; w.dl = dl; return w

    def _label(self, text, size=11, bold=False, color="#555555"):
        l = QLabel(text); l.setFont(QFont("Arial", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        l.setStyleSheet(f"color:{color};background:transparent;border:none"); return l

    def _divider(self):
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"background:{C_BORDER};border:none;max-height:1px;"); return f

    def _vdiv(self):
        f = QFrame(); f.setFrameShape(QFrame.Shape.VLine)
        f.setStyleSheet(f"background:{C_BORDER};border:none;max-width:1px;"); return f

    def _build(self):
        self.setStyleSheet(f"QWidget{{background:{C_BG};}}")
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        sc = QScrollArea(); sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sc.setStyleSheet(f"QScrollArea{{border:none;background:transparent;}}"
                         f"QScrollBar:vertical{{width:4px;background:transparent;}}"
                         f"QScrollBar::handle:vertical{{background:{C_FAINT};border-radius:2px;}}")
        body = QWidget(); body.setStyleSheet("background:transparent;")
        lo = QVBoxLayout(body); lo.setContentsMargins(52,44,52,56); lo.setSpacing(20)

        # Title
        self.title_lbl = QLabel(self._tr.t('stroop.results_title'))
        self.title_lbl.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet(f"color:{C_TEXT};background:transparent;border:none")
        lo.addWidget(self.title_lbl)

        # Hero: ring card left + stats card right (two separate cards)
        hero_row = QHBoxLayout(); hero_row.setSpacing(16)

        ring_card = self._card()
        ring_card.setFixedSize(200, 200)
        rl = QVBoxLayout(ring_card); rl.setContentsMargins(16,16,16,16)
        rl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ring = AccuracyRing()
        self.ring.setFixedSize(168, 168)
        rl.addWidget(self.ring)
        hero_row.addWidget(ring_card, 0)

        self.s_acc_cong   = self._mini_stat("—", self._tr.t('stroop.lbl_acc_cong'),   C_CONG)
        self.s_acc_incong = self._mini_stat("—", self._tr.t('stroop.lbl_acc_incong'),  C_INCONG)
        self.s_rt_cong    = self._mini_stat("—", self._tr.t('stroop.lbl_rt_cong'),     C_CONG)
        self.s_rt_incong  = self._mini_stat("—", self._tr.t('stroop.lbl_rt_incong'),   C_INCONG)

        stats_card = self._card()
        sl = QVBoxLayout(stats_card); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)
        top_row = QHBoxLayout(); top_row.setSpacing(0); top_row.setContentsMargins(0,0,0,0)
        bot_row = QHBoxLayout(); bot_row.setSpacing(0); bot_row.setContentsMargins(0,0,0,0)
        top_row.addWidget(self.s_acc_cong, 1)
        top_row.addWidget(self._vdiv())
        top_row.addWidget(self.s_acc_incong, 1)
        bot_row.addWidget(self.s_rt_cong, 1)
        bot_row.addWidget(self._vdiv())
        bot_row.addWidget(self.s_rt_incong, 1)
        sl.addLayout(top_row, 1)
        sl.addWidget(self._divider())
        sl.addLayout(bot_row, 1)
        hero_row.addWidget(stats_card, 1)
        lo.addLayout(hero_row)

        # Interference card — highlight of the test
        inter_card = self._card()
        il = QVBoxLayout(inter_card); il.setContentsMargins(24,20,24,20); il.setSpacing(14)
        self.lbl_inter_title = self._label(self._tr.t('stroop.section_interference'), 11, True, C_TEXT)
        il.addWidget(self.lbl_inter_title)
        irow = QHBoxLayout(); irow.setSpacing(0)
        self.s_inter_rt  = self._mini_stat("—", self._tr.t('stroop.lbl_inter_rt'),   C_INTER)
        self.s_inter_pct = self._mini_stat("—", self._tr.t('stroop.lbl_stroop_pct'), C_AMBER)
        self.s_ig        = self._mini_stat("—", self._tr.t('stroop.lbl_ig'),          C_LAVEND)
        self.s_err_inter = self._mini_stat("—", self._tr.t('stroop.lbl_err_inter'),   C_WRONG)
        for i, w in enumerate((self.s_inter_rt, self.s_inter_pct, self.s_ig, self.s_err_inter)):
            irow.addWidget(w,1)
            if i < 3: irow.addWidget(self._vdiv())
        il.addLayout(irow)
        lo.addWidget(inter_card)

        # RT comparison bars
        rt_card = self._card()
        rl = QVBoxLayout(rt_card); rl.setContentsMargins(24,18,24,18); rl.setSpacing(10)
        rhdr = QHBoxLayout()
        self.lbl_rt_title = self._label(self._tr.t('stroop.section_rt_comparison'), 11, True, C_TEXT)
        rhdr.addWidget(self.lbl_rt_title); rhdr.addStretch()
        for col, key in [(C_CONG,'stroop.lbl_congruent'),(C_INCONG,'stroop.lbl_incongruent')]:
            d = QLabel("●"); d.setStyleSheet(f"color:{col};background:transparent;font-size:11px;border:none")
            t = QLabel(self._tr.t(key)); t.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
            rhdr.addWidget(d); rhdr.addWidget(t); rhdr.addSpacing(10)
        rl.addLayout(rhdr)
        self.inter_bars = InterferenceBar(0, 0)
        rl.addWidget(self.inter_bars)
        lo.addWidget(rt_card)

        # Sparkline
        spark_card = self._card()
        sl = QVBoxLayout(spark_card); sl.setContentsMargins(24,18,24,18); sl.setSpacing(10)
        shdr = QHBoxLayout()
        self.lbl_spark_title = self._label(self._tr.t('stroop.section_trend'), 11, True, C_TEXT)
        shdr.addWidget(self.lbl_spark_title); shdr.addStretch()
        self.spark_legends = []
        for col, key in [(C_CONG,'stroop.legend_cong'),(C_INCONG,'stroop.legend_incong'),(C_WRONG,'stroop.legend_wrong')]:
            d = QLabel("—"); d.setStyleSheet(f"color:{col};background:transparent;font-size:11px;font-weight:700;border:none")
            t = QLabel(self._tr.t(key)); t.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
            self.spark_legends.append((t, key))
            shdr.addWidget(d); shdr.addWidget(t); shdr.addSpacing(10)
        sl.addLayout(shdr)
        self.sparkline = Sparkline()
        sl.addWidget(self.sparkline)
        lo.addWidget(spark_card)

        # Trial bars
        bars_card = self._card()
        bl = QVBoxLayout(bars_card); bl.setContentsMargins(24,18,24,18); bl.setSpacing(10)
        bhdr = QHBoxLayout()
        self.lbl_trials_title = self._label(self._tr.t('stroop.section_trials'), 11, True, C_TEXT)
        bhdr.addWidget(self.lbl_trials_title); bhdr.addStretch()
        self.trial_legends = []
        for col, key in [(C_CONG,'stroop.legend_cong'),(C_INCONG,'stroop.legend_incong'),(C_WRONG,'stroop.legend_wrong')]:
            d = QLabel("●"); d.setStyleSheet(f"color:{col};background:transparent;font-size:10px;border:none")
            t = QLabel(self._tr.t(key)); t.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
            self.trial_legends.append((t, key))
            bhdr.addWidget(d); bhdr.addWidget(t); bhdr.addSpacing(10)
        bl.addLayout(bhdr)
        self.bars_w = QWidget(); self.bars_w.setStyleSheet("background:transparent;")
        self.bars_lo = QVBoxLayout(self.bars_w); self.bars_lo.setSpacing(3); self.bars_lo.setContentsMargins(0,0,0,0)
        bl.addWidget(self.bars_w)
        lo.addWidget(bars_card)

        # Export
        exp_card = self._card()
        exl = QVBoxLayout(exp_card); exl.setContentsMargins(24,20,24,20); exl.setSpacing(12)
        self.lbl_export = self._label(self._tr.t('stroop.export_title'), 11, True, C_TEXT)
        exl.addWidget(self.lbl_export)
        self.exp_hint = QLabel(self._tr.t('stroop.export_hint'))
        self.exp_hint.setStyleSheet(f"color:{C_MUTED};font-size:11px;background:transparent;border:none")
        exl.addWidget(self.exp_hint)
        fmt_row = QHBoxLayout(); fmt_row.setSpacing(6)
        self.b_csv  = Chip("CSV","csv"); self.b_json = Chip("JSON","json")
        self.b_txt  = Chip("TXT","txt"); self.b_pdf  = Chip("PDF","pdf")
        self.b_csv.setChecked(True)
        for b in (self.b_csv,self.b_json,self.b_txt,self.b_pdf):
            self._grp.addButton(b); fmt_row.addWidget(b)
        fmt_row.addStretch()
        self.save_btn = QPushButton(self._tr.t('stroop.save_report'))
        self.save_btn.setFont(QFont("Arial",11)); self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedHeight(34)
        self.save_btn.setStyleSheet(f"QPushButton{{background:{C_TEXT};color:#fff;border-radius:8px;padding:0 20px;font-size:11px;font-weight:600;}}QPushButton:hover{{background:#444;}}")
        self.save_btn.clicked.connect(self._save); fmt_row.addWidget(self.save_btn)
        exl.addLayout(fmt_row); lo.addWidget(exp_card)

        # Buttons
        br = QHBoxLayout(); br.setSpacing(10); br.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.restart_btn = QPushButton(self._tr.t('stroop.restart'))
        self.back_btn    = QPushButton(self._tr.t('stroop.back_main_menu'))
        for btn, ss in [(self.restart_btn, f"background:{C_TEXT};color:#fff;"), (self.back_btn, f"background:{C_TEXT};color:#fff;")]:
            btn.setStyleSheet(f"QPushButton{{{ss}border-radius:12px;padding:0 28px;font-size:13px;font-weight:600;}}QPushButton:hover{{background:#444;}}")
            btn.setFont(QFont("Arial",13)); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(46); btn.setMinimumWidth(160); br.addWidget(btn)
        self.restart_btn.clicked.connect(self.on_restart)
        self.back_btn.clicked.connect(self.back_callback)
        lo.addLayout(br)
        sc.setWidget(body); outer.addWidget(sc)

    def set_results(self, s: dict):
        self._summary = s
        self.ring.animate(s['accuracy'])
        self.s_acc_cong.vl.setText(f"{s['acc_congruent']:.0f}%")
        self.s_acc_incong.vl.setText(f"{s['acc_incongruent']:.0f}%")
        self.s_rt_cong.vl.setText(f"{s['avg_rt_congruent']:.2f} s")
        self.s_rt_incong.vl.setText(f"{s['avg_rt_incongruent']:.2f} s")

        ir = s['interference_rt']
        self.s_inter_rt.vl.setText(f"{ir:+.2f} s")
        col = C_WRONG if ir > 0 else C_GOOD
        self.s_inter_rt.vl.setStyleSheet(f"color:{col};background:transparent;font-size:18px;font-weight:700;")

        self.s_inter_pct.vl.setText(f"{s['stroop_effect_pct']:+.0f}%")
        self.s_ig.vl.setText(f"{s['ig_score']:.1f}")
        self.s_err_inter.vl.setText(f"{s['error_interference']:+.0f}%")

        self.inter_bars.rt_cong = s['avg_rt_congruent']
        self.inter_bars.rt_incong = s['avg_rt_incongruent']
        self.inter_bars.update()

        rts   = [t.rt for t in s['trials']]
        congs = [t.congruent for t in s['trials']]
        oks   = [t.correct for t in s['trials']]
        self.sparkline.set_data(rts, congs, oks)

        while self.bars_lo.count():
            item = self.bars_lo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        mx = max(rts) if rts else 1.0
        for t in s['trials']:
            self.bars_lo.addWidget(TrialRow(t.trial, t.congruent, t.correct, t.rt, mx))

    def _save(self):
        if not self._summary: return
        checked = self._grp.checkedButton()
        if not isinstance(checked, Chip): return
        ext = checked.ext
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self, self._tr.t('stroop.save_report'), f"stroop_results_{ts}.{ext}",
            f"{ext.upper()} Files (*.{ext});;All Files (*)")
        if not path: return
        try:
            {"csv":self._csv,"json":self._json,"txt":self._txt,"pdf":self._pdf}[ext](path)
            self.save_btn.setText("✓  " + self._tr.t('stroop.saved'))
            QTimer.singleShot(2500, lambda: self.save_btn.setText(self._tr.t('stroop.save_report')))
        except Exception:
            self.save_btn.setText("⚠  Error")
            QTimer.singleShot(3000, lambda: self.save_btn.setText(self._tr.t('stroop.save_report')))

    def _csv(self, path):
        s = self._summary
        with open(path,'w',newline='',encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["Stroop Test Results"])
            w.writerow(["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]); w.writerow([])
            for k,v in [
                ("total_trials",s['total']),("accuracy_%",f"{s['accuracy']:.2f}"),
                ("acc_congruent_%",f"{s['acc_congruent']:.2f}"),("acc_incongruent_%",f"{s['acc_incongruent']:.2f}"),
                ("avg_rt_s",f"{s['avg_rt']:.3f}"),("avg_rt_congruent_s",f"{s['avg_rt_congruent']:.3f}"),
                ("avg_rt_incongruent_s",f"{s['avg_rt_incongruent']:.3f}"),
                ("interference_rt_s",f"{s['interference_rt']:+.3f}"),
                ("stroop_effect_%",f"{s['stroop_effect_pct']:+.1f}"),
                ("ig_score",f"{s['ig_score']:.2f}"),
                ("error_interference_%",f"{s['error_interference']:+.1f}"),
                ("median_rt_s",f"{s['median_rt']:.3f}"),("std_rt_s",f"{s['std_rt']:.3f}"),
            ]: w.writerow([k,v])
            w.writerow([]); w.writerow(["trial","type","correct","rt_s"])
            for t in s['trials']:
                w.writerow([t.trial,"Congruent" if t.congruent else "Incongruent","yes" if t.correct else "no",f"{t.rt:.3f}"])

    def _json(self, path):
        s = self._summary
        with open(path,'w',encoding='utf-8') as f:
            json.dump({
                "test":"Stroop","date":datetime.now().isoformat(),
                "summary":{
                    "total":s['total'],"accuracy_pct":round(s['accuracy'],2),
                    "acc_congruent_pct":round(s['acc_congruent'],2),
                    "acc_incongruent_pct":round(s['acc_incongruent'],2),
                    "avg_rt_s":round(s['avg_rt'],3),
                    "avg_rt_congruent_s":round(s['avg_rt_congruent'],3),
                    "avg_rt_incongruent_s":round(s['avg_rt_incongruent'],3),
                    "interference_rt_s":round(s['interference_rt'],3),
                    "stroop_effect_pct":round(s['stroop_effect_pct'],1),
                    "ig_score":round(s['ig_score'],2),
                    "error_interference_pct":round(s['error_interference'],1),
                    "median_rt_s":round(s['median_rt'],3),
                    "std_rt_s":round(s['std_rt'],3),
                },
                "trials":[{"trial":t.trial,"congruent":t.congruent,"correct":t.correct,"rt_s":round(t.rt,3)} for t in s['trials']]
            },f,indent=2,ensure_ascii=False)

    def _txt(self, path):
        s = self._summary
        sep = "─"*46
        lines = [
            "╔══════════════════════════════════════════════╗",
            "║        STROOP TEST RESULTS REPORT            ║",
            "╚══════════════════════════════════════════════╝",
            f"  Date : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}",
            "","  OVERALL",f"  {sep}",
            f"  Total trials    : {s['total']}",
            f"  Accuracy        : {s['accuracy']:.1f}%",
            "","  BY CONDITION",f"  {sep}",
            f"  Congruent acc.  : {s['acc_congruent']:.1f}%   RT: {s['avg_rt_congruent']:.3f} s",
            f"  Incongruent acc.: {s['acc_incongruent']:.1f}%   RT: {s['avg_rt_incongruent']:.3f} s",
            "","  INTERFERENCE (Stroop Effect)",f"  {sep}",
            f"  Interference RT : {s['interference_rt']:+.3f} s",
            f"  Stroop effect   : {s['stroop_effect_pct']:+.1f}%",
            f"  IG score (Golden): {s['ig_score']:.2f}",
            f"  Error interfer. : {s['error_interference']:+.1f}%",
            "","  TRIALS",f"  {sep}",
            f"  {'#':<5}  {'Type':<13}  {'Result':<8}  {'RT (s)'}",f"  {sep}",
        ]
        for t in s['trials']:
            tp = "Congruent" if t.congruent else "Incongruent"
            lines.append(f"  {t.trial:<5}  {tp:<13}  {'✓' if t.correct else '✗':<8}  {t.rt:.3f}")
        lines.append(f"  {sep}")
        with open(path,'w',encoding='utf-8') as f: f.write("\n".join(lines)+"\n")

    def _pdf(self, path):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas as rl_canvas
        import math as _m

        s = self._summary; W, H = A4
        c = rl_canvas.Canvas(path, pagesize=A4)
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

        CREAM  = colors.HexColor("#fffbf0"); WHITE = colors.white
        DARK   = colors.HexColor("#2c2825"); MUTED = colors.HexColor("#9a9590")
        FAINT  = colors.HexColor("#f0e8d0")
        CONG   = colors.HexColor("#5b8fd4"); INCONG = colors.HexColor("#e06058")
        INTER  = colors.HexColor("#d95878"); AMBER  = colors.HexColor("#e09a30")
        LAVEND = colors.HexColor("#8b7ad9"); GOOD   = colors.HexColor("#4dab83")
        STONE  = colors.HexColor("#8a96a8")

        def rr(x,y,w,h,r=6,fill=WHITE,stroke_col=None):
            c.saveState(); c.setFillColor(fill)
            c.setLineWidth(0.4 if stroke_col else 0)
            if stroke_col: c.setStrokeColor(stroke_col)
            c.roundRect(x,y,w,h,r,fill=1,stroke=1 if stroke_col else 0); c.restoreState()

        def txt(x,y,s_,size=9,bold=False,col=DARK,align="left"):
            c.saveState(); c.setFillColor(col)
            c.setFont("Helvetica-Bold" if bold else "Helvetica",size)
            if align=="center": c.drawCentredString(x,y,s_)
            elif align=="right": c.drawRightString(x,y,s_)
            else: c.drawString(x,y,s_); c.restoreState()

        c.setFillColor(CREAM); c.rect(0,0,W,H,fill=1,stroke=0)
        rr(0,H-52,W,52,r=0,fill=DARK)
        txt(W/2,H-28,"STROOP TEST RESULTS",16,True,WHITE,"center")
        txt(W/2,H-42,now_str,7,False,MUTED,"center")

        M=36; IW=W-2*M; y=H-68

        # Accuracy ring
        ring_cx=M+46; ring_cy=y-52; ring_r=36; acc=s['accuracy']
        ring_col = GOOD if acc>=80 else (AMBER if acc>=50 else INCONG)
        rr(M,y-104,104,104,fill=WHITE,stroke_col=FAINT)
        c.saveState(); c.setStrokeColor(FAINT); c.setLineWidth(7)
        c.circle(ring_cx,ring_cy,ring_r,fill=0,stroke=1); c.restoreState()
        steps=max(2,int(acc/100*72))
        c.saveState(); c.setStrokeColor(ring_col); c.setLineWidth(7)
        for i in range(steps):
            a0=_m.radians(90-360*i/72); a1=_m.radians(90-360*(i+1)/72)
            c.line(ring_cx+ring_r*_m.cos(a0),ring_cy+ring_r*_m.sin(a0),
                   ring_cx+ring_r*_m.cos(a1),ring_cy+ring_r*_m.sin(a1))
        c.restoreState()
        txt(ring_cx,ring_cy-6,f"{acc:.0f}%",16,True,DARK,"center")
        txt(ring_cx,ring_cy-17,"accuracy",7,False,MUTED,"center")

        sw=(IW-108-12)/4; sx0=M+112
        for i,(val,lbl,col_) in enumerate([
            (f"{s['acc_congruent']:.0f}%",   "Congruent Acc.",   CONG),
            (f"{s['acc_incongruent']:.0f}%",  "Incongruent Acc.", INCONG),
            (f"{s['avg_rt_congruent']:.2f}s",  "Congruent RT",    CONG),
            (f"{s['avg_rt_incongruent']:.2f}s","Incongruent RT",  INCONG),
        ]):
            rr(sx0+i*(sw+4),y-104,sw,48,fill=WHITE,stroke_col=FAINT)
            c.saveState(); c.setFillColor(col_); c.circle(sx0+i*(sw+4)+10,y-92,3,fill=1,stroke=0); c.restoreState()
            txt(sx0+i*(sw+4)+18,y-96,val,12,True,DARK)
            txt(sx0+i*(sw+4)+18,y-104+6,lbl,7,False,MUTED)

        y-=116
        rr(M,y-52,IW,52,fill=WHITE,stroke_col=FAINT)
        txt(M+8,y-12,"INTERFERENCE METRICS (Stroop Effect)",8,True,MUTED)
        aw=IW/4
        inter_vals=[
            (f"{s['interference_rt']:+.3f}s","Interference RT",INTER),
            (f"{s['stroop_effect_pct']:+.1f}%","Stroop Effect %",AMBER),
            (f"{s['ig_score']:.2f}","IG Score (Golden)",LAVEND),
            (f"{s['error_interference']:+.1f}%","Error Interference",INCONG),
        ]
        for i,(val,lbl,col_) in enumerate(inter_vals):
            ax=M+i*aw+aw/2
            if i>0:
                c.saveState(); c.setStrokeColor(FAINT); c.setLineWidth(0.4)
                c.line(M+i*aw,y-46,M+i*aw,y-8); c.restoreState()
            txt(ax,y-28,val,13,True,col_,"center")
            txt(ax,y-43,lbl,7,False,MUTED,"center")

        y-=64
        rr(M,y-118,IW,118,fill=WHITE,stroke_col=FAINT)
        txt(M+8,y-12,"REACTION TIME - TRIAL BY TRIAL",7,True,MUTED)
        trials=s['trials']; max_rt=max(t.rt for t in trials) if trials else 1.0
        bx0=M+24; bw_=IW-80; bh=7; gap_=min(13,100/max(1,len(trials)))
        for i,t in enumerate(trials):
            by=y-28-i*(bh+gap_)
            if by<y-114: break
            fw=max(5,bw_*t.rt/max_rt)
            col_=CONG if t.congruent else INCONG
            if not t.correct: col_=colors.HexColor("#e06058")
            c.setFillColor(FAINT); c.roundRect(bx0,by,bw_,bh,3,fill=1,stroke=0)
            c.setFillColor(col_); c.roundRect(bx0,by,fw,bh,3,fill=1,stroke=0)
            txt(bx0-4,by+1,f"#{t.trial}",6,False,MUTED,"right")
            txt(bx0+fw+4,by+1,f"{t.rt:.2f}s",6,False,STONE)

        y-=130
        if y>80:
            cols=[M,M+30,M+110,M+200,M+280]; rh=14
            rr(M,y-rh,IW,rh,fill=DARK)
            for cx_,hd in zip(cols,["#","Type","RT (s)","vs Avg","Result"]):
                txt(cx_+3,y-rh+4,hd,7,True,WHITE)
            for ri,t in enumerate(trials):
                ry=y-rh-(ri+1)*rh
                if ry<30: break
                bg=colors.HexColor("#f0f5fc") if t.congruent else colors.HexColor("#fdf2f1")
                rr(M,ry,IW,rh,fill=bg)
                diff=t.rt-s['avg_rt']
                for cx_,v,fc in [
                    (cols[0],str(t.trial),MUTED),
                    (cols[1],"Congruent" if t.congruent else "Incongruent",CONG if t.congruent else INCONG),
                    (cols[2],f"{t.rt:.3f}",DARK),
                    (cols[3],f"{diff:+.3f}",GOOD if diff<=0 else INCONG),
                    (cols[4],"✓" if t.correct else "✗",GOOD if t.correct else INCONG),
                ]:
                    txt(cx_+3,ry+4,v,7,False,fc)

        txt(W/2,18,f"Cognitive Function Assessment Suite  ·  {now_str}",6,False,MUTED,"center")
        c.save()

    def retranslate(self, lang=None):
        tr = self._tr.t
        self.title_lbl.setText(tr('stroop.results_title'))
        self.restart_btn.setText(tr('stroop.restart'))
        self.back_btn.setText(tr('stroop.back_main_menu'))
        self.save_btn.setText(tr('stroop.save_report'))
        self.exp_hint.setText(tr('stroop.export_hint'))
        self.ring._label = tr('stroop.accuracy_label')
        self.ring.update()
        self.lbl_inter_title.setText(tr('stroop.section_interference'))
        self.lbl_rt_title.setText(tr('stroop.section_rt_comparison'))
        self.lbl_spark_title.setText(tr('stroop.section_trend'))
        self.lbl_trials_title.setText(tr('stroop.section_trials'))
        self.lbl_export.setText(tr('stroop.export_title'))
        for w, key in [(self.s_acc_cong,'stroop.lbl_acc_cong'),(self.s_acc_incong,'stroop.lbl_acc_incong'),
                       (self.s_rt_cong,'stroop.lbl_rt_cong'),(self.s_rt_incong,'stroop.lbl_rt_incong'),
                       (self.s_inter_rt,'stroop.lbl_inter_rt'),(self.s_inter_pct,'stroop.lbl_stroop_pct'),
                       (self.s_ig,'stroop.lbl_ig'),(self.s_err_inter,'stroop.lbl_err_inter')]:
            w.dl.setText(tr(key))
        for lbl, key in self.spark_legends + self.trial_legends:
            lbl.setText(tr(key))