"""Colour palette, fonts, DPI helpers and live theme-change notifications."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

# (light, dark) pairs — CustomTkinter picks the right one automatically.
PALETTE: dict[str, tuple[str, str]] = {
    "bg": ("#eef0f6", "#0a0c13"),
    "sidebar": ("#ffffff", "#0e1119"),
    "surface": ("#ffffff", "#131722"),
    "surface2": ("#f3f4fa", "#1a1f2e"),
    "border": ("#dfe2ee", "#252b3d"),
    "text": ("#12141f", "#eef0f8"),
    "muted": ("#6b7186", "#8a91a8"),
    "danger": ("#dc2626", "#ef4444"),
    "danger_hover": ("#b91c1c", "#dc2626"),
    "success": ("#16a34a", "#22c55e"),
    "accent": ("#4f46e5", "#6366f1"),
    "accent_hover": ("#4338ca", "#4f46e5"),
    "accent_soft": ("#e0e1fb", "#1e2142"),
}

ACCENTS: dict[str, tuple[str, str, str, str, str]] = {
    # name: light, dark, light-hover, dark-hover, soft(light), (soft dark derived below)
    "Indigo": ("#4f46e5", "#6366f1", "#4338ca", "#4f46e5", "#e0e1fb"),
    "Emerald": ("#059669", "#10b981", "#047857", "#059669", "#d8f5ea"),
    "Rose": ("#e11d48", "#f43f5e", "#be123c", "#e11d48", "#fde0e7"),
    "Amber": ("#d97706", "#f59e0b", "#b45309", "#d97706", "#fdecc8"),
    "Sky": ("#0284c7", "#0ea5e9", "#0369a1", "#0284c7", "#d6eefb"),
}

FONT_FAMILY = "Segoe UI"
S = 1.0  # DPI scale for raw tk canvases (CustomTkinter scales its own widgets)

_listeners: list[Callable[[], None]] = []


def init_scale(root) -> None:
    global S
    try:
        S = max(1.0, float(root.winfo_fpixels("1i")) / 96.0)
    except Exception:
        S = 1.0


def px(value: float) -> int:
    return int(round(value * S))


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def canvas_font(size: int, weight: str = "normal"):
    """Raw tk font tuple; negative size = pixels so DPI scaling stays correct."""
    return (FONT_FAMILY, -px(size), weight)


def set_accent(name: str) -> None:
    light, dark, light_h, dark_h, soft = ACCENTS.get(name, ACCENTS["Indigo"])
    PALETTE["accent"] = (light, dark)
    PALETTE["accent_hover"] = (light_h, dark_h)
    PALETTE["accent_soft"] = (soft, mix(dark, "#0e1119", 0.78))


def mode_index() -> int:
    return 1 if ctk.get_appearance_mode() == "Dark" else 0


def resolve(pair: tuple[str, str] | str) -> str:
    return pair if isinstance(pair, str) else pair[mode_index()]


def c(name: str) -> str:
    """Current-mode hex colour for raw tk widgets/canvases."""
    return resolve(PALETTE[name])


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    """Blend colour ``a`` towards ``b`` by ``t`` (0..1)."""
    t = max(0.0, min(1.0, t))
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    return "#%02x%02x%02x" % (round(ar + (br - ar) * t), round(ag + (bg - ag) * t), round(ab + (bb - ab) * t))


def on_change(callback: Callable[[], None]) -> None:
    _listeners.append(callback)


def notify() -> None:
    for callback in list(_listeners):
        try:
            callback()
        except Exception:  # a destroyed widget must never break the others
            pass


def set_mode(mode: str) -> None:
    ctk.set_appearance_mode(mode)
