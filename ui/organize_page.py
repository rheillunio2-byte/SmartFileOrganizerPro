import queue
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from utils import history_manager, organizer, settings_manager
from utils.file_types import CATEGORIES, CATEGORY_COLORS
from utils.system import open_path

from . import theme
from .folder_float import FolderFloat
from .widgets import DropZone, PageHeader, button, card


class OrganizePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.app = app
        self.selected_folder = ""
        self.counts: dict[str, int] = {}
        self.queue: queue.Queue = queue.Queue()
        self.running = False
        self._started = 0.0

        self.header = PageHeader(self, "Organize Files",
                                 "Pick a folder, choose which categories to sort, then press Organize")
        self.header.pack(fill="x", padx=32, pady=(28, 14))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=26, pady=(0, 24))
        body.grid_columnconfigure(0, weight=1, uniform="o")
        body.grid_columnconfigure(1, weight=1, uniform="o")
        body.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------- left column
        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=6)

        zone_card = card(left)
        zone_card.pack(fill="x")
        self.zone = DropZone(zone_card, self.select_folder, height=140)
        self.zone.pack(fill="x", padx=14, pady=14)

        summary = card(left)
        summary.pack(fill="x", pady=(12, 0))
        self.summary_big = ctk.CTkLabel(summary, text="0", font=theme.font(40, "bold"),
                                        text_color=theme.PALETTE["accent"], anchor="w")
        self.summary_big.pack(anchor="w", padx=20, pady=(12, 0))
        self.summary_text = ctk.CTkLabel(summary, text="No folder selected yet.", font=theme.font(13),
                                         text_color=theme.PALETTE["muted"], anchor="w", justify="left")
        self.summary_text.pack(anchor="w", padx=20, pady=(0, 6))
        self.preview_only = ctk.CTkSwitch(summary, text="Preview only (don't move any files)",
                                          progress_color=theme.PALETTE["accent"], font=theme.font(13),
                                          text_color=theme.PALETTE["text"])
        self.preview_only.pack(anchor="w", padx=20, pady=(0, 14))

        actions = ctk.CTkFrame(left, fg_color="transparent")
        actions.pack(fill="x", pady=(12, 0))
        actions.grid_columnconfigure(0, weight=3)
        actions.grid_columnconfigure(1, weight=2)
        self.organize_button = button(actions, "Organize Files", self.organize_files, height=46)
        self.organize_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.undo_button = button(actions, "Undo last run", self.undo_last, kind="secondary", height=46)
        self.undo_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.progress = ctk.CTkProgressBar(left, height=8, corner_radius=4, progress_color=theme.PALETTE["accent"],
                                           fg_color=theme.PALETTE["surface2"])
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(16, 6))
        self.status = ctk.CTkLabel(left, text="Status: waiting for a folder", font=theme.font(13),
                                   text_color=theme.PALETTE["muted"], anchor="w")
        self.status.pack(fill="x")

        # ---------------------------------------------------------------- right column
        right = card(body)
        right.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(right, text="Categories", font=theme.font(15, "bold"), text_color=theme.PALETTE["text"]).pack(
            anchor="w", padx=20, pady=(16, 0))
        ctk.CTkLabel(right, text="Hover or click the folder. Click a pill to switch a category on/off — "
                                 "drag them around, they float.", font=theme.font(12), wraplength=330,
                     justify="left", text_color=theme.PALETTE["muted"]).pack(anchor="w", padx=20, pady=(2, 0))
        items = [{"key": k, "label": k, "color": CATEGORY_COLORS[k]} for k in CATEGORIES]
        self.folder = FolderFloat(right, items, on_toggle=lambda _k, _v: self._update_summary(), height=340)
        self.folder.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self._refresh_undo_state()

    # ------------------------------------------------------------------ lifecycle
    def on_show(self) -> None:
        self.header.play()
        self.folder.replay()
        self._refresh_undo_state()

    # ------------------------------------------------------------------ folder + scan
    def select_folder(self) -> None:
        if self.running:
            return
        folder = filedialog.askdirectory(title="Choose a folder to organize")
        if folder:
            self.set_folder(folder)

    def set_folder(self, folder: str) -> None:
        self.selected_folder = folder
        self.zone.set_path(folder)
        self.rescan()
        self.status.configure(text="Status: folder ready", text_color=theme.PALETTE["muted"])
        self.progress.set(0)

    def rescan(self) -> None:
        try:
            stats = organizer.scan(self.selected_folder)
        except OSError as exc:
            messagebox.showerror("Cannot read folder", str(exc))
            return
        self.counts = {k: stats[k] for k in CATEGORIES}
        self.folder.set_counts(self.counts)
        self._update_summary()

    def _enabled_total(self) -> int:
        return sum(self.counts.get(k, 0) for k in self.folder.get_selected())

    def _update_summary(self) -> None:
        if not self.selected_folder:
            return
        total, all_total = self._enabled_total(), sum(self.counts.values())
        self.summary_big.configure(text=f"{total:,}")
        if all_total == 0:
            self.summary_text.configure(text="This folder has no loose files to organize.")
        else:
            self.summary_text.configure(
                text=f"files ready to move  ({all_total:,} found, {len(self.folder.get_selected())} "
                     f"of {len(CATEGORIES)} categories on)")

    # ------------------------------------------------------------------ organize
    def organize_files(self) -> None:
        if self.running:
            return
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        if not Path(self.selected_folder).is_dir():
            messagebox.showerror("Folder missing", "The selected folder no longer exists.")
            return
        enabled = self.folder.get_selected()
        if not enabled:
            messagebox.showwarning("Warning", "Switch on at least one category.")
            return
        self.rescan()
        total = self._enabled_total()
        if total == 0:
            self.app.toast.show("Nothing to organize in those categories", "info")
            return
        dry = bool(self.preview_only.get())
        if not dry and settings_manager.get("confirm_before_organize"):
            if not messagebox.askyesno("Organize files",
                                       f"Move {total:,} file(s) into category folders inside:\n\n{self.selected_folder}\n\n"
                                       "You can undo this afterwards."):
                return
        self._set_running(True)
        self.progress.set(0)
        self.status.configure(text="Status: " + ("scanning…" if dry else "organizing…"),
                              text_color=theme.PALETTE["muted"])
        self._started = time.perf_counter()
        folder = self.selected_folder

        def work():
            try:
                result = organizer.organize(folder, enabled, dry_run=dry,
                                            progress=lambda d, t, n: self.queue.put(("progress", d, t, n)))
                self.queue.put(("done", result, dry))
            except Exception as exc:  # reported on the UI thread
                self.queue.put(("error", str(exc)))

        threading.Thread(target=work, daemon=True).start()
        self.after(30, self._poll)

    def _poll(self) -> None:
        latest = None
        finished = None
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == "progress":
                    latest = message
                else:
                    finished = message
        except queue.Empty:
            pass
        if latest:
            _, done, total, name = latest
            self.progress.set(done / total if total else 1)
            self.status.configure(text=f"Status: {done:,}/{total:,}  •  {name}")
        if finished is None:
            self.after(30, self._poll)
            return
        self._set_running(False)
        if finished[0] == "error":
            self.progress.set(0)
            self.status.configure(text="Status: failed", text_color=theme.PALETTE["danger"])
            messagebox.showerror("Error", finished[1])
            return
        self._finish(finished[1], finished[2])

    def _finish(self, result, dry: bool) -> None:
        elapsed = time.perf_counter() - self._started
        stats = result.stats
        self.progress.set(1)
        if dry:
            self.status.configure(text=f"Status: preview — {stats['Total']:,} file(s) would be moved",
                                  text_color=theme.PALETTE["muted"])
            self.app.toast.show(f"Preview: {stats['Total']:,} files would be organized", "info")
            return
        history_manager.save_history(self.selected_folder, stats, result.moves)
        self.rescan()
        self.app.after_history_change(stats)
        note = f"  ({len(result.errors)} skipped)" if result.errors else ""
        self.status.configure(text=f"Status: completed — {stats['Total']:,} file(s) in {elapsed:.1f}s{note}",
                              text_color=theme.PALETTE["success"])
        self.app.toast.show(f"Organized {stats['Total']:,} files in {elapsed:.1f}s", "success")
        self._refresh_undo_state()
        if result.errors:
            messagebox.showwarning("Some files were skipped", "\n".join(result.errors[:12]))
        if settings_manager.get("auto_open_folder"):
            open_path(self.selected_folder)

    def _set_running(self, running: bool) -> None:
        self.running = running
        state = "disabled" if running else "normal"
        self.organize_button.configure(state=state)
        self.undo_button.configure(state="disabled" if running else self.undo_button.cget("state"))
        if not running:
            self._refresh_undo_state()

    # ------------------------------------------------------------------ undo
    def _refresh_undo_state(self) -> None:
        if not self.running:
            self.undo_button.configure(state="normal" if history_manager.last_undoable() else "disabled")

    def undo_last(self) -> None:
        entry = history_manager.last_undoable()
        if not entry or self.running:
            return
        count = len(entry["moves"])
        if not messagebox.askyesno("Undo last run",
                                   f"Move {count:,} file(s) back to where they came from?\n\n{entry['folder']}"):
            return
        restored, skipped = organizer.undo([tuple(m) for m in entry["moves"]])
        history_manager.mark_undone(entry["id"])
        if self.selected_folder and Path(self.selected_folder).is_dir():
            self.rescan()
        self.app.after_history_change(None)
        self._refresh_undo_state()
        suffix = f" ({skipped} missing)" if skipped else ""
        self.status.configure(text=f"Status: restored {restored:,} file(s){suffix}", text_color=theme.PALETTE["muted"])
        self.progress.set(0)
        self.app.toast.show(f"Restored {restored:,} files{suffix}", "info")
