"""Loader de ícones SVG monocromáticos com recolor por tema.

Cada .svg em resources/icons/ usa o token literal ``__FG__`` como cor de
traço/preenchimento; o loader substitui pelo hex do tema (ou por uma cor
explícita) e renderiza um QPixmap. Cacheado por (name, color, size).

Na troca de tema, chame ``clear_icon_cache()`` e re-solicite os ícones para
que sejam reconstruídos na nova cor (QIcon já aplicado a widgets não muda
sozinho — os widgets do chrome fazem isso via callback de tema).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from .theme import Theme

_ICON_DIR = Path(__file__).resolve().parent.parent / "resources" / "icons"


def _render(raw: bytes, size: int, color: str) -> QPixmap:
    data = raw.replace(b"__FG__", color.encode("ascii"))
    renderer = QSvgRenderer(QByteArray(data))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p)
    p.end()
    return pm


@lru_cache(maxsize=512)
def _cached(name: str, color: str, size: int) -> QIcon:
    path = _ICON_DIR / f"{name}.svg"
    if not path.exists():
        return QIcon()
    icon_obj = QIcon()
    icon_obj.addPixmap(_render(path.read_bytes(), size, color))
    return icon_obj


def icon(name: str, color: str | None = None, size: int = 20) -> QIcon:
    """Ícone recolorido para ``color`` (padrão: ``Theme.TEXT``)."""
    return _cached(name, color or Theme.TEXT, size)


def clear_icon_cache() -> None:
    """Limpa o cache — chamar em troca de tema antes de re-solicitar ícones."""
    _cached.cache_clear()
