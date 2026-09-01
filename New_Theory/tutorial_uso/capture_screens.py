# -*- coding: utf-8 -*-
"""Captura screenshots REAIS das telas do BAS V2 para o tutorial HTML.

Roda com a plataforma Qt NATIVA do Windows (NÃO offscreen) para renderizar as
fontes de verdade (Bahnschrift). WA_DontShowOnScreen lê o layout sem exibir a
janela no desktop (sem flashes). Saída: New_Theory/tutorial_uso/img/*.png

    python New_Theory/tutorial_uso/capture_screens.py   # via PowerShell (nativo)
"""
import os
import sys
import time

sys.path.insert(0, 'src')
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

app = QApplication([])
for _n in ("question", "warning", "information", "critical"):
    setattr(QMessageBox, _n, staticmethod(lambda *a, **k: QMessageBox.StandardButton.Ok))

from bolt_analysis_studio.gui.theme import Theme
app.setStyleSheet(Theme.get_stylesheet())

OUT = os.path.join("New_Theory", "tutorial_uso", "img")
os.makedirs(OUT, exist_ok=True)


def pump(n=8):
    for _ in range(n):
        app.processEvents()


def save(w, name):
    try:
        pm = w.grab()
        pm.save(os.path.join(OUT, name), "PNG")
        print("OK  ", name, pm.width(), "x", pm.height())
    except Exception as e:  # noqa
        print("FAIL", name, repr(e))


def offscreen(w):
    w.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    w.show()
    pump(6)


from bolt_analysis_studio.gui.new_analysis_wizard import (
    build_model, AnalysisSpec, NewAnalysisWizard)

# ── 01 Splash ────────────────────────────────────────────────────────────────
try:
    from bolt_analysis_studio.gui.splash import AnimatedSplashScreen
    sp = AnimatedSplashScreen()
    offscreen(sp)
    sp._start_time = time.monotonic() - 1.7      # frame com a curva já desenhada
    pump(3)
    save(sp, "01_splash.png")
    sp.close()
except Exception as e:  # noqa
    print("FAIL splash", repr(e))

# ── 02-04 Wizard ─────────────────────────────────────────────────────────────
try:
    wz = NewAnalysisWizard()
    wz.resize(760, 580)
    offscreen(wz)
    save(wz, "02_wizard_joint.png")
    for nm in ("03_wizard_bolt.png", "04_wizard_loading.png"):
        try:
            wz.next()
            pump(5)
            save(wz, nm)
        except Exception as e:  # noqa
            print("wizard nav", nm, repr(e))
    wz.close()
except Exception as e:  # noqa
    print("FAIL wizard", repr(e))

# ── 05 Shell (Model) + closeups ──────────────────────────────────────────────
from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
win = ChromeWindow()
win.resize(1600, 950)
win._after_wizard(build_model(AnalysisSpec()))
win.switch_module("Model")
pump(12)
save(win, "05_shell_model.png")
save(win.module_bar, "06_stepper.png")
save(win._tree_dock, "07_tree.png")
save(win._inspector_dock, "08_properties.png")
save(win._msg_dock, "09_messages.png")

# ── 10-13 Módulos ────────────────────────────────────────────────────────────
win.switch_module("Contacts"); pump(8); save(win, "10_contacts.png")
win.switch_module("Loads"); pump(8); save(win, "11_loads.png")
win.switch_module("Analysis"); pump(16); save(win, "12_analysis.png")
win.switch_module("Results"); pump(12); save(win, "13_results.png")

# ── 15 Tema claro (mostra a troca de tema) ───────────────────────────────────
win.switch_module("Model"); pump(4)
try:
    win._apply_theme("light"); pump(10); save(win, "15_shell_light.png")
    win._apply_theme("engineering"); pump(4)
except Exception as e:  # noqa
    print("FAIL light", repr(e))

# ── 14 Validation browser com um caso plotado (curva REAL do store) ──────────
try:
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    from bolt_analysis_studio.validation.case_registry import all_records
    vb = ValidationBrowser()
    vb.resize(1400, 820)
    offscreen(vb)
    recs = [r for r in all_records() if getattr(r, "family", "") != "other"]
    cid = None
    for r in recs:
        if vb.store.get(r.case_id) is not None:
            cid = r.case_id
            break
    if cid is None and recs:
        cid = recs[0].case_id
    if cid:
        vb.show_case(cid)
        pump(10)
    save(vb, "14_validation.png")
    print("validation case:", cid)
    vb.close()
except Exception as e:  # noqa
    print("FAIL validation", repr(e))

print("DONE")
