# Contributing to SmartFileOrganizerPro

Thank you for your interest in contributing to **SmartFileOrganizerPro** (currently **v2.0.0**)!
Contributions, suggestions, and improvements are welcome.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/your-username/SmartFileOrganizerPro.git
   cd SmartFileOrganizerPro
   ```

3. **Create a virtual environment and install dependencies** (Python 3.10+):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

   Linux users may also need `sudo apt install python3-tk`.

4. **Run the app:**

   ```bash
   python app.py
   ```

5. **Create a branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Project Layout

| Folder | What belongs there |
| --- | --- |
| `utils/` | Logic only — scanning, moving, undo, history, settings. **No UI imports.** |
| `ui/` | Everything visual. One module per page, plus shared widgets/animation/theme modules. |
| `tests/` | Unit tests and the headless UI smoke test. |
| `assets/` | Icons and other bundled files. |

See the project structure in the [README](../README.md) for a file-by-file overview.

## Before You Open a Pull Request

Run both test suites — neither needs a display:

```bash
python -m unittest discover -s tests -t .
python -m tests.smoke_ui
```

Then try your change in the real app:

- Organize a **copy** of a test folder, check the result, then press **Undo last run**.
- Switch between Dark and Light themes — canvases must recolour correctly.
- Turn **Animations** off in Settings — nothing should break or hang.
- If you touched the cursor effect, test it on Windows (it is Windows-only).

Commit and push:

```bash
git add .
git commit -m "Add your changes"
git push origin feature/your-feature-name
```

Open a Pull Request and explain *what* changed and *why*. Screenshots or a short screen recording are very
helpful for UI changes.

## Development Guidelines

### General
- Write clean, readable Python 3.10+ code with clear names and comments for non-obvious logic.
- Keep dependencies minimal — discuss before adding a new one.
- Keep commits small and descriptive.

### Logic (`utils/`)
- **Never lose or overwrite a user's files.** Moves must be collision-safe and undoable.
- Keep functions free of UI code so they can be unit-tested; add a test for every behaviour you add or fix.
- Record anything needed to reverse an action in the history entry.

### UI (`ui/`)
- Take colours from `ui/theme.py` (`theme.PALETTE[...]` for CustomTkinter widgets, `theme.c(...)` for raw canvases).
  Do not hard-code hex colours in pages.
- Canvases that draw their own colours must register a `refresh_colors` callback with `theme.on_change(...)`.
- Size raw-canvas content with `theme.px(...)` / `theme.canvas_font(...)` so it stays correct on high-DPI displays.
- Animate with the helpers in `ui/anim.py` (`Tween`, `CanvasLoop`, easing functions). They respect the user's
  *Animations* setting and stop safely when a widget is destroyed.
- Never block the UI thread: long work goes on a worker thread and reports back through a `queue` (see
  `organize_page.py`).
- Pages expose an optional `on_show()` hook, called each time the page is shown.
- Keep animations short and purposeful (roughly 150–500 ms) and always provide a way to disable them.

### Code Style
- Modular, maintainable structure; one responsibility per module.
- Use type hints on new public functions.
- Prefer `pathlib` over string paths.

## Reporting Bugs

Please open an issue and include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior and actual behavior
- Screenshots (if applicable)
- Your Python version, operating system and display scaling (for UI glitches)
- The app version (*About* page)

## Suggesting Features

Feature suggestions are welcome. Please include:

- Feature description
- Why it would be useful
- How it could improve SmartFileOrganizerPro

## License

By contributing to SmartFileOrganizerPro, you agree that your contributions will be licensed under the project's
**MIT License**.

Thank you for helping improve **SmartFileOrganizerPro**!
