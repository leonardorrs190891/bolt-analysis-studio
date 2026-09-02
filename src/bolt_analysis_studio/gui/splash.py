"""Animated splash screen for Bolt Analysis Studio.

Displayed at application startup for a minimum of 5 seconds while the
main window initialises. Pure PyQt6 / QPainter — no external dependencies.
"""
from __future__ import annotations

import math
import sys
import time

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QGuiApplication, QLinearGradient, QPainter,
    QPainterPath, QPen, QRadialGradient,
)
from PyQt6.QtWidgets import QApplication, QWidget

from .theme import Theme


def project_hex_faces(theta_deg: float, R: float, W: float):
    """Project a rotating hex prism onto 2D screen coordinates.

    Args:
        theta_deg: Global rotation about the vertical axis, degrees.
        R: Circumradius — distance from axis to face centre.
        W: Face width (equal to hex side length).

    Returns:
        List of dicts (length 6) sorted back-to-front by depth, each with:
            face_angle_deg: Base angle of this face (0, 60, 120, 180, 240, 300).
            cx: Horizontal screen offset from prism axis (px).
            w: Projected width (px) — foreshortened by cos(α).
            z: Depth for sorting (R·cos(α)).
            visible: True iff cos(α) > 0 (front-facing, non-edge-on).
    """
    theta_rad = math.radians(theta_deg)
    faces = []
    for k in range(6):
        face_angle_deg = k * 60
        alpha = theta_rad + math.radians(face_angle_deg)
        cos_a = math.cos(alpha)
        sin_a = math.sin(alpha)
        faces.append({
            'face_angle_deg': face_angle_deg,
            'cx': R * sin_a,
            'w': W * abs(cos_a),
            'z': R * cos_a,
            'visible': cos_a > 1e-9,
        })
    faces.sort(key=lambda f: f['z'])
    return faces


def sample_path(path: QPainterPath, n: int):
    """Return `n` QPointF samples at equal arc-length along the path.

    Uses `QPainterPath.pointAtPercent` which is QPainter's built-in
    parametric sampler (distance, not arc length — close enough for
    visual purposes).
    """
    if n < 2:
        return [path.pointAtPercent(0.0)]
    return [path.pointAtPercent(i / (n - 1)) for i in range(n)]


class AnimatedSplashScreen(QWidget):
    """Borderless translucent widget acting as animated splash.

    Public API mirrors `QSplashScreen.finish(main_window)` so it can be used
    as a drop-in replacement in `run_app.py`.
    """

    FRAME_INTERVAL_MS = 16   # ~60 fps
    WIDTH = 640
    HEIGHT = 360

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geo = screen.geometry()
            self.move((geo.width() - self.WIDTH) // 2,
                      (geo.height() - self.HEIGHT) // 2)

        self._start_time = time.monotonic()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(self.FRAME_INTERVAL_MS)

        self._curve_path = self._build_decay_path()
        self._curve_samples = sample_path(self._curve_path, n=100)

    def _build_decay_path(self) -> QPainterPath:
        """Preload decay curve in splash coordinates."""
        p = QPainterPath()
        p.moveTo(self._CP_X + 30,  self._CP_Y + 30)
        p.lineTo(self._CP_X + 90,  self._CP_Y + 30)
        p.quadTo(self._CP_X + 130, self._CP_Y + 30,
                 self._CP_X + 155, self._CP_Y + 65)
        p.quadTo(self._CP_X + 205, self._CP_Y + 140,
                 self._CP_X + 260, self._CP_Y + 158)
        p.quadTo(self._CP_X + 290, self._CP_Y + 167,
                 self._CP_X + 308, self._CP_Y + 168)
        return p

    def _draw_background(self, painter: QPainter) -> None:
        rect = QRectF(0, 0, self.WIDTH, self.HEIGHT)

        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.setClipPath(path)

        grad = QLinearGradient(0, 0, self.WIDTH, self.HEIGHT)
        grad.setColorAt(0.0, QColor(Theme.BASE))
        grad.setColorAt(1.0, QColor(Theme.MANTLE))
        painter.fillRect(rect, QBrush(grad))

        for cx, cy in ((0.30 * self.WIDTH, 0.20 * self.HEIGHT),
                       (0.80 * self.WIDTH, 0.90 * self.HEIGHT)):
            rg = QRadialGradient(cx, cy, 280.0)
            rg.setColorAt(0.0, QColor(Theme.SURFACE0))
            rg.setColorAt(1.0, QColor(49, 50, 68, 0))
            painter.fillRect(rect, QBrush(rg))

        pen = QPen(QColor(205, 214, 244, int(0.025 * 255)))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for x in range(0, self.WIDTH, 20):
            painter.drawLine(x, 0, x, self.HEIGHT)
        for y in range(0, self.HEIGHT, 20):
            painter.drawLine(0, y, self.WIDTH, y)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor(205, 214, 244, int(0.08 * 255)))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)

    def _draw_title(self, painter: QPainter) -> None:
        title_rect = QRectF(0, 22, self.WIDTH, 36)
        grad = QLinearGradient(0, title_rect.top(), 0, title_rect.bottom())
        grad.setColorAt(0.0, QColor('#ffffff'))
        grad.setColorAt(1.0, QColor(Theme.SUBTEXT))

        font = QFont('Segoe UI', 22, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.setPen(QPen(QBrush(grad), 0))
        painter.drawText(title_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'BOLT ANALYSIS STUDIO')

        sub_rect = QRectF(0, 60, self.WIDTH, 18)
        font = QFont('Segoe UI', 9)
        painter.setFont(font)
        painter.setPen(QColor(Theme.BLUE))
        painter.drawText(sub_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'V2 \u00b7 Bolted Joint Self-Loosening Analysis')

        auth_rect = QRectF(0, 78, self.WIDTH, 16)
        font = QFont('Segoe UI', 8)
        painter.setFont(font)
        painter.setPen(QColor(Theme.OVERLAY))
        # os DOIS autores do software (decisao de 2026-09-01). Medido: 359 px
        # dos 640 disponiveis a 8 pt, e 15 px de altura no rect de 16 — cabe
        # numa linha, sem precisar reduzir a fonte nem quebrar em duas.
        painter.drawText(auth_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'Prof. Leonardo Rosa Ribeiro da Silva, PhD'
                         '  ·  Neilon de Souza da Silva, PhD')

    @staticmethod
    def _flange_gradient(y: float, h: float) -> QLinearGradient:
        grad = QLinearGradient(0, y, 0, y + h)
        grad.setColorAt(0.0, QColor('#585b70'))
        grad.setColorAt(0.5, QColor('#9399b2'))
        grad.setColorAt(1.0, QColor('#45475a'))
        return grad

    @staticmethod
    def _steel_gradient(x: float, w: float) -> QLinearGradient:
        grad = QLinearGradient(x, 0, x + w, 0)
        grad.setColorAt(0.0,  QColor('#45475a'))
        grad.setColorAt(0.2,  QColor('#a6adc8'))
        grad.setColorAt(0.5,  QColor('#f5f5ff'))
        grad.setColorAt(0.8,  QColor('#7f849c'))
        grad.setColorAt(1.0,  QColor('#313244'))
        return grad

    def _draw_hatch(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        painter.setClipRect(rect)
        pen = QPen(QColor(108, 112, 134, int(0.6 * 255)))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        diag = 5.0
        x0 = rect.left() - rect.height()
        x1 = rect.right()
        x = x0
        while x < x1:
            painter.drawLine(QPointF(x, rect.bottom()),
                             QPointF(x + rect.height(), rect.top()))
            x += diag
        painter.restore()

    _JP_X = 36
    _JP_Y = 90
    _JP_W = 220
    _JP_H = 240
    _AXIS_X = _JP_X + 110

    # Thread animation timing (seconds per pitch / revolution)
    NUT_PERIOD_S = 15.0
    PITCH_PX = 6.0

    # Hex-prism geometry (shared by nut and head)
    HEX_R = 26.0
    HEX_W = 30.0

    def _draw_hex_prism(self,
                        painter: QPainter,
                        cx: float, top_y: float,
                        height: float,
                        theta_deg: float,
                        gradient_stops: list) -> None:
        """Draw 6-faced hex prism centred at (cx, top_y) with given face height."""
        faces = project_hex_faces(theta_deg, self.HEX_R, self.HEX_W)
        boundaries = []
        for face in faces:
            if not face['visible']:
                continue
            w = face['w']
            if w < 0.5:
                continue
            x = cx + face['cx'] - w / 2
            rect = QRectF(x, top_y, w, height)

            grad = QLinearGradient(0, top_y, 0, top_y + height)
            for offset, colour in gradient_stops:
                grad.setColorAt(offset, QColor(colour))
            painter.fillRect(rect, QBrush(grad))

            painter.fillRect(QRectF(x, top_y, w, 1.5),
                             QColor(gradient_stops[0][1]))
            painter.fillRect(QRectF(x, top_y + height - 1.5, w, 1.5),
                             QColor(gradient_stops[-1][1]))

            boundaries.append(round(x, 2))
            boundaries.append(round(x + w, 2))

        if boundaries:
            counts = {}
            for b in boundaries:
                counts[b] = counts.get(b, 0) + 1
            silhouette_xs = sorted(x for x, c in counts.items() if c == 1)
            seam_xs = sorted(x for x, c in counts.items() if c >= 2)

            seam_pen = QPen(QColor(10, 10, 16, int(0.7 * 255)))
            seam_pen.setWidthF(0.8)
            painter.setPen(seam_pen)
            for sx in seam_xs:
                painter.drawLine(QPointF(sx, top_y),
                                 QPointF(sx, top_y + height))

            rim_pen = QPen(QColor(255, 255, 255, int(0.35 * 255)))
            rim_pen.setWidthF(0.5)
            painter.setPen(rim_pen)
            for sx in silhouette_xs:
                inset = 0.5 if sx == silhouette_xs[0] else -0.5
                painter.drawLine(QPointF(sx + inset, top_y + 1.5),
                                 QPointF(sx + inset, top_y + height - 1.5))

    def _draw_joint_static(self, painter: QPainter) -> None:
        pen = QPen(QColor(Theme.RED))
        pen.setWidthF(0.6)
        pen.setDashPattern([5, 2, 1, 2])
        painter.setPen(pen)
        painter.setOpacity(0.65)
        painter.drawLine(self._AXIS_X, self._JP_Y + 10,
                         self._AXIS_X, self._JP_Y + 230)
        painter.setOpacity(1.0)

        for fy in (self._JP_Y + 85, self._JP_Y + 107):
            rect = QRectF(self._JP_X + 35, fy, 150, 22)
            painter.fillRect(rect, QBrush(self._flange_gradient(fy, 22)))
            self._draw_hatch(painter, rect)
            painter.setPen(QPen(QColor('#313244'), 0.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

        pen = QPen(QColor(Theme.RED))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.setOpacity(0.9)
        y_part = self._JP_Y + 107
        painter.drawLine(self._JP_X + 35, y_part, self._JP_X + 185, y_part)
        painter.setOpacity(1.0)

        shank_rect = QRectF(self._JP_X + 100, self._JP_Y + 85, 20, 44)
        painter.fillRect(shank_rect,
                         QBrush(self._steel_gradient(shank_rect.left(), 20)))
        painter.setPen(QPen(QColor('#313244'), 0.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(shank_rect)

        painter.setPen(QColor(Theme.OVERLAY))
        font = QFont('Segoe UI', 7)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(self._JP_X, self._JP_Y + 212, self._JP_W, 14),
                         Qt.AlignmentFlag.AlignHCenter, 'BOLTED JOINT')

    def _draw_threads(self, painter: QPainter, t: float) -> None:
        """Threads below the shank, scrolling down at 1 pitch / NUT_PERIOD_S."""
        thread_x = self._JP_X + 100
        thread_y = self._JP_Y + 129
        thread_w = 20
        thread_h = 66
        thread_rect = QRectF(thread_x, thread_y, thread_w, thread_h)

        scroll = (t / self.NUT_PERIOD_S) * self.PITCH_PX
        scroll = scroll % self.PITCH_PX

        painter.save()
        painter.setClipRect(thread_rect)

        pattern_y_start = thread_y - self.PITCH_PX + scroll
        y = pattern_y_start
        while y < thread_y + thread_h:
            self._draw_thread_pitch(painter, thread_x, y, thread_w)
            y += self.PITCH_PX

        painter.setBrush(QColor(Theme.BASE))
        pen = QPen(QColor('#0a0a10'))
        pen.setWidthF(0.4)
        painter.setPen(pen)

        left = QPainterPath()
        left.moveTo(thread_x, pattern_y_start)
        yy = pattern_y_start
        while yy < thread_y + thread_h + self.PITCH_PX:
            left.lineTo(thread_x - 3, yy + 3)
            left.lineTo(thread_x,     yy + 6)
            yy += 6
        painter.drawPath(left)

        right = QPainterPath()
        right.moveTo(thread_x + thread_w, pattern_y_start)
        yy = pattern_y_start
        while yy < thread_y + thread_h + self.PITCH_PX:
            right.lineTo(thread_x + thread_w + 3, yy + 3)
            right.lineTo(thread_x + thread_w,     yy + 6)
            yy += 6
        painter.drawPath(right)

        painter.restore()

        painter.setPen(QPen(QColor('#313244'), 0.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(thread_rect)

    def _draw_thread_pitch(self, painter: QPainter,
                            x: float, y: float, w: float) -> None:
        """One 6-px-tall pitch unit: gradient background + root + crest bands."""
        unit = QRectF(x, y, w, self.PITCH_PX)
        painter.fillRect(unit, QBrush(self._steel_gradient(x, w)))
        painter.fillRect(QRectF(x, y,         w, 1.5),
                         QColor(0, 0, 0, int(0.55 * 255)))
        painter.fillRect(QRectF(x, y + 3.0,   w, 0.8),
                         QColor(255, 255, 255, int(0.75 * 255)))
        painter.fillRect(QRectF(x, y + 3.8,   w, 0.4),
                         QColor(255, 255, 255, int(0.30 * 255)))

    _HEAD_GRADIENT = [
        (0.0,  '#f5f5ff'),
        (0.2,  '#cdd6f4'),
        (0.5,  '#9399b2'),
        (0.8,  '#585b70'),
        (1.0,  '#313244'),
    ]

    def _draw_head(self, painter: QPainter, t: float) -> None:
        # Head rotates opposite to nut, same angular speed.
        phase = (t % self.NUT_PERIOD_S) / self.NUT_PERIOD_S
        theta_deg = -phase * 360.0
        cx = self._AXIS_X
        top = self._JP_Y + 52
        self._draw_hex_prism(painter,
                             cx=cx, top_y=top, height=33,
                             theta_deg=theta_deg,
                             gradient_stops=self._HEAD_GRADIENT)

    def _draw_shank_rotation(self, painter: QPainter, t: float) -> None:
        """Oscillating highlight band on the shank — cylinder rotating opposite
        to the nut at the same angular speed. Highlight x-position and width
        follow cos/sin of theta so the glint traces around a cylindrical body.
        """
        phase = (t % self.NUT_PERIOD_S) / self.NUT_PERIOD_S
        theta_rad = -phase * 2.0 * math.pi
        sx = math.sin(theta_rad)
        cx_vis = math.cos(theta_rad)
        if cx_vis <= 0.0:
            return  # glint on the far side of the cylinder

        shank_left = self._JP_X + 100
        shank_top = self._JP_Y + 85
        shank_w = 20.0
        shank_h = 44.0
        R = shank_w / 2.0
        cx = shank_left + R

        highlight_w = 2.0 * cx_vis
        if highlight_w < 0.3:
            return
        highlight_x = cx + R * sx - highlight_w / 2.0

        alpha = int(0.30 * 255 * cx_vis)
        painter.fillRect(QRectF(highlight_x, shank_top, highlight_w, shank_h),
                         QColor(255, 255, 255, alpha))

    _NUT_GRADIENT = [
        (0.0,  '#fff5c7'),
        (0.3,  '#f9e2af'),
        (0.6,  '#e5c989'),
        (1.0,  '#9a804a'),
    ]
    NUT_DESCENT_PX = 3.0

    def _draw_nut(self, painter: QPainter, t: float) -> None:
        phase = (t % self.NUT_PERIOD_S) / self.NUT_PERIOD_S
        theta_deg = phase * 360.0
        delta_y  = phase * self.NUT_DESCENT_PX
        cx = self._AXIS_X
        top = self._JP_Y + 127 + delta_y
        self._draw_hex_prism(painter,
                             cx=cx, top_y=top, height=24,
                             theta_deg=theta_deg,
                             gradient_stops=self._NUT_GRADIENT)

    _CP_X = 292
    _CP_Y = 100
    _CP_W = 320
    _CP_H = 200

    def _draw_curve_static(self, painter: QPainter) -> None:
        x0 = self._CP_X
        y0 = self._CP_Y

        pen = QPen(QColor(205, 214, 244, int(0.18 * 255)))
        pen.setWidthF(0.5)
        painter.setPen(pen)
        for gy in (30, 65, 100, 135):
            painter.drawLine(QPointF(x0 + 30,  y0 + gy),
                             QPointF(x0 + 300, y0 + gy))
        for gx in (90, 150, 210, 270):
            painter.drawLine(QPointF(x0 + gx, y0 + 20),
                             QPointF(x0 + gx, y0 + 170))

        pen = QPen(QColor(Theme.GREEN))
        pen.setWidthF(1.0)
        pen.setDashPattern([3, 2])
        painter.setPen(pen)
        painter.setOpacity(0.7)
        painter.drawLine(QPointF(x0 + 30, y0 + 30), QPointF(x0 + 110, y0 + 30))
        painter.setOpacity(1.0)
        painter.setPen(QColor(Theme.GREEN))
        painter.setFont(QFont('Segoe UI', 7))
        painter.drawText(QPointF(x0 + 14, y0 + 33), 'F\u2080')

        pen = QPen(QColor('#9399b2'))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawLine(QPointF(x0 + 30, y0 + 20),  QPointF(x0 + 30,  y0 + 170))
        painter.drawLine(QPointF(x0 + 30, y0 + 170), QPointF(x0 + 310, y0 + 170))

        font = QFont('Segoe UI', 8, italic=True)
        painter.setFont(font)
        painter.drawText(QPointF(x0 + 18,  y0 + 25),  'F')
        painter.drawText(QPointF(x0 + 305, y0 + 185), 'N')

        painter.setFont(QFont('Segoe UI', 7))
        painter.setPen(QColor(Theme.BLUE))
        painter.drawText(QRectF(x0 + 30, y0 + 8, 80, 12),
                         Qt.AlignmentFlag.AlignHCenter, 'Stage I')
        painter.setPen(QColor(Theme.RED))
        painter.drawText(QRectF(x0 + 180, y0 + 8, 80, 12),
                         Qt.AlignmentFlag.AlignHCenter, 'Stage II')

        pen = QPen(QColor(Theme.OVERLAY))
        pen.setWidthF(0.5)
        pen.setDashPattern([2, 2])
        painter.setPen(pen)
        painter.setOpacity(0.5)
        painter.drawLine(QPointF(x0 + 115, y0 + 12), QPointF(x0 + 115, y0 + 170))
        painter.setOpacity(1.0)

        painter.setPen(QColor(Theme.OVERLAY))
        font = QFont('Segoe UI', 7)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(x0, y0 + 188, self._CP_W, 14),
                         Qt.AlignmentFlag.AlignHCenter,
                         'PRELOAD DECAY \u00b7 F/F\u2080 vs CYCLES')

    CURVE_PERIOD_S = 3.2

    def _draw_curve_animated(self, painter: QPainter, t: float) -> None:
        phase = (t % self.CURVE_PERIOD_S) / self.CURVE_PERIOD_S
        if phase < 0.85:
            progress = phase / 0.85
            progress = 1.0 - (1.0 - progress) ** 3
        else:
            progress = 1.0

        x_start = self._CP_X + 30
        x_end   = self._CP_X + 310
        x_now   = x_start + progress * (x_end - x_start)

        painter.save()
        painter.setClipRect(QRectF(x_start, self._CP_Y + 20,
                                   x_now - x_start, 150))

        grad = QLinearGradient(self._CP_X + 30, 0, self._CP_X + 308, 0)
        grad.setColorAt(0.0, QColor(Theme.GREEN))
        grad.setColorAt(0.5, QColor(Theme.YELLOW))
        grad.setColorAt(1.0, QColor(Theme.RED))
        pen = QPen(QBrush(grad), 2.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._curve_path)

        painter.restore()

        if progress > 0.02:
            idx = int(progress * (len(self._curve_samples) - 1))
            pt = self._curve_samples[idx]
            painter.setBrush(QColor(249, 226, 175, int(0.35 * 255)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pt, 8, 8)
            painter.setBrush(QColor(Theme.YELLOW))
            painter.drawEllipse(pt, 4, 4)

    PROGRESS_PERIOD_S = 2.2

    def _draw_progress(self, painter: QPainter, t: float) -> None:
        track_left   = 80
        track_right  = self.WIDTH - 80
        track_width  = track_right - track_left
        track_top    = self.HEIGHT - 18 - 4
        track_height = 4

        track_rect = QRectF(track_left, track_top, track_width, track_height)
        painter.setBrush(QColor(49, 50, 68, int(0.8 * 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 2, 2)

        fill_width = 0.40 * track_width
        phase = (t % self.PROGRESS_PERIOD_S) / self.PROGRESS_PERIOD_S
        eased = 0.5 - 0.5 * math.cos(math.pi * phase)
        translate = -fill_width + eased * 3.5 * fill_width

        painter.save()
        painter.setClipRect(track_rect)
        fill_rect = QRectF(track_left + translate, track_top,
                           fill_width, track_height)
        grad = QLinearGradient(fill_rect.left(), 0, fill_rect.right(), 0)
        grad.setColorAt(0.0, QColor(137, 180, 250, 0))
        grad.setColorAt(0.3, QColor(Theme.BLUE))
        grad.setColorAt(0.7, QColor(Theme.GREEN))
        grad.setColorAt(1.0, QColor(166, 227, 161, 0))
        painter.fillRect(fill_rect, QBrush(grad))
        painter.restore()

        painter.setPen(QColor(Theme.GREEN))
        font = QFont('Segoe UI', 8)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(0, self.HEIGHT - 14, self.WIDTH, 14),
                         Qt.AlignmentFlag.AlignHCenter,
                         'INITIALISING MODULES\u2026')

    PRELOAD_PERIOD_S = 2.4

    def _draw_preload_arrows(self, painter: QPainter, t: float) -> None:
        phase = (t / self.PRELOAD_PERIOD_S) * 2 * math.pi
        opacity = 0.55 + 0.45 * (0.5 - 0.5 * math.cos(phase))

        painter.save()
        painter.setOpacity(opacity)

        pen = QPen(QColor(Theme.GREEN))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        font = QFont('Segoe UI', 7)
        painter.setFont(font)

        for x in (self._JP_X + 48, self._JP_X + 172):
            painter.drawLine(QPointF(x, self._JP_Y + 22),
                             QPointF(x, self._JP_Y + 45))
            head = QPainterPath()
            head.moveTo(x - 4, self._JP_Y + 41)
            head.lineTo(x,     self._JP_Y + 45)
            head.lineTo(x + 4, self._JP_Y + 41)
            painter.drawPath(head)
            painter.drawText(QRectF(x - 10, self._JP_Y + 8, 20, 12),
                             Qt.AlignmentFlag.AlignHCenter, 'F\u2080')

        painter.restore()

    def paintEvent(self, event) -> None:
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        self._draw_shank_rotation(painter, t)
        self._draw_head(painter, t)
        self._draw_threads(painter, t)
        self._draw_nut(painter, t)
        self._draw_preload_arrows(painter, t)
        self._draw_curve_static(painter)
        self._draw_curve_animated(painter, t)
        self._draw_progress(painter, t)
        painter.end()

    def finish(self, main_window) -> None:
        """Stop the animation timer and close the splash."""
        self._timer.stop()
        self.close()


if __name__ == '__main__':
    # Dev entry point: show the splash for 10 s for visual verification.
    app = QApplication(sys.argv)
    splash = AnimatedSplashScreen()
    splash.show()
    QTimer.singleShot(10_000, splash.close)
    sys.exit(app.exec())
