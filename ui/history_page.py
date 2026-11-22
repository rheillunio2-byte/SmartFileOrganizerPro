import csv
from tkinter import filedialog, messagebox

import customtkinter as ctk

from utils import history_manager
from utils.file_types import CATEGORIES, CATEGORY_COLORS

from . import theme
from .anim import Tween
from .widgets import PageHeader, button, card, elide

MAX_CARDS = 60


class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.app = app
        self._debounce = None
        self._tweens: list[Tween] = []

        self.header = PageHeader(self, "History", "Every run is recorded — search it, export it, or undo the latest one")
        self.header.pack(fill="x", padx=32, pady=(28, 14))

        bar = card(self)
        bar.pack(fill="x", padx=32, pady=(0, 12))
        self.search_entry = ctk.CTkEntry(bar, placeholder_text="Search folder, date or category…", height=40,
                                         corner_radius=10, border_width=1, border_color=theme.PALETTE["border"],
                                         fg_color=theme.PALETTE["surface2"], font=theme.font(14))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=12)
        self.search_entry.bind("<KeyRelease>", self._on_key)
        button(bar, "Refresh", self.refresh_history, kind="secondary", width=96, height=40).pack(side="left", padx=4)
        button(bar, "Export CSV", self.export_csv, kind="secondary", width=110, height=40).pack(side="left", padx=4)
        button(bar, "Clear", self.clear_history, kind="danger", width=84, height=40).pack(side="left", padx=(4, 14))

        self.list = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0,
                                           scrollbar_button_color=theme.PALETTE["border"])
        self.list.pack(fill="both", expand=True, padx=26, pady=(0, 20))
        self.load_history()

    def on_show(self) -> None:
        self.header.play()
        self.load_history()

    # ------------------------------------------------------------------ data
    def _on_key(self, _event=None) -> None:
        if self._debounce:
            self.after_cancel(self._debounce)
        self._debounce = self.after(180, self.search_history)

    def load_history(self) -> None:
        self._render(history_manager.search(self.search_entry.get()))

    search_history = load_history

    def refresh_history(self) -> None:
        self.search_entry.delete(0, "end")
        self.load_history()
        self.app.toast.show("History refreshed", "info")

    def _render(self, entries: list) -> None:
        for tween in self._tweens:
            tween.cancel()
        self._tweens.clear()
        for child in self.list.winfo_children():
            child.destroy()
        if not entries:
            msg = "No matching records found." if self.search_entry.get().strip() else \
                "No history yet — organize a folder and it will show up here."
            ctk.CTkLabel(self.list, text=msg, font=theme.font(14), text_color=theme.PALETTE["muted"]).pack(pady=50)
            return
        undoable = history_manager.last_undoable()
        undoable_id = undoable["id"] if undoable else None
        for index, entry in enumerate(entries[:MAX_CARDS]):
            self._entry_card(entry, index, entry.get("id") == undoable_id)
        if len(entries) > MAX_CARDS:
            ctk.CTkLabel(self.list, text=f"Showing the newest {MAX_CARDS} of {len(entries)} records. Use search to narrow down.",
                         font=theme.font(12), text_color=theme.PALETTE["muted"]).pack(pady=12)

    def _entry_card(self, entry: dict, index: int, can_undo: bool) -> None:
        box = card(self.list, corner_radius=14)
        box.pack(fill="x", padx=6, pady=6)
        top = ctk.CTkFrame(box, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(top, text=entry.get("timestamp", ""), font=theme.font(14, "bold"),
                     text_color=theme.PALETTE["text"]).pack(side="left")
        if entry.get("undone"):
            ctk.CTkLabel(top, text="UNDONE", font=theme.font(11, "bold"), text_color=theme.PALETTE["muted"],
                         fg_color=theme.PALETTE["surface2"], corner_radius=6, width=64, height=22).pack(side="left", padx=10)
        total = entry.get("stats", {}).get("Total", 0)
        ctk.CTkLabel(top, text=f"{total:,} files", font=theme.font(14, "bold"),
                     text_color=theme.PALETTE["accent"]).pack(side="right")
        if can_undo:
            button(top, "Undo", self.app.organize_page.undo_last, kind="secondary", width=64, height=26,
                   font=theme.font(12, "bold")).pack(side="right", padx=12)
        ctk.CTkLabel(box, text=elide(entry.get("folder", ""), 90), font=theme.font(13),
                     text_color=theme.PALETTE["muted"], anchor="w").pack(fill="x", padx=18, pady=(2, 8))
        chips = ctk.CTkFrame(box, fg_color="transparent")
        chips.pack(fill="x", padx=14, pady=(0, 14))
        for key in CATEGORIES:
            n = entry.get("stats", {}).get(key, 0)
            if n:
                ctk.CTkLabel(chips, text=f" {key}  {n} ", font=theme.font(12, "bold"), corner_radius=8,
                             text_color=theme.PALETTE["text"],
                             fg_color=(theme.mix("#ffffff", CATEGORY_COLORS[key], 0.25),
                                       theme.mix("#131722", CATEGORY_COLORS[key], 0.28)),
                             height=26).pack(side="left", padx=4)
        # fade/slide-in, staggered
        self._tweens.append(Tween(box, 320, lambda t, b=box: b.configure(
            border_color=theme.mix(theme.c("bg"), theme.c("border"), t)), delay=min(index, 12) * 45,
            done=lambda b=box: b.configure(border_color=theme.PALETTE["border"])))

    # ------------------------------------------------------------------ actions
    def export_csv(self) -> None:
        entries = history_manager.load_history()
        if not entries:
            messagebox.showinfo("Export", "There is no history to export yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile="organizer_history.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.writer(fh)
                writer.writerow(["Date", "Folder", *CATEGORIES, "Total", "Undone"])
                for e in entries:
                    s = e.get("stats", {})
                    writer.writerow([e.get("timestamp", ""), e.get("folder", ""), *[s.get(c, 0) for c in CATEGORIES],
                                     s.get("Total", 0), "yes" if e.get("undone") else "no"])
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        self.app.toast.show("History exported", "success")

    def clear_history(self) -> None:
        if not messagebox.askyesno("Clear History", "Delete all history? Undo will no longer be possible."):
            return
        history_manager.clear_history()
        self.load_history()
        self.app.after_history_change(None)
        self.app.toast.show("History cleared", "info")
