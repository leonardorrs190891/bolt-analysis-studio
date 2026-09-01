"""Fase 5: chrome vira default; --v1 é o fallback."""
from pathlib import Path


def test_default_is_chrome_and_v1_flag_present():
    src = (Path(__file__).resolve().parent.parent / "run_app.py").read_text(encoding="utf-8")
    assert "--v1" in src
    # o default constrói ChromeWindow quando não há --v1
    assert "args.v1" in src
    assert "ChromeWindow()" in src
