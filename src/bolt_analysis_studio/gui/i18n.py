"""Bilingual (PT/EN) toggle for the GUI — the software counterpart of the
variable-explorer's ``data-l`` switch.

`Lang` holds the current language and fires callbacks on change; ``tr(pt, en)``
returns the string for the current language. A widget builds a :class:`TrGroup`
(a list of ``(setter, pt, en)`` triples) so that a language switch re-applies the
texts live, without rebuilding widgets.

Usage::

    from ..i18n import Lang, tr, TrGroup

    self._tg = TrGroup()
    self._tg.add(menu.setTitle, "Arquivo", "File")
    self._tg.add(btn.setText,   "Rodar",   "Run")
    # ... on Lang.toggle() every registered setter re-fires with the new lang.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Tuple

_PREFS_DIR = Path.home() / ".bolt_analysis_studio"
_PREFS_FILE = _PREFS_DIR / "preferences.json"


class Lang:
    """Global language state (``'pt'`` or ``'en'``) + change callbacks."""

    current: str = "pt"
    _callbacks: List[Callable] = []

    @classmethod
    def tr(cls, pt: str, en: str) -> str:
        return en if cls.current == "en" else pt

    @classmethod
    def is_en(cls) -> bool:
        return cls.current == "en"

    @classmethod
    def set_lang(cls, lang: str) -> None:
        lang = "en" if lang == "en" else "pt"
        if lang == cls.current:
            return
        cls.current = lang
        cls.save_preference()
        for cb in list(cls._callbacks):
            try:
                cb()
            except Exception:  # pragma: no cover - defensivo
                pass

    @classmethod
    def toggle(cls) -> None:
        cls.set_lang("en" if cls.current == "pt" else "pt")

    @classmethod
    def register_callback(cls, fn: Callable) -> None:
        if fn not in cls._callbacks:
            cls._callbacks.append(fn)

    @classmethod
    def unregister_callback(cls, fn: Callable) -> None:
        if fn in cls._callbacks:
            cls._callbacks.remove(fn)

    # ---- persistence (mesmo preferences.json do Theme) ----
    @classmethod
    def save_preference(cls) -> None:
        try:
            _PREFS_DIR.mkdir(parents=True, exist_ok=True)
            prefs = {}
            if _PREFS_FILE.exists():
                with open(_PREFS_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
            prefs["lang"] = cls.current
            with open(_PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2)
        except Exception:  # pragma: no cover - defensivo
            pass

    @classmethod
    def load_preference(cls) -> str:
        try:
            if _PREFS_FILE.exists():
                with open(_PREFS_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                lang = prefs.get("lang")
                if lang in ("pt", "en"):
                    cls.current = lang
        except Exception:  # pragma: no cover - defensivo
            pass
        return cls.current


def tr(pt: str, en: str) -> str:
    """Return the string for the current language."""
    return Lang.tr(pt, en)


class TrGroup:
    """Coleta ``(setter, pt, en)`` e re-aplica no toggle de idioma.

    Registra-se em :class:`Lang`; se os widgets já foram destruídos (``RuntimeError``
    do wrapper C++), auto-remove o callback para não vazar entre janelas/testes.
    """

    def __init__(self) -> None:
        self._items: List[Tuple[Callable, str, str]] = []
        Lang.register_callback(self.retranslate)

    def add(self, setter: Callable, pt: str, en: str) -> str:
        """Registra um setter e já o aplica no idioma atual; devolve a string."""
        self._items.append((setter, pt, en))
        s = Lang.tr(pt, en)
        try:
            setter(s)
        except RuntimeError:  # pragma: no cover
            pass
        return s

    def retranslate(self) -> None:
        try:
            for setter, pt, en in self._items:
                setter(Lang.tr(pt, en))
        except RuntimeError:            # widgets destruídos → solta o callback
            Lang.unregister_callback(self.retranslate)

    def dispose(self) -> None:
        Lang.unregister_callback(self.retranslate)
        self._items.clear()
