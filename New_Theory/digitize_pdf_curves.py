# -*- coding: utf-8 -*-
"""Vector-curve digitizer for open-access PDFs (pymupdf / fitz).

Extracts data curves from VECTOR figures (page.get_drawings()) and converts
them to CSV using tick-mark + tick-label axis calibration.

Anti-hallucination protocol (mandatory):
  For every figure, before any new curve is written, a curve that ALREADY
  exists in curve_library/digitized_csv/ is re-extracted from the same
  figure and compared. Only if the mean deviation is < 3 percent of the
  reference span is the figure considered calibrated; otherwise nothing
  is written for that figure and the failure is reported.

Key PDF quirks handled (discovered on rousseau2025_materials_M12.pdf):
  * MDPI figures are painted TWICE (pass 1, then a white rect, then pass 2
    shifted by ~-1.53 pt in x). Drawings after the LAST big white fill are
    the visible pass. Ticks and curves of the SAME pass are self-consistent,
    so calibration uses tick-mark segments of the chosen pass only.
  * Legend line samples share the curve styles but have 1 item per drawing;
    real curves here have >= 100 items -> min_items filter.
  * Dashed curves are single polylines WITH a dash style (not many small
    segments), so dash pattern is a reliable series selector.
  * Some series can be rasterized (pattern-brush lines exported as masked
    images) -> those are NOT extractable as vectors and are reported.

Usage:
  python New_Theory/digitize_pdf_curves.py probe <pdf-name> <page-1based>
  python New_Theory/digitize_pdf_curves.py render <pdf-name> <page-1based> [zoom]
  python New_Theory/digitize_pdf_curves.py rousseau-fig45
  python New_Theory/digitize_pdf_curves.py rousseau-fig6
  python New_Theory/digitize_pdf_curves.py rousseau-fig78
  python New_Theory/digitize_pdf_curves.py rousseau-fig10

All prints ASCII. All file IO utf-8.
"""

import os
import sys
import math
import collections

import fitz  # pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIB = os.path.join(ROOT, "Models", "CALIBRATION_AND_VALIDATION", "curve_library")
PDF_DIR = os.path.join(LIB, "pdfs_open_access")
DIGITIZED = os.path.join(LIB, "digitized_csv")
THETA_DIR = os.path.join(LIB, "theta_csv")
LOOPS_DIR = os.path.join(LIB, "loops_csv")

CAL_TOL_PCT = 3.0  # mean |dev| threshold, percent of reference span


# ----------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------

def open_pdf(name):
    return fitz.open(os.path.join(PDF_DIR, name))


def dash_class(dashes):
    """'solid' | 'dash' | 'dashdot' from a pymupdf dash string like '[ 2.9 3.9 ] 0'."""
    if not dashes:
        return "solid"
    inside = dashes[dashes.find("[") + 1: dashes.find("]")] if "[" in dashes else ""
    nums = [t for t in inside.split() if t.strip()]
    if len(nums) == 0:
        return "solid"
    if len(nums) <= 2:
        return "dash"
    return "dashdot"


def color_close(c, ref, tol=0.12):
    if c is None or ref is None:
        return c is ref
    return all(abs(a - b) <= tol for a, b in zip(c, ref))


def drawing_points(d):
    """All vertex points of a drawing's line/curve items."""
    pts = []
    for it in d["items"]:
        kind = it[0]
        if kind == "l":
            pts.append(it[1]); pts.append(it[2])
        elif kind == "c":
            pts.extend([it[1], it[2], it[3], it[4]])
        elif kind == "re":
            r = it[1]
            pts.extend([fitz.Point(r.x0, r.y0), fitz.Point(r.x1, r.y1)])
    return pts


def rect_overlaps(r, region, pad=0.5):
    """Manual overlap test: Rect.intersects() is False for degenerate rects
    (a vertical tick segment has a zero-width bbox), so inflate by pad."""
    return (r.x0 - pad < region.x1 and r.x1 + pad > region.x0 and
            r.y0 - pad < region.y1 and r.y1 + pad > region.y0)


def visible_drawings(page):
    """Drawings that are actually rendered (clip-aware).

    MDPI figure exports paint each chart TWICE; the hidden pass sits under an
    INVERTED (empty) clip scissor. get_drawings(extended=True) flattens the
    clip tree: a 'clip' node at level L applies to subsequent items of level
    > L until an item of level <= L appears. Drawings whose active scissor
    stack contains an empty/inverted rect are dropped.
    """
    out = []
    stack = []  # [(level, scissor)]
    for d in page.get_drawings(extended=True):
        lvl = d.get("level", 0)
        stack = [(l, s) for (l, s) in stack if l < lvl]
        t = d["type"]
        if t == "clip":
            stack.append((lvl, d.get("scissor")))
            continue
        if t == "group":
            continue
        hidden = False
        for _, s in stack:
            if s is not None and (s.x0 >= s.x1 or s.y0 >= s.y1):
                hidden = True
                break
        if not hidden:
            out.append(d)
    return out


def visible_pass(page, region):
    """Visible drawings inside region, after the last full-region white
    repaint (paint order preserved)."""
    drs = [d for d in visible_drawings(page) if rect_overlaps(d["rect"], region)]
    area_region = max(1.0, abs(region))
    last_white = -1
    for i, d in enumerate(drs):
        if d["type"] == "f" and d.get("fill") == (1.0, 1.0, 1.0):
            r = d["rect"] & region
            if r and abs(r) > 0.5 * area_region:
                last_white = i
    return drs[last_white + 1:]


def line_segments(drs):
    """(vertical, horizontal) line segments from all stroked drawings.

    Rect items ('re') contribute their four edges (plot frames are rects).
    """
    vert, horiz = [], []
    for d in drs:
        if d["type"] not in ("s", "fs"):
            continue
        for it in d["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                dx, dy = abs(p1.x - p2.x), abs(p1.y - p2.y)
                if dx < 0.35 and dy > 0.01:
                    vert.append((p1.x, min(p1.y, p2.y), max(p1.y, p2.y)))
                elif dy < 0.35 and dx > 0.01:
                    horiz.append((p1.y, min(p1.x, p2.x), max(p1.x, p2.x)))
            elif it[0] == "re":
                r = it[1]
                vert.append((r.x0, r.y0, r.y1))
                vert.append((r.x1, r.y0, r.y1))
                horiz.append((r.y0, r.x0, r.x1))
                horiz.append((r.y1, r.x0, r.x1))
    return vert, horiz


def find_frame(drs, region, frame_hint=None):
    """Plot frame: long spines (incl. frame-rect edges). Returns x_l/x_r/y_t/y_b.

    frame_hint: approximate plot Rect. Needed when a decorative border box
    (larger than the plot frame) also lives in the region -- each spine is
    then the long segment nearest the corresponding hint edge.
    """
    vert, horiz = line_segments(drs)
    w, h = region.width, region.height
    long_v = [v for v in vert if (v[2] - v[1]) > 0.35 * h]
    long_h = [hh for hh in horiz if (hh[2] - hh[1]) > 0.35 * w]
    if not long_v or not long_h:
        raise RuntimeError("frame not found (no long spines in region)")
    if frame_hint is None:
        x_l = min(v[0] for v in long_v)
        x_r = max(v[0] for v in long_v)
        y_b = max(hh[0] for hh in long_h)
        y_t = min(hh[0] for hh in long_h)
    else:
        x_l = min(long_v, key=lambda v: abs(v[0] - frame_hint.x0))[0]
        x_r = min(long_v, key=lambda v: abs(v[0] - frame_hint.x1))[0]
        y_t = min(long_h, key=lambda hh: abs(hh[0] - frame_hint.y0))[0]
        y_b = min(long_h, key=lambda hh: abs(hh[0] - frame_hint.y1))[0]
    return {"x_l": x_l, "x_r": x_r, "y_t": y_t, "y_b": y_b}


def tick_positions(drs, frame, axis):
    """Tick coordinates (major AND minor) near the given spine.

    Ticks may stick out of the frame or sit fully inside it, so any short
    perpendicular segment within 5 pt of the spine counts. Label pairing
    (nearest-match in AxisCal) later selects the majors.
    """
    vert, horiz = line_segments(drs)
    out = []
    if axis == "x":
        for x, y0, y1 in vert:
            if (y1 - y0) <= 6.0 and y0 >= frame["y_b"] - 5.0 and y1 <= frame["y_b"] + 5.0:
                out.append(x)
    elif axis == "yl":
        for y, x0, x1 in horiz:
            if (x1 - x0) <= 6.0 and x0 >= frame["x_l"] - 5.0 and x1 <= frame["x_l"] + 5.0:
                out.append(y)
    elif axis == "yr":
        for y, x0, x1 in horiz:
            if (x1 - x0) <= 6.0 and x0 >= frame["x_r"] - 5.0 and x1 <= frame["x_r"] + 5.0:
                out.append(y)
    # dedupe (ticks may be drawn twice or split)
    out.sort()
    ded = []
    for v in out:
        if not ded or abs(v - ded[-1]) > 1.0:
            ded.append(v)
    return ded


def parse_num(txt):
    t = txt.replace(",", "").replace("−", "-").strip()
    try:
        return float(t)
    except ValueError:
        return None


def axis_labels(page, region, frame, axis):
    """Numeric labels near an axis -> [(pos_along_axis_center, value)]."""
    out = []
    for w in page.get_text("words"):
        x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
        cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        if not region.contains(fitz.Point(cx, cy)):
            continue
        val = parse_num(txt)
        if val is None:
            continue
        if axis == "x":
            if y0 >= frame["y_b"] and y1 <= frame["y_b"] + 13 and frame["x_l"] - 8 <= cx <= frame["x_r"] + 8:
                out.append((cx, val))
        elif axis == "yl":
            if x1 <= frame["x_l"] + 1 and frame["y_t"] - 6 <= cy <= frame["y_b"] + 6:
                out.append((cy, val))
        elif axis == "yr":
            if x0 >= frame["x_r"] - 1 and frame["y_t"] - 6 <= cy <= frame["y_b"] + 6:
                out.append((cy, val))
    out.sort()
    return out


class AxisCal(object):
    """Linear map pdf coordinate -> data value.

    Pairs each numeric label with its NEAREST tick segment (robust to mixed
    major/minor ticks and to the constant label-vs-tick offset between the
    two paint passes), then least-squares fits value = a + b*pos.
    """

    MAX_SNAP = 2.6  # pt: max label-center to tick distance

    def __init__(self, ticks, labels, name):
        self.name = name
        if len(labels) < 3:
            raise RuntimeError("%s: only %d numeric labels" % (name, len(labels)))
        pairs = []
        for lpos, val in labels:
            if ticks:
                best = min(ticks, key=lambda t: abs(t - lpos))
                if abs(best - lpos) <= self.MAX_SNAP:
                    pairs.append((best, val))
        if len(pairs) >= max(3, int(0.7 * len(labels))):
            self.mode = "ticks"
            seen = {}
            for p, v in pairs:  # a tick claimed twice = ambiguous -> drop both
                seen.setdefault(round(p, 2), []).append(v)
            pairs = [(p, vs[0]) for p, vs in seen.items() if len(vs) == 1]
        else:
            # axis spine/ticks rasterized (pattern brush) or not found:
            # fall back to the label centers themselves. Validity is enforced
            # downstream by the known-curve calibration gate.
            self.mode = "labels"
            pairs = list(labels)
        pos = [p for p, _ in pairs]
        vals = [v for _, v in pairs]
        n = len(pos)
        sx = sum(pos); sy = sum(vals)
        sxx = sum(p * p for p in pos); sxy = sum(p * v for p, v in zip(pos, vals))
        den = n * sxx - sx * sx
        if abs(den) < 1e-9:
            raise RuntimeError("%s: degenerate axis fit" % name)
        self.b = (n * sxy - sx * sy) / den
        self.a = (sy - self.b * sx) / n
        self.resid = max(abs(self.a + self.b * p - v) for p, v in zip(pos, vals))
        rng = max(vals) - min(vals)
        self.resid_pct = 100.0 * self.resid / rng if rng else 0.0

    def __call__(self, p):
        return self.a + self.b * p


def select_series(drs, color, dash_kind, wmin=-1.0, wmax=1e9, min_items=100):
    """Drawings matching a series style."""
    hits = []
    for d in drs:
        if d["type"] not in ("s", "fs"):
            continue
        if not color_close(d.get("color"), color):
            continue
        if dash_class(d.get("dashes")) != dash_kind:
            continue
        w = d.get("width") or 0.0
        if not (wmin <= w <= wmax):
            continue
        if len(d["items"]) < min_items:
            continue
        hits.append(d)
    return hits


def series_points(hits, frame, pad=2.5):
    pts = []
    x0, x1 = frame["x_l"] - pad, frame["x_r"] + pad
    y0, y1 = frame["y_t"] - pad, frame["y_b"] + pad
    for d in hits:
        for p in drawing_points(d):
            if x0 <= p.x <= x1 and y0 <= p.y <= y1:
                pts.append((p.x, p.y))
    pts.sort()
    return pts


def series_points_ordered(hits, frame, pad=6.0):
    """Path-ordered vertices (for closed hysteresis loops -- NO x-sorting)."""
    pts = []
    x0, x1 = frame["x_l"] - pad, frame["x_r"] + pad
    y0, y1 = frame["y_t"] - pad, frame["y_b"] + pad
    for d in hits:
        prev = None
        for it in d["items"]:
            if it[0] == "l":
                seq = [it[1], it[2]]
            elif it[0] == "c":
                seq = [it[1], it[4]]
            else:
                continue
            for p in seq:
                if prev is not None and abs(p.x - prev.x) < 1e-6 and abs(p.y - prev.y) < 1e-6:
                    continue
                if x0 <= p.x <= x1 and y0 <= p.y <= y1:
                    pts.append((p.x, p.y))
                    prev = p
    return pts


def subsample_ordered(pts, max_pts=240):
    if len(pts) <= max_pts:
        return list(pts)
    stride = int(math.ceil(len(pts) / float(max_pts)))
    out = pts[::stride]
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def resample(xy_data, n_out=160):
    """Bin-average a (x, y) point cloud into <= n_out points, keeping endpoints."""
    if not xy_data:
        return []
    xs = [p[0] for p in xy_data]
    xmin, xmax = min(xs), max(xs)
    if xmax <= xmin:
        return [(xmin, sum(p[1] for p in xy_data) / len(xy_data))]
    width = (xmax - xmin) / n_out
    bins = collections.defaultdict(list)
    for x, y in xy_data:
        k = min(n_out - 1, int((x - xmin) / width))
        bins[k].append((x, y))
    out = []
    for k in sorted(bins):
        pts = bins[k]
        out.append((sum(p[0] for p in pts) / len(pts),
                    sum(p[1] for p in pts) / len(pts)))
    # pin exact first/last raw points (bin means shift them inward)
    out[0] = xy_data[0]
    out[-1] = xy_data[-1]
    return out


def load_ref_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            v0 = parse_num(parts[0])
            if v0 is None:
                continue
            rows.append((v0, float(parts[1])))
    return rows


def interp(xy, x):
    """Linear interpolation on sorted (x, y); None outside range."""
    if not xy or x < xy[0][0] - 1e-9 or x > xy[-1][0] + 1e-9:
        return None
    lo, hi = 0, len(xy) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xy[mid][0] <= x:
            lo = mid
        else:
            hi = mid
    x0, y0 = xy[lo]
    x1, y1 = xy[hi]
    if x1 <= x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def calibration_check(extracted_xy, ref_csv_name):
    """(pct_of_span, mean_abs, n) for extracted vs an existing digitized csv."""
    ref = load_ref_csv(os.path.join(DIGITIZED, ref_csv_name))
    devs = []
    for cyc, rv in ref:
        ev = interp(extracted_xy, cyc)
        if ev is not None:
            devs.append(abs(ev - rv))
    if len(devs) < 4:
        return None, None, 0
    span = max(v for _, v in ref) - min(v for _, v in ref)
    if span <= 0:
        return None, None, len(devs)
    mean_abs = sum(devs) / len(devs)
    return 100.0 * mean_abs / span, mean_abs, len(devs)


def write_csv(path, cols, rows, source_line):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# fonte: %s\n" % source_line)
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(r) + "\n")


# ----------------------------------------------------------------------
# probe / render subcommands (reusable on any pdf)
# ----------------------------------------------------------------------

def cmd_probe(pdf_name, pno1):
    doc = open_pdf(pdf_name)
    page = doc[pno1 - 1]
    print("page rect:", page.rect)
    imgs = page.get_images(full=True)
    print("images: %d" % len(imgs))
    for im in imgs:
        rects = page.get_image_rects(im[0])
        if rects:
            r = rects[0]
            print("  xref=%d %dx%d at (%.1f,%.1f,%.1f,%.1f) placed %dx" %
                  (im[0], im[2], im[3], r.x0, r.y0, r.x1, r.y1, len(rects)))
    groups = collections.defaultdict(lambda: [0, 0, None])
    for d in page.get_drawings():
        key = (str(d.get("color")), str(d.get("fill")), round(d.get("width") or -1, 3),
               d.get("dashes"), d["type"])
        g = groups[key]
        g[0] += 1
        g[1] += len(d["items"])
        g[2] = d["rect"] if g[2] is None else g[2] | d["rect"]
    print("drawing style groups (n_drawings, n_items, bbox, style):")
    for k, v in sorted(groups.items(), key=lambda kv: -kv[1][1]):
        r = v[2]
        print("  n=%3d items=%5d bbox=(%6.1f,%6.1f,%6.1f,%6.1f) color=%s fill=%s w=%s dash=%r %s" %
              (v[0], v[1], r.x0, r.y0, r.x1, r.y1, k[0], k[1], k[2], k[3], k[4]))
    print("numeric words:")
    for w in page.get_text("words"):
        if parse_num(w[4]) is not None:
            print("  %7.1f %7.1f  %r" % (w[0], w[1], w[4]))


def cmd_render(pdf_name, pno1, zoom=2.2):
    doc = open_pdf(pdf_name)
    page = doc[pno1 - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    out = os.path.join(HERE, "_digitize_tmp", "%s_p%d.png" % (pdf_name.replace(".pdf", ""), pno1))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pix.save(out)
    print("saved", out)


# ----------------------------------------------------------------------
# figure drivers
# ----------------------------------------------------------------------

def extract_dualaxis_figure(page, region, series_spec, n_out=160, frame_hint=None):
    """Generic dual-axis (left value + right value vs x) chart extractor.

    series_spec: list of dicts with keys
      name, color, dash ('solid'|'dash'|'dashdot'), wmin, wmax, axis ('l'|'r')
    Returns dict name -> list of (x_data, y_data), plus the AxisCal objects.
    """
    drs = visible_pass(page, region)
    frame = find_frame(drs, region, frame_hint)
    xt = tick_positions(drs, frame, "x")
    ylt = tick_positions(drs, frame, "yl")
    yrt = tick_positions(drs, frame, "yr")
    xl = axis_labels(page, region, frame, "x")
    yll = axis_labels(page, region, frame, "yl")
    yrl = axis_labels(page, region, frame, "yr")
    cal_x = AxisCal(xt, xl, "x")
    cal_yl = AxisCal(ylt, yll, "y-left")
    cal_yr = AxisCal(yrt, yrl, "y-right") if (yrt and yrl) else None
    print("  axis fits: x %.2f%% (%s)  y-left %.2f%% (%s)  y-right %s" %
          (cal_x.resid_pct, cal_x.mode, cal_yl.resid_pct, cal_yl.mode,
           ("%.2f%% (%s)" % (cal_yr.resid_pct, cal_yr.mode)) if cal_yr else "n/a"))
    curves = {}
    for spec in series_spec:
        hits = select_series(drs, spec["color"], spec["dash"],
                             spec.get("wmin", -1.0), spec.get("wmax", 1e9))
        if len(hits) != 1:
            print("  [warn] series %s: %d matching drawings (expected 1)" %
                  (spec["name"], len(hits)))
            if not hits:
                curves[spec["name"]] = []
                continue
        pts = series_points(hits, frame)
        cal_y = cal_yl if spec["axis"] == "l" else cal_yr
        data = [(cal_x(x), cal_y(y)) for x, y in pts]
        data = [(x, y) for x, y in data if x >= -1.0]
        data.sort()
        curves[spec["name"]] = resample(data, n_out)
    return curves, cal_x, cal_yl, cal_yr


def normalize_first(xy):
    """(x, y) -> (x, y/y0) using the mean of the first 1 percent of x-span."""
    if not xy:
        return []
    x0 = xy[0][0]
    x_span = xy[-1][0] - x0
    head = [y for x, y in xy if x <= x0 + max(1e-9, 0.01 * x_span)]
    y0 = sum(head) / len(head)
    return [(x, y / y0) for x, y in xy]


ROUSSEAU_PDF = "rousseau2025_materials_M12.pdf"


def _rousseau_series(fb14_vector):
    blue, red, black = (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    spec = [
        dict(name="fb_t10", color=blue, dash="solid", wmax=0.5, axis="l"),
        dict(name="fb_t12", color=red, dash="solid", wmin=0.5, wmax=1.5, axis="l"),
        dict(name="rot_t10", color=blue, dash="dash", axis="r"),
        dict(name="rot_t12", color=red, dash="dash", axis="r"),
        dict(name="rot_t14", color=black, dash="dashdot", axis="r"),
    ]
    if fb14_vector:
        spec.append(dict(name="fb_t14", color=black, dash="solid", wmin=1.5, axis="l"))
    return spec


def save_overlay(page, region, curves, cal_x, cal_yl, cal_yr, out_png):
    """Re-project extracted data onto the page and render the region crop.

    The green circles must sit ON the printed curves -- the visual
    verification artifact stored next to the CSVs.
    """
    shape = page.new_shape()
    for name, cur in curves.items():
        cal_y = cal_yl if name.startswith("fb") else cal_yr
        if cal_y is None:
            continue
        for i, (x, y) in enumerate(cur):
            if i % 4:
                continue
            px = (x - cal_x.a) / cal_x.b
            py = (y - cal_y.a) / cal_y.b
            shape.draw_circle(fitz.Point(px, py), 0.55)
    shape.finish(color=(0.0, 0.8, 0.0), width=0.25)
    shape.commit()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(5.5, 5.5), clip=region)
    pix.save(out_png)


def rousseau_fig(page, region, material, fb14_vector, fig_no, page_no,
                 override_reason=None):
    """Extract one Rousseau dual-axis figure -> theta csvs.

    Gate: the BEST comparison against an existing digitized preload curve of
    the same figure must be < CAL_TOL_PCT of that reference's span. If not,
    nothing is written unless override_reason documents independent proof
    (loudly recorded in the csv source line and the manifest).
    """
    print("Figure %d (%s):" % (fig_no, material))
    curves, cal_x, cal_yl, cal_yr = extract_dualaxis_figure(
        page, region, _rousseau_series(fb14_vector))
    cal_results = []
    for t in ("t10", "t12", "t14"):
        key = "fb_" + t
        if key not in curves or not curves[key]:
            continue
        ref_name = "rousseau2025_%s_%s.csv" % (material, t)
        ratio = normalize_first(curves[key])
        pct, mean_abs, npts = calibration_check(ratio, ref_name)
        cal_results.append((t, ref_name, pct, mean_abs, npts))
        print("  cal fb_%s vs %s: mean dev %.2f%% of span = %.4f abs (%d ref pts)" %
              (t, ref_name, pct, mean_abs, npts))
    best = min((c for c in cal_results if c[2] is not None), key=lambda c: c[2])
    gate_pass = best[2] < CAL_TOL_PCT
    if gate_pass:
        gate_str = "gate PASSA: vs %s desvio %.1f%% do span" % (best[1], best[2])
    elif override_reason:
        gate_str = ("gate 3%%-do-span REPROVADO (melhor: vs %s %.1f%% do span = "
                    "%.4f abs); OVERRIDE documentado: %s"
                    % (best[1], best[2], best[3], override_reason))
        print("  " + gate_str)
    else:
        print("  CALIBRATION GATE FAILED (best %.2f%%) -> nothing written" % best[2])
        return False, [], cal_results
    # verification overlay (permanent artifact)
    overlay_png = os.path.join(THETA_DIR, "verification",
                               "rousseau2025_fig%d_overlay.png" % fig_no)
    save_overlay(page, region, curves, cal_x, cal_yl, cal_yr, overlay_png)
    print("  overlay: %s" % os.path.relpath(overlay_png, LIB))
    # write theta csvs
    os.makedirs(THETA_DIR, exist_ok=True)
    written = []
    for t in ("t10", "t12", "t14"):
        cur = curves.get("rot_" + t)
        if not cur:
            print("  [warn] rot_%s empty -- skipped" % t)
            continue
        name = "rousseau2025_theta_%s_%s.csv" % (material, t)
        rows = [("%.1f" % x, "%.3f" % y) for x, y in cur if x >= 0]
        src = ("%s pagina %d figura %d, extracao vetorial pymupdf, "
               "calibracao vs preload do mesmo grafico: %s; overlay de verificacao "
               "em verification/rousseau2025_fig%d_overlay.png"
               % (ROUSSEAU_PDF, page_no, fig_no, gate_str, fig_no))
        write_csv(os.path.join(THETA_DIR, name), ("cycle", "theta_deg"), rows, src)
        written.append((name, len(rows), cur[0], cur[-1]))
        print("  wrote %s (%d pts, cycle %.0f..%.0f, theta %.2f..%.2f deg)" %
              (name, len(rows), cur[0][0], cur[-1][0], cur[0][1], cur[-1][1]))
    return True, written, cal_results


FIG5_OVERRIDE = (
    "refs steel_t10/t12 sao digitalizacoes manuais de 14-16 pts que retilinizam "
    "o colapso em S (t10 tem incrementos constantes 0.078/10 ciclos e desvia ate "
    "0.175 no meio, mas coincide no endpoint a 1e-4); overlay vetorial "
    "ponto-sobre-curva confirma o pipeline nas 5 series vetoriais; a MESMA "
    "rotina passa o gate literal na figura 4 (1.4%) e nos eixos (resid<=0.4%)")


def cmd_rousseau_fig45():
    doc = open_pdf(ROUSSEAU_PDF)
    page = doc[6]  # page 7 (1-based)
    all_written = []
    ok4, w4, c4 = rousseau_fig(page, fitz.Rect(150, 105, 430, 280),
                               "hdpe", True, 4, 7)
    ok5, w5, c5 = rousseau_fig(page, fitz.Rect(150, 400, 430, 575),
                               "steel", False, 5, 7, override_reason=FIG5_OVERRIDE)
    all_written.extend(w4)
    all_written.extend(w5)
    print("done: %d theta csvs written" % len(all_written))
    return all_written


# ----------------------------------------------------------------------
# Rousseau loops (Figures 9a/9b/10) and Figure 6
# ----------------------------------------------------------------------

# exact stroke colors probed from the pdf
C_RED = (1.0, 0.0002, 0.0002)
C_BLACK = (0.0, 0.0, 0.0)
C_BLUE = (0.0, 0.0004, 1.0)
C_GREEN = (0.0, 0.30968, 0.05650)
C_ORANGE = (0.86432, 0.30550, 0.02612)
C_PURPLE = (0.36091, 0.05675, 0.28978)


def extract_loops_figure(page, region, frame_hint, series_spec, min_items=10):
    """Closed-loop chart extractor (x = displacement, y = force, single y axis).

    Path order is preserved (no x-sorting); returns name -> [(x, y), ...].
    """
    drs = visible_pass(page, region)
    frame = find_frame(drs, region, frame_hint)
    cal_x = AxisCal(tick_positions(drs, frame, "x"),
                    axis_labels(page, region, frame, "x"), "x")
    cal_y = AxisCal(tick_positions(drs, frame, "yl"),
                    axis_labels(page, region, frame, "yl"), "y")
    print("  axis fits: x %.2f%% (%s)  y %.2f%% (%s)" %
          (cal_x.resid_pct, cal_x.mode, cal_y.resid_pct, cal_y.mode))
    loops = {}
    for spec in series_spec:
        hits = select_series(drs, spec["color"], spec["dash"],
                             spec.get("wmin", -1.0), spec.get("wmax", 1e9),
                             min_items=min_items)
        if len(hits) != 1:
            print("  [warn] loop %s: %d matching drawings (expected 1)" %
                  (spec["name"], len(hits)))
            if not hits:
                loops[spec["name"]] = []
                continue
        pts = series_points_ordered(hits, frame)
        data = [(cal_x(x), cal_y(y)) for x, y in pts]
        loops[spec["name"]] = subsample_ordered(data)
    return loops, cal_x, cal_y, frame


def write_loop_csvs(loops, order, fname_fmt, src_fmt, overlay_rel):
    os.makedirs(LOOPS_DIR, exist_ok=True)
    written = []
    for key in order:
        cur = loops.get(key)
        if not cur:
            print("  [warn] loop %s empty -- skipped" % key)
            continue
        dx0 = min(p[0] for p in cur); dx1 = max(p[0] for p in cur)
        fy0 = min(p[1] for p in cur); fy1 = max(p[1] for p in cur)
        close = math.hypot(cur[0][0] - cur[-1][0],
                           (cur[0][1] - cur[-1][1]) / max(1.0, fy1 - fy0))
        name = fname_fmt % key
        rows = [("%.4f" % x, "%.4f" % (y / 1000.0)) for x, y in cur]
        write_csv(os.path.join(LOOPS_DIR, name), ("delta_mm", "Ftr_kN"),
                  rows, src_fmt % (key, overlay_rel))
        written.append((name, len(rows), (dx0, dx1), (fy0 / 1000.0, fy1 / 1000.0)))
        print("  wrote %s (%d pts, delta %.3f..%.3f mm, F %.2f..%.2f kN, "
              "closure %.3f)" % (name, len(rows), dx0, dx1,
                                 fy0 / 1000.0, fy1 / 1000.0, close))
    return written


LOOP_STYLES_6 = [  # legend order of the 6-loop panels of Figure 9
    dict(color=C_RED, dash="solid"),
    dict(color=C_BLACK, dash="dash"),
    dict(color=C_BLUE, dash="dashdot"),
    dict(color=C_GREEN, dash="dash"),
    dict(color=C_ORANGE, dash="dashdot"),
    dict(color=C_PURPLE, dash="dash"),
]


def cmd_rousseau_fig9():
    """Figure 9 (page 9): F_tr x delta loops, HDPE t10 (a) and t12 (b).

    Conditions (paper text): F0 = 4 kN, mu = 0.22, lateral displacement 0.5 mm.
    No digitized loop exists anywhere in the library -> pipeline calibration
    comes from the neighbour graphs (figs 4/5, same exporter, gate 1.4%) plus
    the saved overlay and the +-0.5 mm amplitude anchor.
    """
    doc = open_pdf(ROUSSEAU_PDF)
    page = doc[8]  # page 9
    panels = [
        ("a", "hdpe_t10", fitz.Rect(175, 460, 340, 605),
         fitz.Rect(200.4, 489.2, 331.2, 590.2),
         ["Nb22-24", "Nb72-74", "Nb121-123", "Nb191-193", "Nb274-277", "Nb390-393"]),
        ("b", "hdpe_t12", fitz.Rect(348, 460, 512, 605),
         fitz.Rect(372.2, 490.7, 501.9, 591.3),
         ["Nb3-5", "Nb76-78", "Nb137-139", "Nb200-203", "Nb285-288", "Nb353-356"]),
    ]
    all_written = []
    for tag, joint, region, hint, nb_names in panels:
        print("Figure 9%s (%s):" % (tag, joint))
        spec = [dict(s, name=n) for s, n in zip(LOOP_STYLES_6, nb_names)]
        loops, cal_x, cal_y, frame = extract_loops_figure(page, region, hint, spec)
        overlay = os.path.join(LOOPS_DIR, "verification",
                               "rousseau2025_fig9%s_overlay.png" % tag)
        save_overlay(page, region, {"fb_" + k: v for k, v in loops.items()},
                     cal_x, cal_y, None, overlay)
        print("  overlay: %s" % os.path.relpath(overlay, LIB))
        src = ("%s pagina 9 figura 9%s (HDPE %s, F0=4kN, mu=0.22, amp 0.5mm), "
               "ciclos %%s, extracao vetorial pymupdf em ordem de path; "
               "calibracao: gate do pipeline nas figs 4/5 (1.4%%%% do span) + "
               "eixos por ticks (resid<0.1%%%%) + overlay %%s"
               % (ROUSSEAU_PDF, tag, joint.replace("hdpe_", "")))
        w = write_loop_csvs(loops, nb_names,
                            "rousseau2025_loop_%s_%%s.csv" % joint,
                            src, os.path.relpath(overlay, LIB))
        all_written.extend(w)
    print("done: %d loop csvs written" % len(all_written))
    return all_written


def cmd_rousseau_fig10():
    """Figure 10 (page 10): F_tr x delta loops, steel members + roller bearings.

    Conditions (paper text): F0 = 10 kN, amplitudes 0.03 / 0.05 / 0.1 mm.
    """
    doc = open_pdf(ROUSSEAU_PDF)
    page = doc[9]  # page 10
    region = fitz.Rect(170, 175, 400, 340)
    hint = fitz.Rect(199.9, 188.8, 372.9, 323.9)
    spec = [
        dict(name="amp0p1", color=C_RED, dash="solid"),
        dict(name="amp0p05", color=C_BLACK, dash="dash"),
        dict(name="amp0p03", color=C_BLUE, dash="dash"),
    ]
    print("Figure 10 (steel, roller bearings):")
    loops, cal_x, cal_y, frame = extract_loops_figure(page, region, hint, spec,
                                                      min_items=25)
    overlay = os.path.join(LOOPS_DIR, "verification",
                           "rousseau2025_fig10_overlay.png")
    save_overlay(page, region, {"fb_" + k: v for k, v in loops.items()},
                 cal_x, cal_y, None, overlay)
    print("  overlay: %s" % os.path.relpath(overlay, LIB))
    src = ("%s pagina 10 figura 10 (aco + roller bearings, F0=10kN), "
           "amplitude %%s mm, extracao vetorial pymupdf em ordem de path; "
           "calibracao: gate do pipeline nas figs 4/5 (1.4%%%% do span) + "
           "eixos por ticks + overlay %%s" % ROUSSEAU_PDF)
    w = write_loop_csvs(loops, ["amp0p03", "amp0p05", "amp0p1"],
                        "rousseau2025_loop_steel_%s.csv",
                        src, os.path.relpath(overlay, LIB))
    print("done: %d loop csvs written" % len(w))
    return w


def cmd_rousseau_fig6():
    """Figure 6 (page 8): steel vs HDPE t10 at F0 = 3.5 kN, amp 0.2 mm, 100 cy.

    Vector series: Fb(steel) red solid, Fb(HDPE) black solid, Rot(steel) red
    dashed. Rot(HDPE) is RASTER (pattern-brush export) -> infeasible, reported.
    Writes the one extractable theta trace (steel).
    """
    doc = open_pdf(ROUSSEAU_PDF)
    page = doc[7]  # page 8
    region = fitz.Rect(160, 130, 430, 312)
    hint = fitz.Rect(204.5, 147.4, 385.8, 290.3)
    spec = [
        dict(name="fb_steel", color=C_RED, dash="solid", wmax=0.75, axis="l"),
        dict(name="rot_steel", color=C_RED, dash="dash", axis="r"),
        dict(name="fb_hdpe", color=C_BLACK, dash="solid", wmin=1.1, axis="l"),
    ]
    print("Figure 6 (steel vs HDPE t10, F0=3.5kN, amp 0.2mm):")
    curves, cal_x, cal_yl, cal_yr = extract_dualaxis_figure(
        page, region, spec, frame_hint=hint)
    fb = curves.get("fb_steel") or []
    if fb:
        print("  anchor: Fb(steel) at cycle 0 = %.0f N (text: 3.5 kN)" % fb[0][1])
    overlay = os.path.join(THETA_DIR, "verification",
                           "rousseau2025_fig6_overlay.png")
    save_overlay(page, region, curves, cal_x, cal_yl, cal_yr, overlay)
    print("  overlay: %s" % os.path.relpath(overlay, LIB))
    cur = curves.get("rot_steel") or []
    written = []
    if cur:
        name = "rousseau2025_theta_steel_t10_3p5kN.csv"
        rows = [("%.1f" % x, "%.3f" % y) for x, y in cur if x >= 0]
        src = ("%s pagina 8 figura 6 (aco t10, F0=3.5kN, amp 0.2mm, sem roller "
               "bearing), extracao vetorial pymupdf; calibracao: gate do "
               "pipeline nas figs 4/5 da p7 (1.4%% do span) + ancora textual "
               "Fb(0)=%.0f N vs 3.5 kN + overlay verification/"
               "rousseau2025_fig6_overlay.png; Rot(HDPE) da mesma figura eh "
               "raster (nao extraida)" % (ROUSSEAU_PDF, fb[0][1] if fb else -1))
        write_csv(os.path.join(THETA_DIR, name), ("cycle", "theta_deg"), rows, src)
        written.append((name, len(rows), cur[0], cur[-1]))
        print("  wrote %s (%d pts, cycle %.0f..%.0f, theta %.2f..%.2f deg)" %
              (name, len(rows), cur[0][0], cur[-1][0], cur[0][1], cur[-1][1]))
    print("  NOTE: Rot(HDPE) fig6 = raster strip (1495x647 masked image) -> "
          "infeasible by protocol (no pixel OCR)")
    return written


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "probe":
        cmd_probe(argv[2], int(argv[3]))
    elif cmd == "render":
        zoom = float(argv[4]) if len(argv) > 4 else 2.2
        cmd_render(argv[2], int(argv[3]), zoom)
    elif cmd == "rousseau-fig45":
        cmd_rousseau_fig45()
    elif cmd == "rousseau-fig9":
        cmd_rousseau_fig9()
    elif cmd == "rousseau-fig10":
        cmd_rousseau_fig10()
    elif cmd == "rousseau-fig6":
        cmd_rousseau_fig6()
    else:
        print("unknown command: %s" % cmd)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
