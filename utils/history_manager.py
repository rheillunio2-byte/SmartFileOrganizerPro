"""Persistent organisation history (JSON), with one-time import of the old history.txt."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any

import config
from .file_types import CATEGORIES, empty_stats

Entry = dict[str, Any]


def _parse_legacy(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for block in text.split("=" * 50):
        block = block.strip()
        if not block:
            continue
        entry: Entry = {"id": uuid.uuid4().hex, "timestamp": "", "folder": "", "stats": empty_stats(),
                        "moves": [], "undone": False, "legacy": True}
        for line in block.splitlines():
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if key == "Date":
                entry["timestamp"] = line.partition(":")[2].strip()
            elif key == "Folder":
                entry["folder"] = value
            elif key in entry["stats"]:
                try:
                    entry["stats"][key] = int(value)
                except ValueError:
                    pass
        if entry["timestamp"]:
            entries.append(entry)
    return entries


def _write(entries: list[Entry]) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = config.HISTORY_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(entries[-config.MAX_HISTORY_ENTRIES:], fh, indent=1)
    os.replace(tmp, config.HISTORY_FILE)


def load_history() -> list[Entry]:
    """All entries, oldest first."""
    try:
        with open(config.HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        pass
    except (OSError, ValueError):
        return []
    for legacy in config.LEGACY_HISTORY_FILES:  # first run after upgrading
        try:
            entries = _parse_legacy(legacy.read_text(encoding="utf-8"))
        except OSError:
            continue
        if entries:
            _write(entries)
            return entries
    return []


def save_history(folder: str, stats: dict[str, int], moves: list[tuple[str, str]] | None = None) -> Entry:
    entry: Entry = {
        "id": uuid.uuid4().hex,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folder": str(folder),
        "stats": {k: int(stats.get(k, 0)) for k in [*CATEGORIES, "Total"]},
        "moves": [list(m) for m in (moves or [])],
        "undone": False,
    }
    entries = load_history()
    entries.append(entry)
    _write(entries)
    return entry


def mark_undone(entry_id: str) -> None:
    entries = load_history()
    for entry in entries:
        if entry.get("id") == entry_id:
            entry["undone"] = True
    _write(entries)


def clear_history() -> None:
    _write([])


def last_undoable() -> Entry | None:
    for entry in reversed(load_history()):
        if entry.get("moves") and not entry.get("undone"):
            return entry
    return None


def search(keyword: str) -> list[Entry]:
    """Newest first; matches folder, date or any category name."""
    keyword = keyword.strip().lower()
    entries = list(reversed(load_history()))
    if not keyword:
        return entries
    return [e for e in entries if keyword in e.get("folder", "").lower()
            or keyword in e.get("timestamp", "").lower()
            or any(keyword in c.lower() and e.get("stats", {}).get(c, 0) for c in CATEGORIES)]
