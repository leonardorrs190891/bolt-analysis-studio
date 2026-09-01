"""Smoke da fundação do chrome V2: a fixture qapp offscreen boota."""


def test_qapp_boots(qapp):
    from PyQt6.QtWidgets import QWidget
    w = QWidget()
    w.setObjectName("smoke")
    assert w.objectName() == "smoke"
