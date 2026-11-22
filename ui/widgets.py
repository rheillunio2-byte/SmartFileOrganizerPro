"""Reusable animated widgets: cards, stat cards, bar chart, drop zone, toast, buttons."""

from __future__ import annotations

import math
import tkinter as tk

import customtkinter as ctk

from . import anim, theme
from .anim import CanvasLoop, Tween, approach, ease_out_cubic
from .folder_float import rounded


# ---------------------------------------------------------------------------- helpers
def card(master, **kwargs) -> ctk.CTkFrame:
    options = dict(fg_color=theme.PALETTE["surface"], border_width=1, border_color=theme.PALETTE["border"],
                   corner_radius=16)
    options.update(kwargs)
    return ctk.CTkFrame(master, **options)


def button(master, text: str, command=None, kind: str = "primary", **kwargs) -> ctk.CTkButton:
    styles = {
        "primary": dict(fg_color=theme.PALETTE["accent"], hover_color=theme.PALETTE["accent_hover"],
                        text_color="#ffffff"),
        "secondary": dict(fg_color=theme.PALETTE["surface2"], hover_color=theme.PALETTE["border"],
                          text_color=theme.PALETTE["text"], border_width=1, border_color=theme.PALETTE["border"]),
        "danger": dict(fg_color=theme.PALETTE["danger"], hover_color=theme.PALETTE["danger_hover"],
                       text_color="#ffffff"),
    }
    options = dict(text=text, command=command, corner_radius=10, height=42, font=theme.font(14, "bold"))
    options.update(styles[kind])
    options.update(kwargs)
    return ctk.CTkButton(master, **options)


def pointer_inside(widget) -> bool:
    try:
        x, y = widget.winfo_pointerxy()
        return (widget.winfo_rootx() <= x < widget.winfo_rootx() + widget.winfo_width()
                and widget.winfo_rooty() <= y < widget.winfo_rooty() + widget.winfo_height())
    except tk.TclError:
        return False


def bind_hover(widget, on_enter, on_leave) -> None:
    """Hover handlers that survive the pointer moving between a widget's children."""

    def enter(_e=None):
        on_enter()

    def leave(_e=None):
        widget.after(25, lambda: None if pointer_inside(widget) else on_leave())

    def attach(w):
        try:
            w.bind("<Enter>", enter, add="+")
            w.bind("<Leave>", leave, add="+")
        except (tk.TclError, NotImplementedError, ValueError):
            pass
        for child in w.winfo_children():
            attach(child)

    attach(widget)


def elide(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    keep = max(4, limit - 1)
    head = keep // 3
    return text[:head] + "…" + text[-(keep - head):]


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master, fg_color="transparent")
        self.title = ctk.CTkLabel(self, text=title, font=theme.font(28, "bold"), text_color=theme.PALETTE["text"],
                                  anchor="w")
        self.title.pack(anchor="w")
        self.sub = ctk.CTkLabel(self, text=subtitle, font=theme.font(14), text_color=theme.PALETTE["muted"], anchor="w")
        self.sub.pack(anchor="w", pady=(2, 8))
        self.bar = ctk.CTkFrame(self, height=4, width=0, corner_radius=2, fg_color=theme.PALETTE["accent"])
        self.bar.pack(anchor="w")

    def play(self) -> None:
        Tween(self, 520, lambda t: self.bar.configure(width=max(1, int(64 * t))), easing=ease_out_cubic, delay=120)


# ---------------------------------------------------------------------------- icons
def draw_icon(cv: tk.Canvas, name: str, color: str, size: int = 20) -> None:
    cv.delete("all")
    s = theme.px(size)
    u = s / 20.0
    kw = dict(outline=color, width=max(1, int(1.6 * u)), fill="")
    if name == "dashboard":
        for x, y, w, h in ((2, 2, 7, 9), (11, 2, 7, 5), (2, 13, 7, 5), (11, 9, 7, 9)):
            cv.create_rectangle(x * u, y * u, (x + w) * u, (y + h) * u, **kw)
    elif name == "organize":
        cv.create_polygon([2 * u, 5 * u, 8 * u, 5 * u, 10 * u, 7 * u, 18 * u, 7 * u, 18 * u, 16 * u, 2 * u, 16 * u], **kw)
        cv.create_line(7 * u, 11.5 * u, 13 * u, 11.5 * u, fill=color, width=kw["width"])
    elif name == "history":
        cv.create_oval(2.5 * u, 2.5 * u, 17.5 * u, 17.5 * u, **kw)
        cv.create_line(10 * u, 5.5 * u, 10 * u, 10 * u, 13.5 * u, 12 * u, fill=color, width=kw["width"])
    elif name == "settings":
        for y, knob in ((5, 7), (10, 13), (15, 5)):
            cv.create_line(2 * u, y * u, 18 * u, y * u, fill=color, width=kw["width"])
            cv.create_oval((knob - 2) * u, (y - 2) * u, (knob + 2) * u, (y + 2) * u, outline=color,
                           width=kw["width"], fill=theme.c("sidebar"))
    elif name == "about":
        cv.create_oval(2.5 * u, 2.5 * u, 17.5 * u, 17.5 * u, **kw)
        cv.create_line(10 * u, 9 * u, 10 * u, 14 * u, fill=color, width=kw["width"])
        cv.create_oval(9 * u, 5.4 * u, 11 * u, 7.4 * u, fill=color, outline=color)


# ---------------------------------------------------------------------------- stat card
class StatCard(ctk.CTkFrame):
    def __init__(self, master, name: str, color: str):
        super().__init__(master, fg_color=theme.PALETTE["surface"], border_width=1,
                         border_color=theme.PALETTE["border"], corner_radius=16)
        self.color, self.name = color, name
        self._hover = 0.0
        self._tween: Tween | None = None

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))
        dot = ctk.CTkFrame(top, width=10, height=10, corner_radius=5, fg_color=color)
        dot.pack(side="left")
        ctk.CTkLabel(top, text=name, font=theme.font(14, "bold"), text_color=theme.PALETTE["muted"]).pack(
            side="left", padx=(8, 0))
        self.share = ctk.CTkLabel(top, text="0%", font=theme.font(12), text_color=theme.PALETTE["muted"])
        self.share.pack(side="right")

        self.value = ctk.CTkLabel(self, text="0", font=theme.font(36, "bold"), text_color=theme.PALETTE["text"],
                                  anchor="w")
        self.value.pack(fill="x", padx=18, pady=(6, 6))
        self.bar = ctk.CTkProgressBar(self, height=6, corner_radius=3, progress_color=color,
                                      fg_color=theme.PALETTE["surface2"])
        self.bar.set(0)
        self.bar.pack(fill="x", padx=18, pady=(0, 18))
        bind_hover(self, lambda: self._set_hover(1.0), lambda: self._set_hover(0.0))

    def _set_hover(self, target: float) -> None:
        if self._tween:
            self._tween.cancel()
        start = self._hover

        def update(t):
            self._hover = start + (target - start) * t
            self.configure(border_color=theme.mix(theme.c("border"), self.color, self._hover))

        self._tween = Tween(self, 180, update)

    def animate_to(self, value: int, total: int, delay: int = 0) -> None:
        share = (value / total) if total else 0.0
        anim.count_up(self, self.value, value, 900, delay)
        Tween(self, 900, lambda t: (self.bar.set(share * t), self.share.configure(text=f"{round(share * 100 * t)}%")),
              delay=delay)


# ---------------------------------------------------------------------------- bar chart
class BarChart(tk.Canvas):
    ROW = 34

    def __init__(self, master, rows: list[tuple[str, str]], bg_name: str = "surface"):
        super().__init__(master, bg=theme.c(bg_name), highlightthickness=0, bd=0, height=theme.px(self.ROW * len(rows) + 8))
        self.rows, self.bg_name = rows, bg_name
        self.values = {k: 0 for k, _ in rows}
        self.t = 1.0
        self._tween: Tween | None = None
        self.bind("<Configure>", lambda _e: self._draw())
        theme.on_change(self.refresh_colors)

    def refresh_colors(self) -> None:
        self.configure(bg=theme.c(self.bg_name))
        self._draw()

    def set_data(self, values: dict[str, int]) -> None:
        self.values = {k: int(values.get(k, 0)) for k, _ in self.rows}
        if self._tween:
            self._tween.cancel()
        self.t = 0.0

        def update(t):
            self.t = t
            self._draw()

        self._tween = Tween(self, 900, update, delay=150)

    def _draw(self) -> None:
        self.delete("all")
        w = self.winfo_width()
        if w < 60:
            return
        label_w, value_w = theme.px(96), theme.px(54)
        left, right = label_w, w - value_w
        peak = max(max(self.values.values()), 1)
        for i, (key, color) in enumerate(self.rows):
            y = theme.px(self.ROW * i + self.ROW / 2 + 4)
            self.create_text(0, y, text=key, anchor="w", fill=theme.c("muted"), font=theme.canvas_font(13))
            h = theme.px(10)
            self.create_polygon(rounded(left, y - h / 2, right, y + h / 2, h / 2), smooth=True,
                                fill=theme.c("surface2"), outline="")
            frac = self.values[key] / peak * self.t
            if frac > 0.004:
                self.create_polygon(rounded(left, y - h / 2, left + max(h, (right - left) * frac), y + h / 2, h / 2),
                                    smooth=True, fill=color, outline="")
            self.create_text(w, y, text=f"{round(self.values[key] * self.t):,}", anchor="e",
                             fill=theme.c("text"), font=theme.canvas_font(13, "bold"))


# ---------------------------------------------------------------------------- drop zone
class DropZone(tk.Canvas, CanvasLoop):
    """Click-to-pick area with a marching-ants border and a breathing folder icon."""

    def __init__(self, master, on_click, bg_name: str = "surface", height: int = 150):
        super().__init__(master, bg=theme.c(bg_name), highlightthickness=0, bd=0, height=theme.px(height))
        self.bg_name, self.on_click = bg_name, on_click
        self.path = ""
        self.hover = 0.0
        self._hover_t = 0.0
        self._ants = 0.0
        self._clock = 0.0
        self._loop_init()
        self.bind("<Configure>", lambda _e: self._build())
        self.bind("<Enter>", lambda _e: self._set_hover(1.0))
        self.bind("<Leave>", lambda _e: self._set_hover(0.0))
        self.bind("<ButtonRelease-1>", lambda _e: self.on_click())
        self.bind("<Destroy>", lambda _e: self.stop_loop(), add="+")
        theme.on_change(self.refresh_colors)
        self.configure(cursor="hand2")
        self.start_loop()

    def _set_hover(self, v: float) -> None:
        self._hover_t = v

    def refresh_colors(self) -> None:
        self.configure(bg=theme.c(self.bg_name))
        self._build()

    def set_path(self, path: str) -> None:
        self.path = path
        self._update_text()

    def _build(self) -> None:
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60:
            return
        self.delete("all")
        pad = theme.px(6)
        self._border = self.create_polygon(rounded(pad, pad, w - pad, h - pad, theme.px(16)), smooth=True, fill="",
                                           outline=theme.c("border"), width=2, dash=(7, 6))
        cx, cy = theme.px(70), h / 2
        self._glow = self.create_oval(0, 0, 0, 0, outline="", fill=theme.c("accent_soft"))
        u = theme.S
        self._icon = self.create_polygon([cx - 22 * u, cy - 13 * u, cx - 6 * u, cy - 13 * u, cx - 1 * u, cy - 7 * u,
                                          cx + 22 * u, cy - 7 * u, cx + 22 * u, cy + 17 * u, cx - 22 * u, cy + 17 * u],
                                         fill="", outline=theme.c("accent"), width=2)
        self._plus = self.create_line(cx - 7 * u, cy + 5 * u, cx + 7 * u, cy + 5 * u, fill=theme.c("accent"), width=2)
        self._plus2 = self.create_line(cx, cy - 2 * u, cx, cy + 12 * u, fill=theme.c("accent"), width=2)
        tx = theme.px(124)
        self._title = self.create_text(tx, cy - 14 * u, anchor="w", text="", fill=theme.c("text"),
                                       font=theme.canvas_font(17, "bold"))
        self._sub = self.create_text(tx, cy + 14 * u, anchor="w", text="", fill=theme.c("muted"),
                                     font=theme.canvas_font(12))
        self._cy, self._cx = cy, cx
        self._update_text()

    def _update_text(self) -> None:
        if not hasattr(self, "_title") or not self.winfo_width() > 60:
            return
        chars = max(20, int((self.winfo_width() - theme.px(150)) / theme.px(7.4)))
        if self.path:
            self.itemconfigure(self._title, text="Folder selected")
            self.itemconfigure(self._sub, text=elide(self.path, chars))
        else:
            self.itemconfigure(self._title, text="Choose a folder to organize")
            self.itemconfigure(self._sub, text="Click here to browse — nothing moves until you press Organize")

    def step(self, dt: float) -> None:
        if not hasattr(self, "_border"):
            return
        self.hover = approach(self.hover, self._hover_t, dt, 0.1)
        self._clock += dt
        self._ants += dt * (14 + 46 * self.hover)
        accent = theme.c("accent")
        self.itemconfigure(self._border, dashoffset=-int(self._ants),
                           outline=theme.mix(theme.c("border"), accent, 0.25 + 0.75 * self.hover),
                           width=2 if self.hover < 0.5 else 3)
        r = (30 + 4 * math.sin(self._clock * 2.2) + 6 * self.hover) * theme.S
        self.coords(self._glow, self._cx - r, self._cy - r + 2, self._cx + r, self._cy + r + 2)


# ---------------------------------------------------------------------------- toast
class Toast(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color=theme.PALETTE["surface"], border_width=1,
                         border_color=theme.PALETTE["border"], corner_radius=12)
        self.root = root
        self._dot = ctk.CTkFrame(self, width=10, height=10, corner_radius=5, fg_color=theme.PALETTE["success"])
        self._dot.pack(side="left", padx=(16, 8), pady=16)
        self._label = ctk.CTkLabel(self, text="", font=theme.font(13, "bold"), text_color=theme.PALETTE["text"],
                                   justify="left")
        self._label.pack(side="left", padx=(0, 18))
        self._job = None
        self._tween: Tween | None = None
        self._shown = False

    def show(self, text: str, kind: str = "success", duration: int = 3400) -> None:
        color = {"success": "success", "error": "danger", "info": "accent"}.get(kind, "success")
        self._dot.configure(fg_color=theme.PALETTE[color])
        self._label.configure(text=text)
        if self._job:
            self.after_cancel(self._job)
        if self._tween:
            self._tween.cancel()
        self.lift()
        self._slide(0.0 if not self._shown else 1.0, 1.0)
        self._shown = True
        self._job = self.after(duration, self.hide)

    def hide(self) -> None:
        if self._tween:
            self._tween.cancel()
        self._slide(1.0, 0.0, done=lambda: (self.place_forget(), setattr(self, "_shown", False)))

    def _slide(self, start: float, end: float, done=None) -> None:
        def update(t):
            k = start + (end - start) * t
            self.place(relx=1.0, rely=1.0, x=int(-24 + (1 - k) * 380), y=-24, anchor="se")

        self._tween = Tween(self, 380, update, easing=anim.ease_out_back if end > start else anim.ease_in_out, done=done)
