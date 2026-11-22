"""Headless UI smoke test (run:  python -m tests.smoke_ui)."""

import os
import sys
import tempfile
import threading
import time
from pathlib import Path

os.environ["SFOP_DATA_DIR"] = tempfile.mkdtemp()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests import stub_tk  # noqa: E402

tk, ctk = stub_tk.install()

import config  # noqa: E402
from ui import anim, theme, wordmark, cursor_fx  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402
from utils import history_manager, settings_manager  # noqa: E402

wordmark.ImageTk = None  # no real Tk imaging here

adv, fire = stub_tk.advance, stub_tk.fire


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        raise SystemExit(1)


settings_manager.load(); settings_manager.set_value("auto_open_folder", False)
app = MainWindow()
adv(0.5)
check(app.current == "dashboard", "main window builds and shows the dashboard")

# canvases get a size event -> build glyphs / folder / bar chart / drop zone
for w in list(stub_tk.Widget.registry):
    if w._binds.get("<Configure>") and not w._destroyed:
        fire(w, "<Configure>", width=w.kw.get("width_px", 900), height=w.kw.get("height_px", 400))
adv(3.0)

wm = app.dashboard.wordmark
check(len(wm.glyphs) == 9, f"wordmark built {len(wm.glyphs)} glyphs (SmartFile)")
check(all(g.off == [0.0, 0.0] for g in wm.glyphs), "wordmark intro settled to home positions")

# hover a letter, drag it, release, click-kick it
g0 = wm.glyphs[3]
x1, y1, x2, y2 = g0.ink()
cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
fire(wm, "<Motion>", x=cx, y=cy)
adv(0.6)
check(wm._focus == 3 and g0.outline > 0.9, "hovering a letter selects it and turns it into an outline")
fire(wm, "<ButtonPress-1>", x=cx, y=cy)
fire(wm, "<Motion>", x=cx + 40, y=cy - 30)
adv(0.3)
check(g0.off[0] > 20, "dragging moves the letter")
fire(wm, "<ButtonRelease-1>", x=cx + 40, y=cy - 30)
adv(3.0)
check(abs(g0.off[0]) < 1 and abs(g0.off[1]) < 1, "dragged letter springs back home")
fire(wm, "<ButtonPress-1>", x=cx, y=cy)
fire(wm, "<ButtonRelease-1>", x=cx, y=cy)
adv(0.12)
check(any(abs(g.off[1]) > 1 for g in wm.glyphs), "clicking kicks the letter and ripples to neighbours")
adv(3.0)
fire(wm, "<Leave>")
adv(5.0)  # idle sweep
check(wm.inside is False, "idle sweep runs without errors")

# all pages
for key in ("organize", "history", "settings", "about", "dashboard"):
    app.show_page(key)
    adv(0.6)
check(app.current == "dashboard", "navigation through all five pages")

# organize flow with a real temp folder
work = Path(tempfile.mkdtemp())
for name in ("a.png", "b.jpg", "c.pdf", "d.mp3", "e.zip", "f.weird", "g.mp4"):
    (work / name).write_text(name)
org = app.organize_page
app.show_page("organize")
adv(0.3)
ff = org.folder
fire(ff, "<Configure>", width=500, height=340)
adv(3.5)
org.set_folder(str(work))
check(org.counts["Images"] == 2 and org.counts["Others"] == 1, "folder scan fills category counts")
check(all(p.mode == "free" for p in ff.pills), "folder pills left the folder and entered the floating world")

pill = ff.pills[1]  # Documents: toggle off by clicking
fire(ff, "<ButtonPress-1>", x=pill.x, y=pill.y)
fire(ff, "<ButtonRelease-1>", x=pill.x, y=pill.y)
check("Documents" not in ff.get_selected(), "clicking a pill disables its category")
fire(ff, "<ButtonPress-1>", x=pill.x, y=pill.y)
fire(ff, "<ButtonRelease-1>", x=pill.x, y=pill.y)
check("Documents" in ff.get_selected(), "clicking again re-enables it")

pill = ff.pills[0]  # drag + throw
fire(ff, "<ButtonPress-1>", x=pill.x, y=pill.y)
fire(ff, "<Motion>", x=pill.x + 50, y=pill.y - 40)
adv(0.1)
fire(ff, "<ButtonRelease-1>", x=pill.x + 50, y=pill.y - 40)
adv(2.0)
zone_ok = all(0 <= p.x <= ff._geo["W"] and 0 <= p.y <= ff._geo["H"] for p in ff.pills)
check(zone_ok, "thrown pills stay inside the world")

# collapse / reopen the folder
g = ff._geo
fire(ff, "<ButtonPress-1>", x=g["fx"] + 20, y=g["fy"] + g["fh"] - 10)
adv(2.0)
check(not ff.open and all(p.mode == "hidden" for p in ff.pills), "clicking the folder closes it and pills return")
fire(ff, "<ButtonPress-1>", x=g["fx"] + 20, y=g["fy"] + g["fh"] - 10)
adv(3.0)
check(ff.open and all(p.mode == "free" for p in ff.pills), "reopening floats the pills out again")

# organize only Images + Others (turn off Music) with a real worker thread
mus = [p for p in ff.pills if p.key == "Music"][0]
fire(ff, "<ButtonPress-1>", x=mus.x, y=mus.y)
fire(ff, "<ButtonRelease-1>", x=mus.x, y=mus.y)
org.organize_files()
for _ in range(200):
    adv(0.05)
    if not org.running:
        break
    time.sleep(0.01)
check(not org.running, "organize finished")
check((work / "Images" / "a.png").exists() and (work / "d.mp3").exists(), "disabled category left untouched")
entries = history_manager.load_history()
check(len(entries) == 1 and entries[0]["stats"]["Images"] == 2 and entries[0]["moves"], "run saved to history with undo data")
check(app.dashboard.stats["Total"] == 6, "dashboard updated after the run")
check(org.undo_button.kw.get("state") == "normal", "undo button enabled")

# preview-only mode moves nothing
org.preview_only._value = 1
before = sorted(p.name for p in work.rglob("*"))
org.rescan()
org.organize_files()
for _ in range(100):
    adv(0.05)
    if not org.running:
        break
    time.sleep(0.01)
check(sorted(p.name for p in work.rglob("*")) == before, "preview-only does not move files")
org.preview_only._value = 0

# undo
org.undo_last()
check((work / "a.png").exists() and not (work / "Images").exists(), "undo restores files and tidies folders")
check(history_manager.last_undoable() is None and app.dashboard.stats["Total"] == 0, "dashboard/history reflect the undo")

# history page: render, search, export
hp = app.history_page
hp.load_history()
hp.search_entry._value = "images"
hp.search_history()
adv(1.0)
hp.search_entry._value = "zzz"
hp.search_history()

# settings
sp = app.settings_page
sp._on_mode("Light"); adv(0.2)
check(ctk._mode == "Light", "light mode applied")
sp._on_mode("Dark"); adv(0.2)
sp._on_accent("Emerald")
check(settings_manager.get("accent") == "Emerald", "accent persisted")
sp.switches["animations"]._value = 0
sp._on_switch("animations", sp._on_animations)
check(anim.ENABLED is False, "animations can be turned off")
app.show_page("about"); adv(0.5)  # instant tweens with animations off
sp.reset_settings()
check(anim.ENABLED is True and settings_manager.get("accent") == "Indigo", "reset restores defaults")

# cursor overlay on a pretend Windows machine
cursor_fx.CursorFX.supported = staticmethod(lambda: True)
cursor_fx.CursorFX._make_click_through = staticmethod(lambda w: True)
app.cursor_fx = cursor_fx.CursorFX(app)
check(app.cursor_fx.enable(), "cursor overlay enables")
for i in range(40):
    stub_tk.POINTER[:] = [100 + i * 9, 200 + i * 4]
    adv(0.016)
fire(app, "<ButtonPress-1>")
app.cursor_fx._on_press(stub_tk.Event(x_root=300, y_root=300))
adv(1.0)
app.cursor_fx.disable()
check(not app.cursor_fx.active, "cursor overlay disables cleanly")

app._close()
print("ALL SMOKE CHECKS PASSED")
