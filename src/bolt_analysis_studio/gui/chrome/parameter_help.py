"""Catalogo de tooltips do Inspector (spec §3.E). Fonte unica: parameter_help.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_JSON = Path(__file__).with_name("parameter_help.json")


@lru_cache(maxsize=1)
def load_parameter_help() -> dict:
    try:
        return json.loads(_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def help_for(widget_name: str) -> str:
    return load_parameter_help().get(widget_name, "")
