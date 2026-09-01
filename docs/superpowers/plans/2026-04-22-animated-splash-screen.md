# Animated Splash Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the static QPixmap splash block in `run_app.py:81–127` with an animated QPainter-based splash that shows a slowly rotating/descending hex nut on a threaded bolt, paired with a progressively-drawn preload-decay curve, a sweeping progress bar, and a title stack.

**Architecture:** Single `AnimatedSplashScreen(QWidget)` class in `src/bolt_analysis_studio/gui/splash.py`. A 16 ms `QTimer` drives `update()`; `paintEvent()` composes all layers from scratch each frame using a single monotonic frame-time float. No new dependencies — pure PyQt6.

**Tech Stack:** PyQt6 (QWidget, QPainter, QTimer, QLinearGradient, QRadialGradient, QPainterPath, QPen, QBrush, QFont, QPainterPathStroker).

**Reference:** All colours, positions, and dimensions come from the spec at `docs/superpowers/specs/2026-04-22-animated-splash-design.md` — the spec is the visual authority; this plan is the code.

---

## File Structure

- **Create:** `src/bolt_analysis_studio/gui/splash.py` (~400 LOC)
- **Create:** `tests/test_splash.py` (~120 LOC) — unit tests for pure-math helpers + smoke tests
- **Modify:** `run_app.py` lines 81–127 (replace ~40 lines with ~6 lines)

`splash.py` contains:
- Module-level pure functions: `project_hex_faces()`, `sample_path()`, `build_decay_path()`
- Class `AnimatedSplashScreen(QWidget)` with one `paintEvent` that delegates to `_draw_<layer>` methods
- `if __name__ == '__main__'` dev entry point for standalone visual verification

---

### Task 1: Create splash module skeleton with window + timer + dev entry

**Files:**
- Create: `src/bolt_analysis_studio/gui/splash.py`
- Create: `tests/test_splash.py`

- [ ] **Step 1: Write the failing smoke test**

Create `tests/test_splash.py`:

```python
"""Tests for the animated splash screen."""
import os
import sys

# Must be set before importing PyQt6
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from PyQt6.QtWidgets import QApplication

from bolt_analysis_studio.gui.splash import AnimatedSplashScreen


@pytest.fixture(scope='module')
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_splash_instantiates(qapp):
    splash = AnimatedSplashScreen()
    try:
        assert splash.width() == 640
        assert splash.height() == 360
        assert splash._timer.isActive()
    finally:
        splash.finish(None)


def test_splash_finish_stops_timer(qapp):
    splash = AnimatedSplashScreen()
    splash.finish(None)
    assert not splash._timer.isActive()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_splash.py -v`
Expected: FAIL with "cannot import name 'AnimatedSplashScreen'" (module doesn't exist yet).

- [ ] **Step 3: Create skeleton splash module**

Create `src/bolt_analysis_studio/gui/splash.py`:

```python
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

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Layers will be added in subsequent tasks
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_splash.py -v`
Expected: PASS, 2 tests green.

- [ ] **Step 5: Syntax check**

Run: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/splash.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py tests/test_splash.py
git commit -m "Add animated splash skeleton (empty paintEvent, timer, dev entry)"
```

---

### Task 2: Pure-math helper — hex-prism face projection (TDD)

Projects a rotating hex prism onto the 2D screen: returns per-face centre offset, projected width, depth, and visibility. Consumed by the nut and head renderers.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py` (add module-level function)
- Modify: `tests/test_splash.py` (add tests)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_splash.py`:

```python
import math

from bolt_analysis_studio.gui.splash import project_hex_faces


def test_hex_faces_at_zero_rotation_front_face_is_centred():
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    # Six results, one per face
    assert len(faces) == 6
    # Face 0 is front-centre: cx ≈ 0, w = W, visible
    f0 = next(f for f in faces if f['face_angle_deg'] == 0)
    assert abs(f0['cx']) < 1e-6
    assert abs(f0['w'] - 30.0) < 1e-6
    assert f0['visible'] is True


def test_hex_faces_at_zero_rotation_back_face_invisible():
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    f180 = next(f for f in faces if f['face_angle_deg'] == 180)
    assert f180['visible'] is False


def test_hex_faces_rotation_shifts_front():
    # After rotating 60°, face-300 should be at the front (α = 360 = 0)
    faces = project_hex_faces(theta_deg=60.0, R=26.0, W=30.0)
    f300 = next(f for f in faces if f['face_angle_deg'] == 300)
    assert abs(f300['cx']) < 1e-6
    assert abs(f300['w'] - 30.0) < 1e-6
    assert f300['visible'] is True


def test_hex_faces_edge_on_face_has_zero_width():
    # Face-90 (not one of the actual faces, but test the math) would have cos=0.
    # Real faces at θ=30°: face-60 has α=90° → cos=0 → w=0 → not visible.
    faces = project_hex_faces(theta_deg=30.0, R=26.0, W=30.0)
    f60 = next(f for f in faces if f['face_angle_deg'] == 60)
    assert f60['visible'] is False  # cos(90°) == 0, treat as not visible


def test_hex_faces_sorted_back_to_front():
    # At θ=0, z = R·cos(α). Sorted ascending z means deepest (smallest z) first.
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    z_values = [f['z'] for f in faces]
    assert z_values == sorted(z_values)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_splash.py::test_hex_faces_at_zero_rotation_front_face_is_centred -v`
Expected: FAIL with ImportError on `project_hex_faces`.

- [ ] **Step 3: Implement the function**

In `splash.py`, insert after the imports and before the class definition:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_splash.py -v`
Expected: all tests green (2 from Task 1 + 5 from Task 2).

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py tests/test_splash.py
git commit -m "Add hex-prism face projection math with unit tests"
```

---

### Task 3: Pure-math helper — QPainterPath sampling (TDD)

Samples N equally-spaced points along a `QPainterPath`. Used by the travelling-marker animation to locate the marker on the decay curve.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`
- Modify: `tests/test_splash.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_splash.py`:

```python
from PyQt6.QtGui import QPainterPath
from bolt_analysis_studio.gui.splash import sample_path


def test_sample_path_straight_line_uniform(qapp):
    p = QPainterPath()
    p.moveTo(0, 0)
    p.lineTo(100, 0)
    samples = sample_path(p, n=11)
    assert len(samples) == 11
    # First and last endpoints
    assert abs(samples[0].x() - 0) < 0.5
    assert abs(samples[-1].x() - 100) < 0.5
    # Middle sample should be near 50
    assert abs(samples[5].x() - 50) < 1.0


def test_sample_path_returns_qpointf(qapp):
    p = QPainterPath()
    p.moveTo(0, 0)
    p.lineTo(10, 10)
    samples = sample_path(p, n=3)
    for pt in samples:
        assert hasattr(pt, 'x') and hasattr(pt, 'y')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_splash.py::test_sample_path_straight_line_uniform -v`
Expected: FAIL with ImportError.

- [ ] **Step 3: Implement the function**

In `splash.py`, add next to `project_hex_faces`:

```python
def sample_path(path: QPainterPath, n: int):
    """Return `n` QPointF samples at equal arc-length along the path.

    Uses `QPainterPath.pointAtPercent` which is QPainter's built-in
    parametric sampler (distance, not arc length — close enough for
    visual purposes).
    """
    if n < 2:
        return [path.pointAtPercent(0.0)]
    return [path.pointAtPercent(i / (n - 1)) for i in range(n)]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_splash.py -v`
Expected: all tests green.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py tests/test_splash.py
git commit -m "Add QPainterPath sampling helper with unit tests"
```

---

### Task 4: Background layer (gradient + radial highlights + grid + border)

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_background` method**

Insert this method in the `AnimatedSplashScreen` class, after `__init__`:

```python
    def _draw_background(self, painter: QPainter) -> None:
        rect = QRectF(0, 0, self.WIDTH, self.HEIGHT)

        # Rounded clip so everything else paints inside the 12 px radius
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.setClipPath(path)

        # Base linear gradient 145°
        grad = QLinearGradient(0, 0, self.WIDTH, self.HEIGHT)
        grad.setColorAt(0.0, QColor('#1e1e2e'))
        grad.setColorAt(1.0, QColor('#181825'))
        painter.fillRect(rect, QBrush(grad))

        # Two radial highlights
        for cx, cy in ((0.30 * self.WIDTH, 0.20 * self.HEIGHT),
                       (0.80 * self.WIDTH, 0.90 * self.HEIGHT)):
            rg = QRadialGradient(cx, cy, 280.0)
            rg.setColorAt(0.0, QColor('#313244'))
            rg.setColorAt(1.0, QColor(49, 50, 68, 0))
            painter.fillRect(rect, QBrush(rg))

        # 20 px grid — very subtle
        pen = QPen(QColor(205, 214, 244, int(0.025 * 255)))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for x in range(0, self.WIDTH, 20):
            painter.drawLine(x, 0, x, self.HEIGHT)
        for y in range(0, self.HEIGHT, 20):
            painter.drawLine(0, y, self.WIDTH, y)

        # 1 px inner border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor(205, 214, 244, int(0.08 * 255)))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)
```

- [ ] **Step 2: Wire into paintEvent**

Replace the `paintEvent` body with:

```python
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Dark rounded rectangle with subtle gradient and grid appears for 10 s.

- [ ] **Step 4: Syntax + existing tests still pass**

Run:
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/splash.py', encoding='utf-8').read()); print('OK')"
pytest tests/test_splash.py -v
```
Expected: `OK` + all tests still green.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw splash background: gradient + radial highlights + grid + border"
```

---

### Task 5: Title stack (three centred text lines at top)

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_title` method**

```python
    def _draw_title(self, painter: QPainter) -> None:
        # Main title with vertical gradient text fill
        title_rect = QRectF(0, 22, self.WIDTH, 36)
        grad = QLinearGradient(0, title_rect.top(), 0, title_rect.bottom())
        grad.setColorAt(0.0, QColor('#ffffff'))
        grad.setColorAt(1.0, QColor('#a6adc8'))

        font = QFont('Segoe UI', 22, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.setPen(QPen(QBrush(grad), 0))
        painter.drawText(title_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'BOLT ANALYSIS STUDIO')

        # Subtitle
        sub_rect = QRectF(0, 60, self.WIDTH, 18)
        font = QFont('Segoe UI', 9)
        painter.setFont(font)
        painter.setPen(QColor('#89b4fa'))
        painter.drawText(sub_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'v4.0 · Bolted Joint Self-Loosening Analysis')

        # Author
        auth_rect = QRectF(0, 78, self.WIDTH, 16)
        font = QFont('Segoe UI', 8)
        painter.setFont(font)
        painter.setPen(QColor('#6c7086'))
        painter.drawText(auth_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                         'Prof. Leonardo Rosa Ribeiro da Silva, PhD')
```

- [ ] **Step 2: Call from paintEvent**

```python
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Three centred text lines at top (title, subtitle, author).

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw splash title stack (title + subtitle + author)"
```

---

### Task 6: Joint panel — static structural elements (flanges, shank, centreline, label)

The joint panel lives at (36, 90) with size 220 × 240. Pink centreline runs the full height. Two hatched flanges sandwich the shank.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add helper for hatched flange rendering**

Add this method to the class:

```python
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
        """45° diagonal hatch pattern for flange cross-section."""
        painter.save()
        painter.setClipRect(rect)
        pen = QPen(QColor(108, 112, 134, int(0.6 * 255)))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        # Diagonal lines spaced ~5 px apart (period of √2·5 along the lines)
        diag = 5.0
        x0 = rect.left() - rect.height()
        x1 = rect.right()
        x = x0
        while x < x1:
            painter.drawLine(QPointF(x, rect.bottom()),
                             QPointF(x + rect.height(), rect.top()))
            x += diag
        painter.restore()
```

- [ ] **Step 2: Add `_draw_joint_static` method**

```python
    # Joint panel origin (top-left of panel within the splash widget)
    _JP_X = 36
    _JP_Y = 90
    _JP_W = 220
    _JP_H = 240
    _AXIS_X = _JP_X + 110   # centre line X in splash coords

    def _draw_joint_static(self, painter: QPainter) -> None:
        # Centre line (pink dashed, engineering convention)
        pen = QPen(QColor('#f38ba8'))
        pen.setWidthF(0.6)
        pen.setDashPattern([5, 2, 1, 2])
        painter.setPen(pen)
        painter.setOpacity(0.65)
        painter.drawLine(self._AXIS_X, self._JP_Y + 10,
                         self._AXIS_X, self._JP_Y + 230)
        painter.setOpacity(1.0)

        # Two flanges, 150 × 22, stacked
        for fy in (self._JP_Y + 85, self._JP_Y + 107):
            rect = QRectF(self._JP_X + 35, fy, 150, 22)
            painter.fillRect(rect, QBrush(self._flange_gradient(fy, 22)))
            self._draw_hatch(painter, rect)
            # border
            painter.setPen(QPen(QColor('#313244'), 0.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

        # Pink parting line between flanges
        pen = QPen(QColor('#f38ba8'))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        painter.setOpacity(0.9)
        y_part = self._JP_Y + 107
        painter.drawLine(self._JP_X + 35, y_part, self._JP_X + 185, y_part)
        painter.setOpacity(1.0)

        # Shank (unthreaded part of the bolt)
        shank_rect = QRectF(self._JP_X + 100, self._JP_Y + 85, 20, 44)
        painter.fillRect(shank_rect, QBrush(self._steel_gradient(shank_rect.left(), 20)))
        painter.setPen(QPen(QColor('#313244'), 0.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(shank_rect)
        # White highlight stripe
        painter.fillRect(QRectF(self._JP_X + 107, self._JP_Y + 85, 2, 44),
                         QColor(255, 255, 255, int(0.3 * 255)))

        # Panel label at bottom
        painter.setPen(QColor('#6c7086'))
        font = QFont('Segoe UI', 7)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(self._JP_X, self._JP_Y + 212, self._JP_W, 14),
                         Qt.AlignmentFlag.AlignHCenter, 'BOLTED JOINT')
```

- [ ] **Step 3: Call from paintEvent**

```python
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        painter.end()
```

- [ ] **Step 4: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Two stacked hatched flanges with pink parting line, shank above them, pink centre line running full panel height, "BOLTED JOINT" label at bottom.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw joint panel static elements (flanges, shank, centreline, label)"
```

---

### Task 7: Joint panel — animated threads (scrolling pattern + zigzag silhouette)

Threads live in a 20 × 66 rectangle below the shank. Pattern scrolls down 6 px (one pitch) per 15 s. Zigzag silhouette on both vertical edges scrolls in sync.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_threads` method**

```python
    # Thread animation timing (seconds per pitch / revolution)
    NUT_PERIOD_S = 15.0
    PITCH_PX = 6.0

    def _draw_threads(self, painter: QPainter, t: float) -> None:
        """Threads below the shank, scrolling down at 1 pitch / NUT_PERIOD_S."""
        thread_x = self._JP_X + 100
        thread_y = self._JP_Y + 129
        thread_w = 20
        thread_h = 66
        thread_rect = QRectF(thread_x, thread_y, thread_w, thread_h)

        scroll = (t / self.NUT_PERIOD_S) * self.PITCH_PX
        scroll = scroll % self.PITCH_PX   # stay within 0..6

        painter.save()
        painter.setClipRect(thread_rect)

        # Draw the tiled pattern, starting PITCH_PX above thread_y so scroll has room
        pattern_y_start = thread_y - self.PITCH_PX + scroll
        y = pattern_y_start
        while y < thread_y + thread_h:
            self._draw_thread_pitch(painter, thread_x, y, thread_w)
            y += self.PITCH_PX

        # Zigzag silhouettes — left and right edges, same scroll
        painter.setBrush(QColor('#1e1e2e'))
        pen = QPen(QColor('#0a0a10'))
        pen.setWidthF(0.4)
        painter.setPen(pen)

        # Left edge: sawtooth going from x=thread_x out to x=thread_x-3
        left = QPainterPath()
        left.moveTo(thread_x, pattern_y_start)
        yy = pattern_y_start
        while yy < thread_y + thread_h + self.PITCH_PX:
            left.lineTo(thread_x - 3, yy + 3)
            left.lineTo(thread_x,     yy + 6)
            yy += 6
        painter.drawPath(left)

        # Right edge: mirror — from x=thread_x+w out to x=thread_x+w+3
        right = QPainterPath()
        right.moveTo(thread_x + thread_w, pattern_y_start)
        yy = pattern_y_start
        while yy < thread_y + thread_h + self.PITCH_PX:
            right.lineTo(thread_x + thread_w + 3, yy + 3)
            right.lineTo(thread_x + thread_w,     yy + 6)
            yy += 6
        painter.drawPath(right)

        painter.restore()

        # Border around thread column
        painter.setPen(QPen(QColor('#313244'), 0.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(thread_rect)

    def _draw_thread_pitch(self, painter: QPainter,
                            x: float, y: float, w: float) -> None:
        """One 6-px-tall pitch unit: gradient background + root + crest bands."""
        unit = QRectF(x, y, w, self.PITCH_PX)
        painter.fillRect(unit, QBrush(self._steel_gradient(x, w)))
        # Dark root band at top (1.5 px)
        painter.fillRect(QRectF(x, y,         w, 1.5),
                         QColor(0, 0, 0, int(0.55 * 255)))
        # White crest highlight (0.8 px) at y+3
        painter.fillRect(QRectF(x, y + 3.0,   w, 0.8),
                         QColor(255, 255, 255, int(0.75 * 255)))
        # Crest fade (0.4 px) at y+3.8
        painter.fillRect(QRectF(x, y + 3.8,   w, 0.4),
                         QColor(255, 255, 255, int(0.30 * 255)))
```

- [ ] **Step 2: Wire into paintEvent**

Pass `t = time.monotonic() - self._start_time` to the thread method:

```python
    def paintEvent(self, event) -> None:
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        self._draw_threads(painter, t)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Thread pattern visible below shank, slowly scrolling downward. Zigzag silhouette on both sides.

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw scrolling thread pattern with zigzag silhouette (1 pitch / 15 s)"
```

---

### Task 8: Shared hex-prism renderer

A helper method that draws a rotating/static hex prism at any screen position, using the `project_hex_faces` math from Task 2 and a parameterisable gradient colour set. Consumed by the nut (Task 9) and head (Task 10).

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_hex_prism` method**

```python
    # Hex-prism geometry (shared by nut and head)
    HEX_R = 26.0   # circumradius
    HEX_W = 30.0   # face width

    def _draw_hex_prism(self,
                        painter: QPainter,
                        cx: float, top_y: float,
                        height: float,
                        theta_deg: float,
                        gradient_stops: list) -> None:
        """Draw 6-faced hex prism centred at (cx, top_y) with given face height.

        Args:
            gradient_stops: list of (offset 0..1, '#hex') tuples for the
                vertical per-face gradient.
        """
        faces = project_hex_faces(theta_deg, self.HEX_R, self.HEX_W)
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

            # Top highlight + bottom shadow (1.5 px each)
            painter.fillRect(QRectF(x, top_y, w, 1.5),
                             QColor(gradient_stops[0][1]))
            painter.fillRect(QRectF(x, top_y + height - 1.5, w, 1.5),
                             QColor(gradient_stops[-1][1]))
```

- [ ] **Step 2: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/splash.py', encoding='utf-8').read()); print('OK')"
pytest tests/test_splash.py -v
```
Expected: `OK` + all tests still green.

- [ ] **Step 3: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Add shared hex-prism renderer using face projection math"
```

---

### Task 9: Bolt head (static hex prism, gray gradient)

Static 3D hex head at (cx=110, top=52 within panel), 33 px tall.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_head` method**

```python
    _HEAD_GRADIENT = [
        (0.0,  '#f5f5ff'),
        (0.2,  '#cdd6f4'),
        (0.5,  '#9399b2'),
        (0.8,  '#585b70'),
        (1.0,  '#313244'),
    ]

    def _draw_head(self, painter: QPainter) -> None:
        cx = self._AXIS_X
        top = self._JP_Y + 52
        self._draw_hex_prism(painter,
                             cx=cx, top_y=top, height=33,
                             theta_deg=0.0,
                             gradient_stops=self._HEAD_GRADIENT)
```

- [ ] **Step 2: Wire into paintEvent (call before threads so head doesn't overlay them, before nut so nut can overlay head later)**

Order matters: static joint → head → threads → nut. For now:

```python
    def paintEvent(self, event) -> None:
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        self._draw_head(painter)
        self._draw_threads(painter, t)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Gray 3D-looking hex head above the top flange.

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw static bolt head as 3D hex prism (gray gradient)"
```

---

### Task 10: Nut (rotating hex prism with axial descent, brass gradient)

Flush against bottom flange at (cx=110, top=127). Rotates 360° and descends 3 px per 15 s.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_nut` method**

```python
    _NUT_GRADIENT = [
        (0.0,  '#fff5c7'),
        (0.3,  '#f9e2af'),
        (0.6,  '#e5c989'),
        (1.0,  '#9a804a'),
    ]
    NUT_DESCENT_PX = 3.0   # total axial travel per NUT_PERIOD_S

    def _draw_nut(self, painter: QPainter, t: float) -> None:
        phase = (t % self.NUT_PERIOD_S) / self.NUT_PERIOD_S   # 0..1
        theta_deg = phase * 360.0
        delta_y  = phase * self.NUT_DESCENT_PX
        cx = self._AXIS_X
        top = self._JP_Y + 127 + delta_y
        self._draw_hex_prism(painter,
                             cx=cx, top_y=top, height=24,
                             theta_deg=theta_deg,
                             gradient_stops=self._NUT_GRADIENT)
```

- [ ] **Step 2: Wire into paintEvent (after threads so nut sits on top of them)**

```python
    def paintEvent(self, event) -> None:
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        self._draw_head(painter)
        self._draw_threads(painter, t)
        self._draw_nut(painter, t)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Brass-coloured nut flush against bottom flange, slowly rotating around vertical axis (faces cycle past) and descending very slightly each revolution.

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw rotating brass nut with subtle axial descent (15 s/rev, 3 px)"
```

---

### Task 11: Preload arrows (pulsing green F₀ arrows)

Two green down-arrows at x=48 and x=172 (relative to joint panel), with opacity pulsing sinusoidally between .55 and 1.0 over 2.4 s.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_preload_arrows` method**

```python
    PRELOAD_PERIOD_S = 2.4

    def _draw_preload_arrows(self, painter: QPainter, t: float) -> None:
        # Sinusoidal opacity pulse .55 → 1.0 → .55
        phase = (t / self.PRELOAD_PERIOD_S) * 2 * math.pi
        opacity = 0.55 + 0.45 * (0.5 - 0.5 * math.cos(phase))

        painter.save()
        painter.setOpacity(opacity)

        pen = QPen(QColor('#a6e3a1'))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        font = QFont('Segoe UI', 7)
        painter.setFont(font)

        for x in (self._JP_X + 48, self._JP_X + 172):
            # Arrow shaft
            painter.drawLine(QPointF(x, self._JP_Y + 22),
                             QPointF(x, self._JP_Y + 45))
            # Arrowhead
            head = QPainterPath()
            head.moveTo(x - 4, self._JP_Y + 41)
            head.lineTo(x,     self._JP_Y + 45)
            head.lineTo(x + 4, self._JP_Y + 41)
            painter.drawPath(head)
            # Label
            painter.drawText(QRectF(x - 10, self._JP_Y + 8, 20, 12),
                             Qt.AlignmentFlag.AlignHCenter, 'F₀')

        painter.restore()
```

- [ ] **Step 2: Wire into paintEvent**

Add after the nut:

```python
        self._draw_nut(painter, t)
        self._draw_preload_arrows(painter, t)
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Two green down-arrows labelled "F₀" above the top flange, pulsing softly.

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw pulsing preload arrows above top flange"
```

---

### Task 12: Curve panel — static axes, gridlines, labels

Panel origin (292, 100), size 320 × 200. Coordinate system inside the panel: (0,0) top-left.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_curve_static` method**

```python
    # Curve panel origin in splash coordinates
    _CP_X = 292
    _CP_Y = 100
    _CP_W = 320
    _CP_H = 200

    def _draw_curve_static(self, painter: QPainter) -> None:
        x0 = self._CP_X
        y0 = self._CP_Y

        # Gridlines (very subtle)
        pen = QPen(QColor(205, 214, 244, int(0.18 * 255)))
        pen.setWidthF(0.5)
        painter.setPen(pen)
        for gy in (30, 65, 100, 135):
            painter.drawLine(QPointF(x0 + 30,  y0 + gy),
                             QPointF(x0 + 300, y0 + gy))
        for gx in (90, 150, 210, 270):
            painter.drawLine(QPointF(x0 + gx, y0 + 20),
                             QPointF(x0 + gx, y0 + 170))

        # Reference line "F₀" at y=30
        pen = QPen(QColor('#a6e3a1'))
        pen.setWidthF(1.0)
        pen.setDashPattern([3, 2])
        painter.setPen(pen)
        painter.setOpacity(0.7)
        painter.drawLine(QPointF(x0 + 30, y0 + 30), QPointF(x0 + 110, y0 + 30))
        painter.setOpacity(1.0)
        painter.setPen(QColor('#a6e3a1'))
        painter.setFont(QFont('Segoe UI', 7))
        painter.drawText(QPointF(x0 + 14, y0 + 33), 'F₀')

        # Axis lines
        pen = QPen(QColor('#9399b2'))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawLine(QPointF(x0 + 30, y0 + 20),  QPointF(x0 + 30,  y0 + 170))
        painter.drawLine(QPointF(x0 + 30, y0 + 170), QPointF(x0 + 310, y0 + 170))

        # Axis labels (italic F, N)
        font = QFont('Segoe UI', 8, italic=True)
        painter.setFont(font)
        painter.drawText(QPointF(x0 + 18,  y0 + 25),  'F')
        painter.drawText(QPointF(x0 + 305, y0 + 185), 'N')

        # Stage labels
        painter.setFont(QFont('Segoe UI', 7))
        painter.setPen(QColor('#89b4fa'))
        painter.drawText(QRectF(x0 + 30, y0 + 8, 80, 12),
                         Qt.AlignmentFlag.AlignHCenter, 'Stage I')
        painter.setPen(QColor('#f38ba8'))
        painter.drawText(QRectF(x0 + 180, y0 + 8, 80, 12),
                         Qt.AlignmentFlag.AlignHCenter, 'Stage II')

        # Stage divider dashed vertical at x=115
        pen = QPen(QColor('#6c7086'))
        pen.setWidthF(0.5)
        pen.setDashPattern([2, 2])
        painter.setPen(pen)
        painter.setOpacity(0.5)
        painter.drawLine(QPointF(x0 + 115, y0 + 12), QPointF(x0 + 115, y0 + 170))
        painter.setOpacity(1.0)

        # Panel label
        painter.setPen(QColor('#6c7086'))
        font = QFont('Segoe UI', 7)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(x0, y0 + 188, self._CP_W, 14),
                         Qt.AlignmentFlag.AlignHCenter,
                         'PRELOAD DECAY · F/F₀ vs CYCLES')
```

- [ ] **Step 2: Wire into paintEvent (before nut so the curve doesn't cover the joint's preload arrows — actually curve is on right side so order doesn't matter visually; put it after _draw_joint for logical order)**

```python
        self._draw_nut(painter, t)
        self._draw_preload_arrows(painter, t)
        self._draw_curve_static(painter)
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Right-side chart panel with axes, grid, F₀ reference line, Stage I/II labels, dashed divider, panel label.

- [ ] **Step 4: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw curve panel static elements (axes, grid, stage labels, F₀ line)"
```

---

### Task 13: Curve panel — animated decay curve + travelling marker

The curve is a single QPainterPath that progressively reveals via a growing clip rectangle. The marker is a yellow glowing circle positioned along the sampled path.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add curve path construction in `__init__`**

In `__init__`, after the timer setup, add:

```python
        self._curve_path = self._build_decay_path()
        self._curve_samples = sample_path(self._curve_path, n=100)
```

And add the builder method:

```python
    def _build_decay_path(self) -> QPainterPath:
        """Construct the preload decay curve in panel-local coordinates,
        then offset to splash coordinates (CP_X, CP_Y)."""
        p = QPainterPath()
        # Points from spec §4.4.3
        p.moveTo(self._CP_X + 30,  self._CP_Y + 30)
        p.lineTo(self._CP_X + 90,  self._CP_Y + 30)
        p.quadTo(self._CP_X + 130, self._CP_Y + 30,
                 self._CP_X + 155, self._CP_Y + 65)
        p.quadTo(self._CP_X + 205, self._CP_Y + 140,
                 self._CP_X + 260, self._CP_Y + 158)
        p.quadTo(self._CP_X + 290, self._CP_Y + 167,
                 self._CP_X + 308, self._CP_Y + 168)
        return p
```

- [ ] **Step 2: Add `_draw_curve_animated` method**

```python
    CURVE_PERIOD_S = 3.2

    def _draw_curve_animated(self, painter: QPainter, t: float) -> None:
        # Phase 0..1: ease-out for draw, hold from 0.85 to 1.0
        phase = (t % self.CURVE_PERIOD_S) / self.CURVE_PERIOD_S
        if phase < 0.85:
            progress = phase / 0.85
            progress = 1.0 - (1.0 - progress) ** 3   # ease-out cubic
        else:
            progress = 1.0

        # Clip to progressively-growing rectangle starting at left axis
        x_start = self._CP_X + 30
        x_end   = self._CP_X + 310
        x_now   = x_start + progress * (x_end - x_start)

        painter.save()
        painter.setClipRect(QRectF(x_start, self._CP_Y + 20,
                                   x_now - x_start, 150))

        # Stroked curve with horizontal gradient
        grad = QLinearGradient(self._CP_X + 30, 0, self._CP_X + 308, 0)
        grad.setColorAt(0.0, QColor('#a6e3a1'))
        grad.setColorAt(0.5, QColor('#f9e2af'))
        grad.setColorAt(1.0, QColor('#f38ba8'))
        pen = QPen(QBrush(grad), 2.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._curve_path)

        painter.restore()

        # Travelling marker — at sampled index corresponding to progress
        if progress > 0.02:
            idx = int(progress * (len(self._curve_samples) - 1))
            pt = self._curve_samples[idx]
            # Glow (outer semi-transparent)
            painter.setBrush(QColor(249, 226, 175, int(0.35 * 255)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pt, 8, 8)
            # Core
            painter.setBrush(QColor('#f9e2af'))
            painter.drawEllipse(pt, 4, 4)
```

- [ ] **Step 3: Wire into paintEvent (after curve_static)**

```python
        self._draw_curve_static(painter)
        self._draw_curve_animated(painter, t)
```

- [ ] **Step 4: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: Curve progressively draws from left to right with a yellow glowing marker travelling along it, resets every 3.2 s.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw progressive preload decay curve with travelling marker"
```

---

### Task 14: Progress bar (sweeping fill at bottom)

Sweeping bar with 2.2 s period, translateX from -100% to +250% of its own width. Label underneath.

**Files:**
- Modify: `src/bolt_analysis_studio/gui/splash.py`

- [ ] **Step 1: Add `_draw_progress` method**

```python
    PROGRESS_PERIOD_S = 2.2

    def _draw_progress(self, painter: QPainter, t: float) -> None:
        track_left   = 80
        track_right  = self.WIDTH - 80
        track_width  = track_right - track_left
        track_top    = self.HEIGHT - 18 - 4
        track_height = 4

        # Track (rounded)
        track_rect = QRectF(track_left, track_top, track_width, track_height)
        painter.setBrush(QColor(49, 50, 68, int(0.8 * 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 2, 2)

        # Sweeping fill — 40% width, animated X translation
        fill_width = 0.40 * track_width
        phase = (t % self.PROGRESS_PERIOD_S) / self.PROGRESS_PERIOD_S
        # Ease-in-out approximation
        eased = 0.5 - 0.5 * math.cos(math.pi * phase)
        # Translate from -100% of own width to 250% of own width
        translate = -fill_width + eased * 3.5 * fill_width

        painter.save()
        painter.setClipRect(track_rect)   # stay inside track
        fill_rect = QRectF(track_left + translate, track_top,
                           fill_width, track_height)
        grad = QLinearGradient(fill_rect.left(), 0, fill_rect.right(), 0)
        grad.setColorAt(0.0, QColor(137, 180, 250, 0))
        grad.setColorAt(0.3, QColor('#89b4fa'))
        grad.setColorAt(0.7, QColor('#a6e3a1'))
        grad.setColorAt(1.0, QColor(166, 227, 161, 0))
        painter.fillRect(fill_rect, QBrush(grad))
        painter.restore()

        # Loading label
        painter.setPen(QColor('#a6e3a1'))
        font = QFont('Segoe UI', 8)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(font)
        painter.drawText(QRectF(0, self.HEIGHT - 14, self.WIDTH, 14),
                         Qt.AlignmentFlag.AlignHCenter,
                         'INITIALISING MODULES…')
```

- [ ] **Step 2: Wire into paintEvent (last layer — always on top)**

```python
    def paintEvent(self, event) -> None:
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_static(painter)
        self._draw_head(painter)
        self._draw_threads(painter, t)
        self._draw_nut(painter, t)
        self._draw_preload_arrows(painter, t)
        self._draw_curve_static(painter)
        self._draw_curve_animated(painter, t)
        self._draw_progress(painter, t)
        painter.end()
```

- [ ] **Step 3: Visual smoke test**

Run: `python -m bolt_analysis_studio.gui.splash`
Expected: All layers composed — full splash matches the v7 mockup. Progress bar sweeps continuously at the bottom.

- [ ] **Step 4: Syntax + all tests green**

Run:
```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/splash.py', encoding='utf-8').read()); print('OK')"
pytest tests/test_splash.py -v
```
Expected: `OK` + all tests green.

- [ ] **Step 5: Commit**

```bash
git add src/bolt_analysis_studio/gui/splash.py
git commit -m "Draw sweeping progress bar with loading label (all layers composed)"
```

---

### Task 15: Integrate splash into `run_app.py`

Replace the static QPixmap block with the new animated splash.

**Files:**
- Modify: `run_app.py:81–127`

- [ ] **Step 1: Replace the splash block**

Currently lines 81–127 look like (from the existing file):

```python
    # --- Splash screen ---
    import time
    _splash_start = time.monotonic()
    _SPLASH_MIN_SECONDS = 5.0
    if not args.builder:
        _splash_w, _splash_h = 480, 260
        _pix = QPixmap(_splash_w, _splash_h)
        _pix.fill(QColor("#1e1e2e"))
        _p = QPainter(_pix)
        # ... ~40 lines of static rendering ...
        _p.end()

        _splash = QSplashScreen(_pix)
        _splash.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint)
        _splash.show()
        app.processEvents()
    else:
        _splash = None
```

Replace with:

```python
    # --- Splash screen ---
    import time
    _splash_start = time.monotonic()
    _SPLASH_MIN_SECONDS = 5.0
    if not args.builder:
        from bolt_analysis_studio.gui.splash import AnimatedSplashScreen
        _splash = AnimatedSplashScreen()
        _splash.show()
        app.processEvents()
    else:
        _splash = None
```

The existing imports `QPixmap, QColor, QFont, QPainter` become unused on line 67; trim them out if they're not referenced elsewhere in the file. (Verify with grep — if still used anywhere in `run_app.py`, leave them.)

- [ ] **Step 2: Grep for leftover imports**

Run: `grep -nE "QPixmap|QFont|QPainter|QSplashScreen|QLabel" run_app.py`

If any references outside the splash block remain, keep those imports. If not, trim the import line at run_app.py:66–68 to what's actually used (`QApplication`, `QGuiApplication`, `QTimer`, `Qt`, `QColor` may still be referenced).

- [ ] **Step 3: Syntax check run_app.py**

Run: `python -c "import ast; ast.parse(open('run_app.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Launch both execution paths**

Run: `python run_app.py`
Expected: Animated splash appears for ≥5 s, then main window opens.

Run: `python run_app.py --builder`
Expected: No splash — MSD Builder window opens directly.

- [ ] **Step 5: Commit**

```bash
git add run_app.py
git commit -m "Replace static splash with AnimatedSplashScreen"
```

---

### Task 16: Final acceptance checklist

Walk through the acceptance criteria from the spec §9. This is a manual verification step — no code changes unless a failure is found.

**Files:** none modified.

- [ ] **Step 1: Verify each acceptance criterion**

```
[ ] python run_app.py shows splash within ~200 ms of process start
[ ] Animations run smoothly (no visible stuttering) for the full 5 s
[ ] Nut visibly rotates (faces cycle past) over 15 s, descends ~3 px per cycle
[ ] Thread pattern scrolls in sync with nut (one pitch per revolution)
[ ] Decay curve progressively draws 0 → full in 3.2 s, marker tracks it, loops
[ ] Progress bar sweeps continuously (2.2 s loop)
[ ] Preload arrows pulse softly (2.4 s loop)
[ ] Splash holds ≥ 5 s, then hands off to main window via finish()
[ ] python run_app.py --builder still works (no splash, MSD Builder opens)
[ ] No new package dependencies introduced (pyproject / setup.py unchanged)
[ ] Syntax checks pass for both splash.py and run_app.py
```

- [ ] **Step 2: Performance sanity check**

Watch Task Manager CPU% during the splash on a single-core thread — should be <5 % on a 2020-era laptop.

- [ ] **Step 3: If any check fails, file a follow-up task**

Report the failure with the exact criterion that didn't hold and the observed behaviour. Do NOT mark this plan complete until all boxes check.

- [ ] **Step 4: If all pass, close out**

Run: `git log --oneline -17`
Expected: 16 commits visible — one per task above, in order.

No commit for Task 16 itself (it's verification-only).

---

## Notes for the executor

- The spec at `docs/superpowers/specs/2026-04-22-animated-splash-design.md` is the visual authority. If the code in this plan conflicts with it, treat the spec as correct and flag the conflict.
- All colours are Catppuccin Mocha hex codes — don't substitute "close enough" colours from memory.
- `QT_QPA_PLATFORM=offscreen` is needed for CI / headless test runs; set it in `tests/test_splash.py` before importing PyQt6 (already done in the Task 1 test file).
- The existing `tests/test_gui.py` has pre-existing fixture issues unrelated to this work — skip it if it fails, don't try to fix it.
- Don't skip commits. Each task's final step is a commit; the plan is designed so partial state is runnable.
- Windows-specific: always open files with `encoding='utf-8'` in any file I/O code you add (already done in the syntax-check commands).
