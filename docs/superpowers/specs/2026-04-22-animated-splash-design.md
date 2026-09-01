# Animated Splash Screen — Design Spec

**Date:** 2026-04-22
**Author:** Prof. Leonardo Rosa Ribeiro da Silva, PhD (with Claude)
**Status:** Approved for implementation planning

---

## 1. Goal

Replace the current static splash in `run_app.py:81–127` with an animated splash that narrates the application's core subject — bolted-joint self-loosening — while the app initialises.

The splash must:
- Launch in under 200 ms (cold start from `python run_app.py` to window visible).
- Hold on screen for the existing 5-second minimum (`_SPLASH_MIN_SECONDS = 5.0`).
- Animate smoothly at 60 fps on modest hardware.
- Depend only on PyQt6 — no new dependencies.

## 2. Visual reference

The approved design is the v7 mockup:
`.superpowers/brainstorm/1510-1776902983/content/joint-v7.html`

Keep it open during implementation — the spec below describes it precisely but the mockup is the authority for colour, placement, and proportion.

## 3. Architecture

### 3.1 Approach: pure QPainter + QTimer

A new `AnimatedSplashScreen` class subclassing `QWidget` (not `QSplashScreen` — we need full custom paint control). A single `QTimer` at ~16 ms drives `update()`, which schedules `paintEvent()`. The paint event draws every layer from scratch each frame, using a single monotonically-increasing frame counter as the animation phase.

Rejected alternatives: `QWebEngineView` (adds ~40 MB and ~500 ms launch cost); hybrid SVG (the 3D nut still needs painter-math anyway).

### 3.2 File structure

- **New:** `src/bolt_analysis_studio/gui/splash.py` — contains `AnimatedSplashScreen` class and standalone render helpers.
- **Modified:** `run_app.py:81–127` — replace the QPixmap/QPainter block with `AnimatedSplashScreen()` instantiation. The `_SPLASH_MIN_SECONDS = 5.0` gate and `_splash.finish(window)` handoff stay.

### 3.3 Window setup

```python
self.setWindowFlags(
    Qt.WindowType.SplashScreen
    | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.FramelessWindowHint
)
self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
self.setFixedSize(640, 360)
# Centre on primary screen
screen = QGuiApplication.primaryScreen().geometry()
self.move((screen.width() - 640) // 2, (screen.height() - 360) // 2)
```

Size bumped 480×260 → 640×360 to match the mockup and give the joint + curve room to breathe.

## 4. Component breakdown

Each subsection describes one draw layer. `paintEvent()` composes them in Z order (back to front).

### 4.1 Background

- Outer rounded rect, radius 12 px.
- Base fill: linear gradient `#1e1e2e → #181825`, 145° angle.
- Two radial highlights: ellipse at (30%, 20%) and (80%, 90%), colour `#313244`, fading to transparent.
- 20-px grid overlay in `rgba(205,214,244,.025)` — subtle, helps readability.
- 1-px border `rgba(205,214,244,.08)`.
- Outer drop shadow `0 20 50 rgba(0,0,0,.55)`.

### 4.2 Title stack (top-centre)

- **"BOLT ANALYSIS STUDIO"** — Segoe UI Bold 26 pt, vertical gradient `#ffffff → #a6adc8`, 2 px glow in `rgba(137,180,250,.25)`.
- **"v4.0 · Bolted Joint Self-Loosening Analysis"** — 11 pt, colour `#89b4fa`.
- **"Prof. Leonardo Rosa Ribeiro da Silva, PhD"** — 10 pt, colour `#6c7086`.

All centred, stacked with 4 px line spacing, top edge at y = 22 px.

### 4.3 Joint panel (left half)

Panel origin: `(36, 90)`, size `220 × 240`. Perspective for 3D elements: observer ~800 px in front of panel centre.

#### 4.3.1 Flanges (static)
Two hatched rectangles, 150 × 22 px, at `y = 85` and `y = 107`. Vertical gradient `#585b70 → #9399b2 → #45475a` overlaid with 45° hatch pattern `#6c7086` at `.6` opacity. Pink parting line `#f38ba8` between them (the "flange interface" centre-line convention).

#### 4.3.2 Shank (static)
20 × 44 px rectangle at `(100, 85)`, horizontal steel gradient `#45475a → #a6adc8 → #f5f5ff → #7f849c → #313244`. Thin white highlight stripe at `x = 107`.

#### 4.3.3 Threads (animated)
20 × 66 px rectangle at `(100, 129)`. Fill: 20 × 6 px tiled pattern — one pitch unit:
- Steel horizontal gradient background
- 1.5 px dark band at top (`#000` at .55 opacity) = root
- 0.8 px white band at y = 3 (`#ffffff` at .75) = crest highlight
- 0.4 px white band at y = 3.8 (at .3 opacity) = crest fade

Zigzag silhouette: two `QPainterPath`s for left/right edges, sawtooth profile (3 px horizontal amplitude, 6 px vertical period = one pitch unit), fill `#1e1e2e`, stroke `#0a0a10`.

**Animation:** both the threaded fill and the zigzag edges translate vertically by `-6 px` (one pitch) per 15 s, clipped to the 20 × 66 thread rectangle. Continuous scroll — resets imperceptibly because the pattern is periodic.

#### 4.3.4 Bolt head (static 3D)
Hex prism at `(top = 52, centre_x = 110)`, width 52 px, height 33 px. Transform `rotateX(18°) rotateY(0°)` — static tilt, no rotation.

See §5 for the hex-prism math. Gradient per face: vertical `#f5f5ff → #cdd6f4 → #9399b2 → #585b70 → #313244`. Drop shadow `(0, 2, 3, rgba(0,0,0,.55))`.

#### 4.3.5 Nut (animated 3D)
Same hex prism construction, at `(top = 127, centre_x = 110)`, width 52 px, height 24 px. Flush against bottom flange (no gap).

Gradient per face: vertical `#fff5c7 → #f9e2af → #e5c989 → #9a804a` (brass/gold).

**Animation (15 s loop):**
- `rotateY`: 0° → 360° linear
- `translateY`: 0 → 3 px linear (axial back-off = self-loosening motion)
- `rotateX`: constant 18° (perspective tilt)

Thread scroll and nut rotation run at the same 15 s period so one full nut revolution corresponds to one pitch of thread translation — physically consistent.

#### 4.3.6 Preload arrows (animated)
Two green down-arrows at `x = 48` and `x = 172`, `y = 22 → 45`, stroke `#a6e3a1`, 1.5 px. Label "F₀" above each.

**Animation:** opacity sinusoid `.55 → 1 → .55` over 2.4 s.

#### 4.3.7 Centre line (static)
Vertical pink dashed line at `x = 110`, `y = 10 → 230`, stroke `#f38ba8`, 0.6 px, dash pattern `5 2 1 2`, opacity .65 (engineering-drawing centre-line convention).

#### 4.3.8 Panel label (static)
"BOLTED JOINT" at the bottom of the panel, 9 pt, `#6c7086`, 1 px letter-spacing.

### 4.4 Curve panel (right half)

Panel origin: `(292, 100)` (derived from `right: 28` in mockup CSS: 640 − 28 − 320 = 292), size `320 × 200`.

#### 4.4.1 Axes and gridlines
- Axis lines at `x = 30` (y-axis) and `y = 170` (x-axis), stroke `#9399b2`, 1 px.
- 4 horizontal + 4 vertical gridlines, stroke `#cdd6f4` at .18 opacity, 0.5 px.
- Axis labels: italic "F" at top-left, "N" at bottom-right, 10 pt, `#9399b2`.
- Reference line "F₀" at y = 30 (initial preload), dashed `3 2`, `#a6e3a1`.

#### 4.4.2 Stage annotations
- "Stage I" label above left portion, `#89b4fa`, 8 pt.
- "Stage II" label above right portion, `#f38ba8`, 8 pt.
- Vertical divider dashed at x = 115, `#6c7086`, 0.5 px, opacity .5.

#### 4.4.3 Decay curve (animated)
`QPainterPath`:
```
M 30 30
L 90 30
Q 130 30 155 65
Q 205 140 260 158
Q 290 167 308 168
```
Stroke: horizontal gradient `#a6e3a1 → #f9e2af → #f38ba8` (green-yellow-red), 2.8 px, round cap. Glow: 4 px yellow drop shadow.

**Animation (3.2 s loop):** progressive reveal — `stroke-dasharray` technique. Full path length computed once; dash offset animates from `path_length` (invisible) to `0` (fully drawn) with ease-out curve, holds at drawn state for ~15 % of the cycle before restarting.

In QPainter terms: use `QPainterPathStroker` with a custom dash pattern, or simpler — clip-path rectangle whose width grows 0 → 320 px. Go with the clip-path rectangle; simpler and equivalent.

#### 4.4.4 Travelling marker (animated)
4 px yellow circle (`#f9e2af`), 6 px glow. Position follows the curve path with the same 3.2 s timing. Implementation: compute N sample points along the path at load time (N ≈ 100); marker position = sample at index `floor((t / 3.2) × N)`.

#### 4.4.5 Panel label (static)
"PRELOAD DECAY · F/F₀ vs CYCLES" below the chart, 9 pt, `#6c7086`, 1 px letter-spacing.

### 4.5 Progress bar (bottom)

Location: `bottom = 18, left = 80, right = 80`.

- Track: 4 px rounded rectangle, fill `rgba(49,50,68,.8)`, inset 1 px border.
- Fill: 40% width of track, horizontal gradient `transparent → #89b4fa → #a6e3a1 → transparent`. 4 px green glow.
- **Animation (2.2 s loop):** translate X from -100% to 250% of own width, ease-in-out — Knight-Rider sweep.
- Label below: "INITIALISING MODULES…", 11 pt, `#a6e3a1`, centred.

## 5. 3D hex-prism math (nut and head)

The hex prism is six vertical rectangular faces arranged around a central axis. In the mockup, CSS 3D transforms handle this. In QPainter we project manually.

### 5.1 Geometry

- Hex circumradius (face centre distance from axis): `R = 26 px` (half the outer width).
- Face width: `W = 30 px`.
- Face angular offsets: `θ_face = [0°, 60°, 120°, 180°, 240°, 300°]`.
- Global rotation: `θ = frame_time × 360° / 15 s` (nut) or `θ = 0` (head).
- Tilt: `φ = 18°` about x-axis.

### 5.2 Projection per face

For each face at angle `θ_face`, its effective angle is `α = θ + θ_face`.

Project to screen:
- Horizontal centre offset: `cx = R × sin(α)` — where the face centre lands relative to prism axis.
- Apparent width: `w = W × |cos(α)|` — foreshortening; faces perpendicular to viewer are full width, faces edge-on collapse to zero.
- Visibility: face is visible only when `cos(α) > 0` (front-facing).

Depth for Z sort: `z = R × cos(α)`.

### 5.3 Render order

1. Compute `(cx, w, z, θ_face)` for all 6 faces.
2. Filter to visible (`cos(α) > 0`).
3. Sort by `z` ascending (back to front).
4. Draw each as a filled rectangle: centre at `(prism_x + cx, prism_y)`, width `w`, full face height, with the vertical face gradient.
5. Add 1.5 px top-border highlight and 1.5 px bottom-border shadow on each.

### 5.4 Perspective tilt

The `rotateX(18°)` in CSS compresses the rendered height by `cos(18°) ≈ 0.95` and adds a tiny Y-shift. For a splash-screen-scale prism (24 or 33 px tall) this is visually negligible — we can skip the tilt entirely and just render flat rectangles. If the prism looks too "blocky" in playtesting, apply a 0.95× Y-scale and call it done. No full 3×3 matrix needed.

### 5.5 Axial descent

Nut-only: after computing the prism's screen position, add `delta_y = 3 × (t mod 15) / 15` px to the y coordinate of every face.

## 6. Animation timings

| Element | Period | Type |
|---------|--------|------|
| Nut rotation + descent | 15 s | Linear, loops |
| Thread scroll | 15 s | Linear, loops (synchronised to nut) |
| Preload arrows pulse | 2.4 s | Ease-in-out |
| Decay curve draw | 3.2 s | Ease-out, loops |
| Travelling marker | 3.2 s | Ease-out, loops (sync'd to curve) |
| Progress sweep | 2.2 s | Ease-in-out, loops |

All times derive from a single `frame_time` float (seconds since splash start) using `fmod`. No multi-timer complexity.

## 7. Frame loop

```python
class AnimatedSplashScreen(QWidget):
    FRAME_INTERVAL_MS = 16   # ~60 fps

    def __init__(self):
        super().__init__()
        # ... window flags, size, position ...
        self._start_time = time.monotonic()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(self.FRAME_INTERVAL_MS)
        # Pre-compute curve sample points (100 samples along the QPainterPath)
        self._curve_path = self._build_decay_path()
        self._curve_samples = self._sample_path(self._curve_path, 100)

    def paintEvent(self, event):
        t = time.monotonic() - self._start_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_background(painter)
        self._draw_title(painter)
        self._draw_joint_panel(painter, t)
        self._draw_curve_panel(painter, t)
        self._draw_progress(painter, t)
        painter.end()

    def finish(self, main_window):
        """Called by run_app.py when main window is ready. Hides this splash."""
        self._timer.stop()
        self.close()
```

## 8. Integration with `run_app.py`

Replace lines 81–127 with:

```python
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

The rest — `_finish_splash()` and the `QTimer.singleShot` gate — stays unchanged. `AnimatedSplashScreen.finish(window)` signature matches `QSplashScreen.finish()` so the existing `_splash.finish(window)` call works.

## 9. Acceptance criteria

- [ ] `python run_app.py` shows the animated splash within 200 ms of process start.
- [ ] All animations run at 60 fps on a 2018-era laptop (no dropped frames visible).
- [ ] Nut visibly rotates and descends over 15 s; thread pattern scrolls in sync.
- [ ] Decay curve progressively draws, marker tracks the curve, both loop cleanly.
- [ ] Progress bar sweeps continuously.
- [ ] Splash holds for at least 5 s, then hands off to main window via `finish()`.
- [ ] `python run_app.py --builder` still works (no splash, MSD Builder opens directly).
- [ ] Syntax check passes: `python -c "import ast; ast.parse(open('src/bolt_analysis_studio/gui/splash.py', encoding='utf-8').read()); print('OK')"`.
- [ ] No new package dependencies introduced.

## 10. Out of scope

- Sound / audio cue on splash completion.
- Interactive elements (click-to-skip, etc.).
- Light-theme variant — splash stays dark-themed regardless of app theme. (Consistent with how most product splashes work; adding theme switching would double the asset work for no user benefit since the splash is 5 s.)
- Localisation of splash text. All strings hard-coded English.
- HiDPI-specific asset paths. QPainter vector drawing scales natively with DPI; we set `setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)` and let Qt handle the rest.
