"""Statistics derived from the history."""

from __future__ import annotations

from .file_types import CATEGORIES, empty_stats
from .history_manager import load_history


def get_latest_statistics() -> dict[str, int]:
    """Stats of the most recent (not undone) run."""
    for entry in reversed(load_history()):
        if not entry.get("undone"):
            stats = empty_stats()
            stats.update({k: int(v) for k, v in entry.get("stats", {}).items() if k in stats})
            return stats
    return empty_stats()


def get_lifetime_statistics() -> dict[str, object]:
    totals = empty_stats()
    runs = 0
    last = ""
    for entry in load_history():
        if entry.get("undone"):
            continue
        runs += 1
        last = entry.get("timestamp", last)
        for key in [*CATEGORIES, "Total"]:
            totals[key] += int(entry.get("stats", {}).get(key, 0))
    return {"totals": totals, "runs": runs, "last_run": last}
