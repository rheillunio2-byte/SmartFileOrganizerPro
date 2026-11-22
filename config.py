"""Central configuration for Smart File Organizer Pro."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Smart File Organizer Pro"
APP_SLUG = "SmartFileOrganizerPro"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Rheil Evans T. Lunio"
APP_REPO = "https://github.com/rheillunio2-byte/SmartFileOrganizerPro"

# Directory that holds the source (or the unpacked PyInstaller bundle).
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS_DIR = BASE_DIR / "assets"


def _data_dir() -> Path:
    """Per-user data folder, so history/settings survive wherever the app is launched from."""
    if sys.platform.startswith("win"):
        root = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / APP_SLUG


DATA_DIR = Path(os.environ.get("SFOP_DATA_DIR") or _data_dir())
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
LEGACY_HISTORY_FILES = (Path("history") / "history.txt", BASE_DIR / "history" / "history.txt")

MAX_HISTORY_ENTRIES = 200
