"""Small OS helpers."""

from __future__ import annotations

import os
import subprocess
import sys


def open_path(path: str) -> bool:
    """Open a folder/file in the system file manager. Returns True on success."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False
