"""Animated cursor: a trailing comet, a springy ring and click ripples.

Implementation: a borderless, click-through, colour-keyed overlay window that sits above the
app window and follows the pointer. Click-through relies on Win32 extended window styles, so the
full effect is Windows-only; on other platforms ``enable()`` returns False and the app simply
skips it (the in-app hover effects still work everywhere).
"""

from __future__ import annotations

import sys
import time
import tkinter as tk
from collections import deque

from . import theme
from .anim import approach

KEY = "#010203"  # colour-key that becomes transparent
TRAIL = 14


class CursorFX:
    def __init__(self, root):
        self.root = root
        self.overlay: tk.Toplevel | None = None
        self.canvas: tk.Canvas | None = None
        self.active = False
        self._job = None
        self._geo = ""
        self._ring = [0.0, 0.0]
        self._press = 0.0
        self._history: deque[tuple[float, float]] = deque(maxlen=TRAIL * 2)
        self._ripples: list[tuple[float, float, float]] = []
        self._last = time.perf_counter()
        self._dots: list[int] = []
        self._ring_item = 0
        self._core = 0
        self._visible = True
        self._bound = False

    # ------------------------------------------------------------------ lifecycle
    @staticmethod
    def supported() -> bool:
        return sys.platform.startswith("win")

    def enable(self) -> bool:
        if self.active:
            return True
        if not self.supported():
            return False
        try:
            self._build()
        except Exception:
            self._teardown()
            return False
        self.active = True
        if not self._bound:  # bind once; handlers are no-ops while disabled
            self.root.bind_all("<ButtonPress-1>", self._on_press, add="+")
            self.root.bind_all("<ButtonRelease-1>", self._on_release, add="+")
            self._bound = True
        self._job = self.root.after(16, self._tick)
        return True

    def disable(self) -> None:
        self.active = False
        if self._job is not None:
            try:
                self.root.after_cancel(self._job)
            except (tk.TclError, ValueError):
                pass
            self._job = None
        self._teardown()

    def recolor(self) -> None:  # accent changed
        pass

    # ------------------------------------------------------------------ internals
    def _build(self) -> None:
        ov = tk.Toplevel(self.root)
        ov.withdraw()
        ov.overrideredirect(True)
        ov.transient(self.root)
        ov.configure(bg=KEY)
        ov.attributes("-transparentcolor", KEY)
        canvas = tk.Canvas(ov, bg=KEY, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        self.overlay, self.canvas = ov, canvas
        self._sync_geometry(force=True)
        ov.deiconify()
        ov.update_idletasks()
        if not self._make_click_through(ov):
            raise RuntimeError("click-through unavailable")
        accent = theme.c("accent")
        self._dots = [canvas.create_oval(0, 0, 0, 0, fill=accent, outline="") for _ in range(TRAIL)]
        self._ring_item = canvas.create_oval(0, 0, 0, 0, outline=accent, width=2, fill="")
        self._core = canvas.create_oval(0, 0, 0, 0, fill="#ffffff", outline="")

    @staticmethod
    def _make_click_through(win) -> bool:
        try:
            import ctypes

            user32 = ctypes.windll.user32
            hwnd = user32.GetParent(win.winfo_id()) or win.winfo_id()
            style = user32.GetWindowLongW(hwnd, -20)
            # LAYERED | TRANSPARENT (mouse passes through) | TOOLWINDOW | NOACTIVATE
            user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20 | 0x80 | 0x08000000)
            return True
        except Exception:
            return False

    def _teardown(self) -> None:
        if self.overlay is not None:
            try:
                self.overlay.destroy()
            except tk.TclError:
                pass
        self.overlay = self.canvas = None
        self._dots = []

    def _sync_geometry(self, force: bool = False) -> None:
        r = self.root
        geo = f"{r.winfo_width()}x{r.winfo_height()}+{r.winfo_rootx()}+{r.winfo_rooty()}"
        if force or geo != self._geo:
            self._geo = geo
            self.overlay.geometry(geo)

    def _on_press(self, event) -> None:
        if not self.active:
            return
        self._press = 1.0
        self._ripples.append((event.x_root, event.y_root, time.perf_counter()))

    def _on_release(self, _event) -> None:
        self._press = 0.0

    def _show(self, visible: bool) -> None:
        if visible != self._visible:
            self._visible = visible
            (self.overlay.deiconify if visible else self.overlay.withdraw)()

    def _tick(self) -> None:
        self._job = None
        if not self.active or self.canvas is None:
            return
        try:
            now = time.perf_counter()
            dt = min(0.05, now - self._last)
            self._last = now
            minimized = self.root.state() == "iconic" or not self.root.winfo_viewable()
            self._show(not minimized)
            if not minimized:
                self._draw(dt, now)
            self._job = self.root.after(16, self._tick)
        except tk.TclError:
            self.active = False

    def _draw(self, dt: float, now: float) -> None:
        self._sync_geometry()
        ox, oy = self.root.winfo_rootx(), self.root.winfo_rooty()
        mx = self.root.winfo_pointerx() - ox
        my = self.root.winfo_pointery() - oy
        inside = 0 <= mx <= self.root.winfo_width() and 0 <= my <= self.root.winfo_height()
        cv, S = self.canvas, theme.S
        accent = theme.c("accent")

        if not inside:  # hide everything while the pointer is outside the app
            for item in (*self._dots, self._ring_item, self._core):
                cv.coords(item, 0, 0, 0, 0)
            self._history.clear()
            return

        if not self._history:
            self._ring[:] = [mx, my]
        self._history.append((mx, my))
        self._ring[0] = approach(self._ring[0], mx, dt, 0.07)
        self._ring[1] = approach(self._ring[1], my, dt, 0.07)

        # comet trail: newest dot is biggest, oldest tiny; colour fades toward the background
        points = list(self._history)[::2][-TRAIL:]
        n = len(points)
        for i, item in enumerate(self._dots):
            if i < n:
                x, y = points[n - 1 - i]
                k = 1 - i / TRAIL
                r = (1.5 + 4.5 * k) * S
                cv.coords(item, x - r, y - r, x + r, y + r)
                cv.itemconfigure(item, fill=theme.mix(accent, "#ffffff", 0.35 * k) if i < 3 else accent)
            else:
                cv.coords(item, 0, 0, 0, 0)

        radius = (15 - 5 * self._press) * S
        rx, ry = self._ring
        cv.coords(self._ring_item, rx - radius, ry - radius, rx + radius, ry + radius)
        cv.itemconfigure(self._ring_item, outline=accent)
        core = 2.5 * S
        cv.coords(self._core, mx - core, my - core, mx + core, my + core)

        cv.delete("ripple")
        alive = []
        for x, y, t0 in self._ripples:
            p = (now - t0) / 0.55
            if p < 1:
                alive.append((x, y, t0))
                r = (12 + 40 * (1 - (1 - p) ** 3)) * S
                cv.create_oval(x - ox - r, y - oy - r, x - ox + r, y - oy + r, outline=theme.mix(accent, KEY, p),
                               width=max(1, int(3 * (1 - p) * S)), tags="ripple")
        self._ripples = alive
