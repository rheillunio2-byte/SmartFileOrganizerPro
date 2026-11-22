import tkinter as tk

import customtkinter as ctk

import config
from . import theme
from .anim import Tween, ease_out_back
from .widgets import bind_hover, draw_icon

ITEMS = [("Dashboard", "dashboard"), ("Organize", "organize"), ("History", "history"),
         ("Settings", "settings"), ("About", "about")]
ITEM_H, ITEM_GAP, ITEM_TOP = 46, 6, 150


class NavItem(ctk.CTkFrame):
    def __init__(self, master, text: str, icon: str, command, width: int = 212):
        super().__init__(master, fg_color="transparent", corner_radius=10, width=width, height=ITEM_H, cursor="hand2")
        self.icon_name, self.active, self.hover = icon, False, 0.0
        self._tween = None
        self.pack_propagate(False)
        self.icon = tk.Canvas(self, width=theme.px(20), height=theme.px(20), highlightthickness=0, bd=0,
                              bg=theme.c("sidebar"))
        self.icon.pack(side="left", padx=(16, 12))
        self.label = ctk.CTkLabel(self, text=text, font=theme.font(15, "bold"), text_color=theme.PALETTE["muted"],
                                  anchor="w")
        self.label.pack(side="left", fill="x", expand=True)
        for w in (self, self.icon, self.label):
            w.bind("<Button-1>", lambda _e: command(), add="+")
        bind_hover(self, lambda: self._animate(1.0), lambda: self._animate(0.0))
        self.paint()

    def set_active(self, value: bool) -> None:
        self.active = value
        self.paint()

    def _animate(self, target: float) -> None:
        if self._tween:
            self._tween.cancel()
        start = self.hover

        def update(t):
            self.hover = start + (target - start) * t
            self.paint()

        self._tween = Tween(self, 160, update)

    def paint(self) -> None:
        bg = theme.c("sidebar")
        if self.active:
            fill, ink = theme.c("accent_soft"), theme.c("accent")
        else:
            fill = theme.mix(bg, theme.c("surface2"), self.hover)
            ink = theme.mix(theme.c("muted"), theme.c("text"), self.hover)
        self.configure(fg_color=fill)
        self.icon.configure(bg=fill)
        self.label.configure(text_color=ink)
        draw_icon(self.icon, self.icon_name, ink)

    def refresh_colors(self) -> None:
        self.paint()


class Sidebar(ctk.CTkFrame):
    WIDTH = 240

    def __init__(self, parent, on_select):
        super().__init__(parent, width=self.WIDTH, corner_radius=0, fg_color=theme.PALETTE["sidebar"])
        self.on_select = on_select
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.items: dict[str, NavItem] = {}
        self.active = ""
        self._indicator_tween = None

        # brand
        self.brand = tk.Canvas(self, width=theme.px(200), height=theme.px(84), highlightthickness=0, bd=0,
                               bg=theme.c("sidebar"))
        self.brand.place(x=20, y=26)
        self._draw_brand()

        for index, (text, key) in enumerate(ITEMS):
            item = NavItem(self, text, key, lambda k=key: self.on_select(k), width=self.WIDTH - 28)
            item.place(x=14, y=ITEM_TOP + index * (ITEM_H + ITEM_GAP))
            self.items[key] = item

        self.indicator = ctk.CTkFrame(self, width=4, height=26, corner_radius=2, fg_color=theme.PALETTE["accent"])
        self.indicator.place(x=0, y=ITEM_TOP + 10)

        self.footer = ctk.CTkLabel(self, text=f"v{config.APP_VERSION}   •   Ctrl+1–5 to navigate",
                                   font=theme.font(11), text_color=theme.PALETTE["muted"])
        self.footer.place(relx=0.5, rely=1.0, y=-18, anchor="s")
        theme.on_change(self.refresh_colors)

    def _draw_brand(self) -> None:
        cv = self.brand
        cv.delete("all")
        u, accent = theme.S, theme.c("accent")
        cv.create_polygon(self._rr(0, 4, 48 * u, 52 * u, 14 * u), smooth=True, fill=accent, outline="")
        cv.create_polygon([11 * u, 20 * u, 22 * u, 20 * u, 26 * u, 25 * u, 37 * u, 25 * u, 37 * u, 40 * u, 11 * u, 40 * u],
                          fill="", outline="#ffffff", width=2)
        cv.create_text(60 * u, 16 * u, text="Smart File", anchor="w", fill=theme.c("text"),
                       font=theme.canvas_font(17, "bold"))
        cv.create_text(60 * u, 38 * u, text="Organizer Pro", anchor="w", fill=theme.c("accent"),
                       font=theme.canvas_font(15, "bold"))

    @staticmethod
    def _rr(x1, y1, x2, y2, r):
        from .folder_float import rounded
        return rounded(x1, y1, x2, y2, r)

    def select(self, key: str, animate: bool = True) -> None:
        previous = self.active
        self.active = key
        for k, item in self.items.items():
            item.set_active(k == key)
        index = [k for _, k in ITEMS].index(key)
        target = ITEM_TOP + index * (ITEM_H + ITEM_GAP) + 10
        if not previous or not animate:
            self.indicator.place(x=0, y=target)
            return
        start = ITEM_TOP + [k for _, k in ITEMS].index(previous) * (ITEM_H + ITEM_GAP) + 10
        if self._indicator_tween:
            self._indicator_tween.cancel()
        self._indicator_tween = Tween(self, 420, lambda t: self.indicator.place(x=0, y=int(start + (target - start) * t)),
                                      easing=ease_out_back)

    def refresh_colors(self) -> None:
        self.brand.configure(bg=theme.c("sidebar"))
        self._draw_brand()
        for item in self.items.values():
            item.refresh_colors()
