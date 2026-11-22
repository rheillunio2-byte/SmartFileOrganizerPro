import customtkinter as ctk

from utils import settings_manager

from . import anim, theme
from .cursor_fx import CursorFX
from .widgets import PageHeader, button, card


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.app = app
        self.switches: dict[str, ctk.CTkSwitch] = {}

        self.header = PageHeader(self, "Settings", "Changes are saved automatically")
        self.header.pack(fill="x", padx=32, pady=(28, 14))

        box = card(self)
        box.pack(fill="x", padx=32, pady=(0, 16))

        self._section(box, "Appearance")
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(4, 10))
        ctk.CTkLabel(row, text="Theme mode", font=theme.font(14), text_color=theme.PALETTE["text"]).pack(side="left")
        self.mode = ctk.CTkSegmentedButton(row, values=["Dark", "Light", "System"], command=self._on_mode,
                                           selected_color=theme.PALETTE["accent"],
                                           selected_hover_color=theme.PALETTE["accent_hover"],
                                           unselected_color=theme.PALETTE["surface2"], font=theme.font(13, "bold"))
        self.mode.set(settings_manager.get("appearance"))
        self.mode.pack(side="right")

        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(4, 4))
        ctk.CTkLabel(row, text="Accent colour", font=theme.font(14), text_color=theme.PALETTE["text"]).pack(side="left")
        self.swatches: dict[str, ctk.CTkButton] = {}
        for name, values in theme.ACCENTS.items():
            sw = ctk.CTkButton(row, text="", width=30, height=30, corner_radius=15, fg_color=values[1],
                               hover_color=values[0], border_width=0, command=lambda n=name: self._on_accent(n))
            sw.pack(side="right", padx=4)
            self.swatches[name] = sw
        self._mark_accent()
        self.accent_note = ctk.CTkLabel(box, text="", font=theme.font(12), text_color=theme.PALETTE["muted"])
        self.accent_note.pack(anchor="e", padx=26, pady=(0, 8))

        self._section(box, "Behaviour")
        self._switch(box, "auto_open_folder", "Open the folder when organizing finishes")
        self._switch(box, "auto_refresh_history", "Refresh history automatically after each run")
        self._switch(box, "confirm_before_organize", "Ask for confirmation before moving files")

        self._section(box, "Motion")
        self._switch(box, "animations", "Animations (page transitions, count-ups, wordmark intro)",
                     command=self._on_animations)
        label = "Animated cursor (ring, comet trail, click ripples)"
        if not CursorFX.supported():
            label += " — Windows only"
        self._switch(box, "cursor_effects", label, command=self._on_cursor,
                     enabled=CursorFX.supported())

        footer = ctk.CTkFrame(box, fg_color="transparent")
        footer.pack(fill="x", padx=22, pady=(14, 20))
        button(footer, "Reset to defaults", self.reset_settings, kind="danger", width=170).pack(side="left")

    # ------------------------------------------------------------------ builders
    def _section(self, parent, title: str) -> None:
        ctk.CTkLabel(parent, text=title.upper(), font=theme.font(12, "bold"),
                     text_color=theme.PALETTE["accent"]).pack(anchor="w", padx=22, pady=(18, 2))

    def _switch(self, parent, key: str, text: str, command=None, enabled: bool = True) -> None:
        sw = ctk.CTkSwitch(parent, text=text, progress_color=theme.PALETTE["accent"], font=theme.font(14),
                           text_color=theme.PALETTE["text"],
                           command=lambda k=key, c=command: self._on_switch(k, c))
        if settings_manager.get(key):
            sw.select()
        if not enabled:
            sw.configure(state="disabled")
        sw.pack(anchor="w", padx=22, pady=8)
        self.switches[key] = sw

    # ------------------------------------------------------------------ handlers
    def _on_switch(self, key: str, command) -> None:
        settings_manager.set_value(key, bool(self.switches[key].get()))
        if command:
            command(bool(self.switches[key].get()))

    def _on_mode(self, value: str) -> None:
        settings_manager.set_value("appearance", value)
        theme.set_mode(value)
        self.after(80, theme.notify)  # let CustomTkinter repaint first, then recolour the canvases
        self.app.toast.show(f"{value} theme applied", "info")

    def _on_accent(self, name: str) -> None:
        settings_manager.set_value("accent", name)
        self._mark_accent()
        self.accent_note.configure(text=f"{name} accent will be used the next time you start the app")
        self.app.toast.show(f"{name} accent saved — restart to apply", "info")

    def _mark_accent(self) -> None:
        current = settings_manager.get("accent")
        for name, sw in self.swatches.items():
            sw.configure(border_width=3 if name == current else 0, border_color=theme.PALETTE["text"])

    def _on_animations(self, value: bool) -> None:
        anim.ENABLED = value

    def _on_cursor(self, value: bool) -> None:
        self.app.set_cursor_effects(value)

    def reset_settings(self) -> None:
        settings_manager.reset()
        self.mode.set("Dark")
        theme.set_mode("Dark")
        self.after(80, theme.notify)
        for key, sw in self.switches.items():
            (sw.select if settings_manager.get(key) else sw.deselect)()
        anim.ENABLED = True
        self.app.set_cursor_effects(settings_manager.get("cursor_effects"))
        self._mark_accent()
        self.accent_note.configure(text="Accent resets to Indigo on next start")
        self.app.toast.show("Settings reset to defaults", "info")

    def on_show(self) -> None:
        self.header.play()
