# Changelog

## 2.0.0

### New
- Complete UI redesign: modern palette, dark / light / system themes, five selectable accent colours.
- Animated sidebar with a sliding active indicator and hover transitions.
- Page transitions, count-up statistics, animated distribution chart and staggered history cards.
- **TechWordmark** hero on the dashboard: letters turn into dashed vector outlines on hover, a selection
  frame glides between them, specks blink, letters can be dragged and spring back, clicks kick and ripple.
- **FolderFloat** category picker on the Organize page: a folder releases floating, draggable pills;
  clicking a pill switches that category on or off.
- Animated cursor (ring, comet trail, click ripples) — Windows.
- Animated drop-zone with a marching-ants border; toast notifications.
- Preview-only (dry run) mode, one-click **Undo last run**, history export to CSV.
- Background worker thread with live progress — the window no longer freezes on large folders.
- Settings now persist (`settings.json`) and actually take effect.
- App icon, `requirements.txt`, unit tests and a headless UI smoke test.

### Fixed
- `organize()` was defined twice and printed debug output; the stray debug code is gone.
- Existing files are never overwritten any more (name clashes get ` (1)`, ` (2)`…).
- History used a path relative to the working directory and broke when launched from elsewhere; it now lives in a
  per-user data folder. Old `history/history.txt` is imported automatically on first run.
- One unreadable file no longer aborts the whole run.
- Hidden files and `desktop.ini` / `Thumbs.db` are skipped.
- README referenced `main.py` and a missing `requirements.txt`; the PyInstaller spec referenced a missing icon.
- Removed the unused `pandas` dependency from the docs.

### Changed
- History is stored as JSON (`history.json`) and includes the data needed for undo.

## 1.0.0
- Initial release.
