import platform
import webbrowser

import customtkinter as ctk

import config
from utils.system import open_path

from . import theme
from .widgets import PageHeader, button, card

FEATURES = [
    ("Smart sorting", "Sorts by file type into Images, Documents, Videos, Music, Archives and Others."),
    ("Safe by design", "Never overwrites — name clashes get a numeric suffix. Hidden files are left alone."),
    ("One-click undo", "Every run records its moves, so the latest run can be reversed."),
    ("Preview mode", "See exactly what would move before anything is touched."),
    ("Live dashboard", "Animated statistics and a distribution chart for your last run."),
    ("Searchable history", "Filter past runs by folder, date or category and export them to CSV."),
]


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.app = app
        self.header = PageHeader(self, "About", f"{config.APP_NAME} • version {config.APP_VERSION}")
        self.header.pack(fill="x", padx=32, pady=(28, 14))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=26)
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="f")
        for index, (title, text) in enumerate(FEATURES):
            box = card(grid, corner_radius=14)
            box.grid(row=index // 3, column=index % 3, padx=6, pady=6, sticky="nsew")
            ctk.CTkLabel(box, text=title, font=theme.font(15, "bold"), text_color=theme.PALETTE["accent"],
                         anchor="w").pack(fill="x", padx=16, pady=(14, 2))
            ctk.CTkLabel(box, text=text, font=theme.font(12), text_color=theme.PALETTE["muted"], anchor="w",
                         justify="left", wraplength=210).pack(fill="x", padx=16, pady=(0, 14))

        dev = card(self)
        dev.pack(fill="x", padx=32, pady=(14, 8))
        ctk.CTkLabel(dev, text="Developed by", font=theme.font(12), text_color=theme.PALETTE["muted"]).pack(
            anchor="w", padx=22, pady=(16, 0))
        ctk.CTkLabel(dev, text=config.APP_AUTHOR, font=theme.font(20, "bold"), text_color=theme.PALETTE["text"]).pack(
            anchor="w", padx=22)
        ctk.CTkLabel(dev, text="Computer Science student • University of Science and Technology of Southern Philippines",
                     font=theme.font(13), text_color=theme.PALETTE["muted"]).pack(anchor="w", padx=22, pady=(0, 10))
        row = ctk.CTkFrame(dev, fg_color="transparent")
        row.pack(anchor="w", padx=22, pady=(0, 16))
        button(row, "GitHub repository", lambda: webbrowser.open(config.APP_REPO), width=170).pack(side="left", padx=(0, 8))
        button(row, "Open data folder", self._open_data, kind="secondary", width=160).pack(side="left")

        ctk.CTkLabel(self, text=f"Python {platform.python_version()}  •  CustomTkinter {ctk.__version__}  •  "
                                f"{platform.system()} {platform.release()}", font=theme.font(12),
                     text_color=theme.PALETTE["muted"]).pack(pady=(8, 0))
        ctk.CTkLabel(self, text="Interactive wordmark and floating-folder concepts are inspired by React Bits "
                                "(TechText, FolderFloat) and re-implemented natively for Tkinter.",
                     font=theme.font(11), text_color=theme.PALETTE["muted"], wraplength=800).pack(pady=(4, 0))
        ctk.CTkLabel(self, text=f"© 2026 {config.APP_AUTHOR} • MIT License", font=theme.font(12),
                     text_color=theme.PALETTE["muted"]).pack(pady=(6, 10))

    def _open_data(self) -> None:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not open_path(str(config.DATA_DIR)):
            self.app.toast.show("Could not open the data folder", "error")

    def on_show(self) -> None:
        self.header.play()
