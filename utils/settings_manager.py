"""Tiny JSON-backed user settings."""

from __future__ import annotations

import json
import os
from typing import Any

import config

DEFAULTS: dict[str, Any] = {
    "appearance": "Dark",          # Dark | Light | System
    "accent": "Indigo",            # see ui.theme.ACCENTS
    "auto_open_folder": True,
    "auto_refresh_history": True,
    "confirm_before_organize": True,
    "animations": True,
    "cursor_effects": True,
}

_cache: dict[str, Any] | None = None


def load() -> dict[str, Any]:
    global _cache
    data = dict(DEFAULTS)
    try:
        with open(config.SETTINGS_FILE, "r", encoding="utf-8") as fh:
            stored = json.load(fh)
        if isinstance(stored, dict):
            data.update({k: v for k, v in stored.items() if k in DEFAULTS})
    except (OSError, ValueError):
        pass
    _cache = data
    return data


def get(key: str) -> Any:
    return (_cache if _cache is not None else load())[key]


def set_value(key: str, value: Any) -> None:
    data = _cache if _cache is not None else load()
    data[key] = value
    save()


def save() -> None:
    data = _cache if _cache is not None else load()
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = config.SETTINGS_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, config.SETTINGS_FILE)
    except OSError:
        pass


def reset() -> dict[str, Any]:
    global _cache
    _cache = dict(DEFAULTS)
    save()
    return _cache
