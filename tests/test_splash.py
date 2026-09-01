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


# ---------------------------------------------------------------------------
# project_hex_faces (Task 2)
# ---------------------------------------------------------------------------
import math

from bolt_analysis_studio.gui.splash import project_hex_faces


def test_hex_faces_at_zero_rotation_front_face_is_centred():
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    assert len(faces) == 6
    f0 = next(f for f in faces if f['face_angle_deg'] == 0)
    assert abs(f0['cx']) < 1e-6
    assert abs(f0['w'] - 30.0) < 1e-6
    assert f0['visible'] is True


def test_hex_faces_at_zero_rotation_back_face_invisible():
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    f180 = next(f for f in faces if f['face_angle_deg'] == 180)
    assert f180['visible'] is False


def test_hex_faces_rotation_shifts_front():
    faces = project_hex_faces(theta_deg=60.0, R=26.0, W=30.0)
    f300 = next(f for f in faces if f['face_angle_deg'] == 300)
    assert abs(f300['cx']) < 1e-6
    assert abs(f300['w'] - 30.0) < 1e-6
    assert f300['visible'] is True


def test_hex_faces_edge_on_face_has_zero_width():
    faces = project_hex_faces(theta_deg=30.0, R=26.0, W=30.0)
    f60 = next(f for f in faces if f['face_angle_deg'] == 60)
    assert f60['visible'] is False


def test_hex_faces_sorted_back_to_front():
    faces = project_hex_faces(theta_deg=0.0, R=26.0, W=30.0)
    z_values = [f['z'] for f in faces]
    assert z_values == sorted(z_values)


# ---------------------------------------------------------------------------
# sample_path (Task 3)
# ---------------------------------------------------------------------------
from PyQt6.QtGui import QPainterPath
from bolt_analysis_studio.gui.splash import sample_path


def test_sample_path_straight_line_uniform(qapp):
    p = QPainterPath()
    p.moveTo(0, 0)
    p.lineTo(100, 0)
    samples = sample_path(p, n=11)
    assert len(samples) == 11
    assert abs(samples[0].x() - 0) < 0.5
    assert abs(samples[-1].x() - 100) < 0.5
    assert abs(samples[5].x() - 50) < 1.0


def test_sample_path_returns_qpointf(qapp):
    p = QPainterPath()
    p.moveTo(0, 0)
    p.lineTo(10, 10)
    samples = sample_path(p, n=3)
    for pt in samples:
        assert hasattr(pt, 'x') and hasattr(pt, 'y')
