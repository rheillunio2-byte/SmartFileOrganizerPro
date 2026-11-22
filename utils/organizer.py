"""Core logic: scan a folder, plan the moves, perform them, and undo them."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from .file_types import CATEGORIES, IGNORED_NAMES, classify, empty_stats

ProgressCallback = Callable[[int, int, str], None]


@dataclass
class OrganizeResult:
    stats: dict[str, int] = field(default_factory=empty_stats)
    moves: list[tuple[str, str]] = field(default_factory=list)  # (source, destination)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


def _is_candidate(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    name = path.name.lower()
    return not (name.startswith(".") or name in IGNORED_NAMES)


def scan(folder_path: str | Path) -> dict[str, int]:
    """Count the top-level files per category without touching anything."""
    folder = Path(folder_path)
    stats = empty_stats()
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    for item in folder.iterdir():
        if _is_candidate(item):
            stats[classify(item)] += 1
            stats["Total"] += 1
    return stats


def unique_destination(destination: Path, reserved: Iterable[Path] = ()) -> Path:
    """Return a free path, appending ' (1)', ' (2)'... when the name is taken."""
    reserved = set(reserved)
    if not destination.exists() and destination not in reserved:
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists() and candidate not in reserved:
            return candidate
        counter += 1


def organize(
    folder_path: str | Path,
    enabled: Iterable[str] | None = None,
    dry_run: bool = False,
    progress: ProgressCallback | None = None,
) -> OrganizeResult:
    """Sort the top-level files of ``folder_path`` into category sub-folders.

    * ``enabled`` limits which categories are touched (default: all).
    * ``dry_run`` only reports what would happen.
    * Existing files are never overwritten; clashes get a numeric suffix.
    * One unreadable file never stops the run; it is reported in ``errors``.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    allowed = set(CATEGORIES if enabled is None else enabled)
    result = OrganizeResult(dry_run=dry_run)

    files = sorted((p for p in folder.iterdir() if _is_candidate(p)), key=lambda p: p.name.lower())
    files = [p for p in files if classify(p) in allowed]
    total = len(files)
    reserved: set[Path] = set()

    for index, file in enumerate(files, start=1):
        category = classify(file)
        target = unique_destination(folder / category / file.name, reserved)
        try:
            if not dry_run:
                target.parent.mkdir(exist_ok=True)
                shutil.move(str(file), str(target))
            reserved.add(target)
            result.moves.append((str(file), str(target)))
            result.stats[category] += 1
            result.stats["Total"] += 1
        except OSError as exc:
            result.errors.append(f"{file.name}: {exc}")
        if progress:
            progress(index, total, file.name)

    return result


def undo(moves: Iterable[tuple[str, str]]) -> tuple[int, int]:
    """Move files back to where they came from. Returns ``(restored, skipped)``."""
    restored = skipped = 0
    touched_dirs: set[Path] = set()
    for source, destination in reversed(list(moves)):
        src, dst = Path(source), Path(destination)
        if not dst.exists():
            skipped += 1
            continue
        try:
            target = unique_destination(src) if src.exists() else src
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(target))
            touched_dirs.add(dst.parent)
            restored += 1
        except OSError:
            skipped += 1
    for directory in touched_dirs:  # tidy up category folders we emptied
        try:
            directory.rmdir()
        except OSError:
            pass
    return restored, skipped
