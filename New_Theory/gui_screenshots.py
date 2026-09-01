# -*- coding: utf-8 -*-
"""Headless screenshots of the V2 application, one PNG per module (2026-08-29).

Used by build_paper_docx.fig_gui_usage() through a subprocess (a second
QApplication cannot live in the builder's process). Renders with the offscreen
QPA platform; on Windows that platform finds no fonts unless QT_QPA_FONTDIR
points at the system font folder, which is set here before Qt is imported.
A corpus case is loaded so the screens show real content.

    py -3.12 New_Theory/gui_screenshots.py --out <dir> [--case lu2024_M8_fig18_amp0p5]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

MODULES = ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gui_screenshots")
    ap.add_argument("--out", required=True)
    ap.add_argument("--case", default="lu2024_M8_fig18_amp0p5")
    ap.add_argument("--width", type=int, default=1500)
    ap.add_argument("--height", type=int, default=900)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from bolt_analysis_studio.core.app_state import get_app_state
    st = get_app_state()
    try:
        from bolt_analysis_studio.validation.case_registry import record
        from bolt_analysis_studio.validation.gui_bridge import build_case_model
        st.model = build_case_model(record(args.case))
        print(f"[gui] case {args.case} loaded as the model")
    except Exception as exc:                       # fall back to the wizard's model
        print(f"[gui] case model failed ({exc}); using the wizard default")
        from bolt_analysis_studio.gui.new_analysis_wizard import build_model, AnalysisSpec
        st.model = build_model(AnalysisSpec())

    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow(st)
    win.resize(args.width, args.height)
    win.show()
    for _ in range(30):
        app.processEvents()
    for mod in MODULES:
        win.switch_module(mod)
        for _ in range(60):
            app.processEvents()
        if mod == "Results":                 # show the validation browser (the corpus)
            tabs = getattr(win, "_results_tabs", None)
            if tabs is not None:
                for i in range(tabs.count()):
                    if tabs.tabText(i) == "Validation":
                        tabs.setCurrentIndex(i)
                for _ in range(120):
                    app.processEvents()
        pm = win.grab()
        f = out / f"chrome_{mod.lower()}.png"
        pm.save(str(f), "PNG")
        print(f"[gui] {mod:9s} -> {f.name} {pm.size().width()}x{pm.size().height()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
