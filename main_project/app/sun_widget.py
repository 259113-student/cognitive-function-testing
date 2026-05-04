from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPixmap, QColor, QRadialGradient, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
import math


class SunWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(image_path)
        self.setMinimumSize(300, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # animation state
        self._t = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def update_animation(self):
        self._t += 0.04
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        center = rect.center()

        # Pulse factor (smooth breathing)
        pulse = 1.0 + 0.05 * math.sin(self._t)

        base_size = min(rect.width(), rect.height()) * 0.6
        size = base_size * pulse

        # Glow effect (radial gradient)
        glow_radius = math.ceil(size * 1.2)

        gradient = QRadialGradient(center.x(), center.y(), glow_radius)
        gradient.setColorAt(0.0, QColor(255, 230, 120, 220))  # strong center
        gradient.setColorAt(0.3, QColor(255, 200, 80, 90))    # fading
        gradient.setColorAt(0.4, QColor(255, 200, 80, 40))    # fading
        gradient.setColorAt(0.6, QColor(255, 200, 80, 0))     # fully transparent

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addEllipse(QPointF(center), glow_radius, glow_radius)
        painter.setClipPath(path)
        r = glow_radius
        circle = QRectF(center.x() - r, center.y() - r, 2*r, 2*r)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(circle)       

        # Draw sun image (scaled + centered)
        scaled = self.pixmap.scaled(
            int(size), int(size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        x = int(center.x() - scaled.width() / 2)
        y = int(center.y() - scaled.height() / 2)

        painter.drawPixmap(int(x), int(y), scaled)
