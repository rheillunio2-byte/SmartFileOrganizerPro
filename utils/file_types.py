"""File categories, their extensions and display colours."""

from __future__ import annotations

from pathlib import Path

OTHERS = "Others"

FILE_TYPES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".tif", ".ico", ".heic"],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".csv",
        ".ppt", ".pptx", ".xls", ".xlsx",
    ],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm", ".m4v", ".flv"],
    "Music": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
}

# Order used everywhere in the UI.
CATEGORIES: list[str] = [*FILE_TYPES.keys(), OTHERS]

# Accent colour per category (works on both light and dark surfaces).
CATEGORY_COLORS: dict[str, str] = {
    "Images": "#38bdf8",
    "Documents": "#a78bfa",
    "Videos": "#fb7185",
    "Music": "#34d399",
    "Archives": "#fbbf24",
    OTHERS: "#94a3b8",
}

_EXTENSION_LOOKUP = {ext: cat for cat, exts in FILE_TYPES.items() for ext in exts}

# Files that should never be moved.
IGNORED_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}


def classify(path: str | Path) -> str:
    """Return the category for a file based on its extension."""
    return _EXTENSION_LOOKUP.get(Path(path).suffix.lower(), OTHERS)


def empty_stats() -> dict[str, int]:
    stats = {category: 0 for category in CATEGORIES}
    stats["Total"] = 0
    return stats
