import customtkinter as ctk

import config
from utils import settings_manager
from utils.statistics import get_latest_statistics

from . import anim, theme
from .about_page import AboutPage
from .cursor_fx import CursorFX
from .dashboard import Dashboard
from .history_page import HistoryPage
from .organize_page import OrganizePage
from .settings_page import SettingsPage
from .sidebar import ITEMS, Sidebar
from .widgets import Toast


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        settings = settings_manager.load()
        anim.ENABLED = bool(settings["animations"])
        theme.set_accent(settings["accent"])
        theme.set_mode(settings["appearance"])
        ctk.set_default_color_theme("blue")

        self.title(config.APP_NAME)
        self.geometry("1240x760")
        self.minsize(1040, 640)
        self.configure(fg_color=theme.PALETTE["bg"])
        theme.init_scale(self)
        self._set_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.container = ctk.CTkFrame(self, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")

        self.dashboard = Dashboard(self.container)
        self.organize_page = OrganizePage(self.container, self)
        self.history_page = HistoryPage(self.container, self)
        self.settings_page = SettingsPage(self.container, self)
        self.about_page = AboutPage(self.container, self)
        self.pages = {"dashboard": self.dashboard, "organize": self.organize_page, "history": self.history_page,
                      "settings": self.settings_page, "about": self.about_page}
        self.current = ""
        self._slide = None
        self.toast = Toast(self)

        self.cursor_fx = CursorFX(self)
        for index, (_, key) in enumerate(ITEMS, start=1):
            self.bind_all(f"<Control-Key-{index}>", lambda _e, k=key: self.show_page(k))

        self.dashboard.stats = get_latest_statistics()
        self.show_page("dashboard")
        if settings["cursor_effects"]:
            self.after(500, lambda: self.set_cursor_effects(True))
        theme.on_change(self._on_theme)
        self.protocol("WM_DELETE_WINDOW", self._close)

    # ------------------------------------------------------------------ navigation
    def show_page(self, key: str) -> None:
        if key == self.current or key not in self.pages:
            return
        for name, page in self.pages.items():
            if name != key:
                page.place_forget()
        page = self.pages[key]
        first = not self.current
        self.current = key
        self.sidebar.select(key, animate=not first)
        if self._slide:
            self._slide.cancel()
        page.place(x=0, y=24, relwidth=1, relheight=1)
        page.lift()
        self._slide = anim.Tween(self, 320, lambda t: page.place(x=0, y=int(24 * (1 - t)), relwidth=1, relheight=1),
                                 easing=anim.ease_out_cubic)
        if hasattr(page, "on_show"):
            page.on_show()

    def after_history_change(self, stats) -> None:
        """Called by pages when the history changed (new run, undo, clear)."""
        latest = stats if stats is not None else get_latest_statistics()
        self.dashboard.update_statistics(latest, animate=False)
        if settings_manager.get("auto_refresh_history") or stats is None:
            self.history_page.load_history()

    # ------------------------------------------------------------------ effects / theme
    def set_cursor_effects(self, enabled: bool) -> None:
        if enabled:
            if not self.cursor_fx.enable() and CursorFX.supported():
                self.toast.show("Cursor effects are not available on this system", "error")
        else:
            self.cursor_fx.disable()

    def _on_theme(self) -> None:
        self.configure(fg_color=theme.PALETTE["bg"])

    def _set_icon(self) -> None:
        icon = config.ASSETS_DIR / "app.ico"
        if icon.exists():
            try:  # CustomTkinter resets the icon shortly after start-up on Windows, so set it late
                self.after(250, lambda: self.iconbitmap(str(icon)))
            except Exception:
                pass

    def _close(self) -> None:
        self.cursor_fx.disable()
        self.destroy()
