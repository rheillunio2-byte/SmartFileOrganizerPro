# SmartFileOrganizerPro 📁

![Version](https://img.shields.io/badge/version-2.0.0-6366f1)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Pillow](https://img.shields.io/badge/Graphics-Pillow-yellow)
![PyInstaller](https://img.shields.io/badge/Packaging-PyInstaller-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A **Python desktop app that sorts messy folders into tidy, categorized folders** — safely, with a live preview,
one-click undo, and an interface full of motion.

---

# 🖥️ Application Preview

> **Note:** the screenshots below are from v1.0. Captures of the v2.0 interface will replace them.

<table>
  <tr>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Dashboard).png" width="400">
      <br>
      <b>Dashboard</b>
    </td>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Organize).png" width="400">
      <br>
      <b>Organize Files</b>
    </td>
  </tr>

  <tr>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(History).png" width="400">
      <br>
      <b>History Tracking</b>
    </td>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Settings).png" width="400">
      <br>
      <b>Application Settings</b>
    </td>
  </tr>

  <tr>
    <td align="center" colspan="2">
      <img src="Images/SmartFileOrganizerPro%20(About).png" width="400">
      <br>
      <b>About Section</b>
    </td>
  </tr>
</table>

---

# 📌 Overview

SmartFileOrganizerPro looks at the loose files in a folder, classifies them by extension, and moves them into
category sub-folders:

- 🖼️ Images · 📄 Documents · 🎬 Videos · 🎵 Music · 📦 Archives · 📁 Others

You choose the folder and which categories to touch. Nothing is overwritten, every run is recorded, and the latest
run can be undone.

---

# ✨ Features

### Organizing
✅ Extension-based classification into six categories  
✅ Choose which categories to organize (toggle the floating pills)  
✅ **Preview only** mode — see what would move without moving anything  
✅ **Undo last run** — files go back where they came from  
✅ Never overwrites: name clashes become `name (1).ext`, `name (2).ext`…  
✅ Skips hidden files, folders, `desktop.ini` and `Thumbs.db`  
✅ Runs in a background thread with live progress — the window never freezes  
✅ One unreadable file never aborts the run  

### History & statistics
✅ Animated dashboard: per-category cards, distribution chart, lifetime totals  
✅ Searchable history (folder, date, category) with CSV export  
✅ Old v1 `history.txt` is imported automatically on first launch  

### Interface & motion
✅ Dark / Light / System themes and five accent colours  
✅ Animated sidebar, page transitions, count-up numbers, toast notifications  
✅ **TechWordmark** hero — hover a letter to turn it into a dashed vector outline; drag, kick or watch it sweep  
✅ **FolderFloat** picker — a folder releases floating, draggable, colliding category pills  
✅ **Animated cursor** — ring, comet trail and click ripples *(Windows)*  
✅ Respects your preferences: animations and cursor effects can be switched off in Settings  

---

# 🛠️ Technologies Used

| Area | Tech |
| --- | --- |
| Language | Python 3.10+ |
| GUI | CustomTkinter + raw Tk canvases for the animated parts |
| Graphics | Pillow (renders the wordmark letters and their outlines) |
| Packaging | PyInstaller |
| Storage | JSON files in a per-user data folder |
| Standard library | `pathlib`, `shutil`, `threading`, `queue`, `json`, `csv` |

> The wordmark and floating-folder interactions are **inspired by the React Bits `TechText` and `FolderFloat`
> components** and re-implemented natively for Tkinter — no web view or JavaScript is involved.

---

# 🚀 Installation

```bash
git clone https://github.com/rheillunio2-byte/SmartFileOrganizerPro.git
cd SmartFileOrganizerPro
pip install -r requirements.txt
python app.py
```

Tkinter ships with the official Python installers for Windows and macOS. On Debian/Ubuntu install it with
`sudo apt install python3-tk`.

## Build an executable (Windows)

```bash
pip install pyinstaller
pyinstaller "Smart File Organizer Pro.spec"
```

The executable appears in `dist/`.

---

# 📖 How It Works

1. Pick a folder (click the drop zone).
2. The folder is scanned and each category pill shows how many files it will take.
3. Switch categories on/off, optionally enable **Preview only**, then press **Organize Files**.
4. Files are moved on a worker thread while the progress bar fills.
5. The run is saved to history together with the information needed to undo it.

```
Before:                          After:

📁 Downloads                      📁 Downloads
 ├── image.jpg                     ├── Images
 ├── document.pdf                  │    └── image.jpg
 └── song.mp3                      ├── Documents
                                   │    └── document.pdf
                                   └── Music
                                        └── song.mp3
```

---

# ⌨️ Shortcuts

| Keys | Action |
| --- | --- |
| `Ctrl+1` … `Ctrl+5` | Dashboard · Organize · History · Settings · About |

---

# 📂 Project Structure

```
SmartFileOrganizerPro/
├── app.py                  # entry point
├── config.py               # version, paths, constants
├── requirements.txt
├── assets/                 # app icon (app.ico / app.png)
├── ui/
│   ├── main_window.py      # window, navigation, page transitions
│   ├── sidebar.py          # animated navigation
│   ├── dashboard.py        # stats, chart, wordmark hero
│   ├── organize_page.py    # folder picker, FolderFloat, worker thread
│   ├── history_page.py     # searchable history, undo, CSV export
│   ├── settings_page.py    # appearance, behaviour, motion
│   ├── about_page.py
│   ├── widgets.py          # cards, buttons, bar chart, drop zone, toast, icons
│   ├── wordmark.py         # TechWordmark (interactive wordmark)
│   ├── folder_float.py     # FolderFloat (floating category pills)
│   ├── cursor_fx.py        # animated cursor overlay (Windows)
│   ├── anim.py             # tween / easing / canvas-loop helpers
│   └── theme.py            # palette, fonts, DPI helpers
├── utils/
│   ├── organizer.py        # scan / organize / undo (no UI code)
│   ├── file_types.py       # categories, extensions, colours
│   ├── history_manager.py  # JSON history (+ legacy import)
│   ├── statistics.py
│   ├── settings_manager.py
│   └── system.py
├── tests/
│   ├── test_core.py        # unit tests for the logic layer
│   ├── smoke_ui.py         # headless UI smoke test (stubbed Tk)
│   └── stub_tk.py
├── docs/CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── Images/
```

**Where your data lives:** `%APPDATA%\SmartFileOrganizerPro` on Windows
(`~/Library/Application Support/…` on macOS, `~/.local/share/…` on Linux) —
`history.json` and `settings.json`. Use *About → Open data folder* to jump there.

---

# ✅ Tests

```bash
python -m unittest discover -s tests -t .     # logic layer (real files, no GUI needed)
python -m tests.smoke_ui                      # UI wiring with a stubbed Tk (no display needed)
```

---

# 🔮 Future Improvements

- Drag-and-drop a folder onto the drop zone
- User-defined categories and extension rules
- Duplicate file detection
- Sub-folder (recursive) organizing
- Scheduled / watch-folder auto-organizing
- Live accent-colour switching (currently applies on next launch)

---

# 👨‍💻 Developer

**Rheil Evans T. Lunio**  
Computer Science Student  
University of Science and Technology of Southern Philippines (USTP)

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

Please read the [CONTRIBUTING.md](https://github.com/rheillunio2-byte/SmartFileOrganizerPro/blob/main/docs/CONTRIBUTING.md) guide before submitting changes. Release notes are in the [CHANGELOG](CHANGELOG.md).

---

# 📄 License

This project is licensed under the [MIT License](https://github.com/rheillunio2-byte/SmartFileOrganizerPro/blob/main/LICENSE).
