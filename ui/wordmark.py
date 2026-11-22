"""TechWordmark — an interactive technical-drawing wordmark.

A native Tkinter/Pillow re-implementation of the *behaviour* of the React Bits "TechText"
component (hover turns a letter into a dashed vector outline, a selection frame glides between
letters, tiny specks blink around the active letter, letters can be dragged and spring home,
clicking kicks a letter and ripples through its neighbours, and an idle sweep runs on its own).
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

try:  # ImageTk needs a working Tk; imported lazily so tests can stub it
    from PIL import ImageTk
except Exception:  # pragma: no cover
    ImageTk = None

from . import anim, theme
from .anim import CanvasLoop, approach

FONT_CANDIDATES = ("segoeuib.ttf", "seguisb.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf",
                   "Arial Bold.ttf", "LiberationSans-Bold.ttf", "Helvetica.ttc")
SPRING = 320.0
LABEL_FONT = ("Consolas", -11)


def _load_font(size: int):
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


def _noise(*values: int) -> float:
    h = 2166136261
    for v in values:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 0x5BD1E995) & 0xFFFFFFFF
        h ^= h >> 15
    return h / 4294967296


@dataclass
class Glyph:
    char: str
    index: int
    x: float                      # home x of the image's top-left (canvas px)
    y: float
    box: tuple[int, int, int, int]  # tight ink box inside the image
    fill: object = None
    dashes: object = None
    item: int = 0
    ghost: int = 0
    off: list = field(default_factory=lambda: [0.0, 0.0])
    vel: list = field(default_factory=lambda: [0.0, 0.0])
    outline: float = 0.0
    hold: float = 0.0
    glyph_x0: float = 0.0

    def ink(self):
        return (self.x + self.box[0] + self.off[0], self.y + self.box[1] + self.off[1],
                self.x + self.box[2] + self.off[0], self.y + self.box[3] + self.off[1])


class TechWordmark(tk.Canvas, CanvasLoop):
    def __init__(self, master, text: str = "SmartFile", height: int = 190, base_size: int = 96,
                 specks: int = 14, bg_name: str = "surface", **kwargs):
        self.bg_name = bg_name
        super().__init__(master, height=theme.px(height), bg=theme.c(bg_name),
                         highlightthickness=0, bd=0, **kwargs)
        self.text, self.base_size, self.specks = text, base_size, specks
        self.glyphs: list[Glyph] = []
        self._size = 0
        self._width = 0
        self._photos: list = []
        self.pointer = [0.0, 0.0]
        self.inside = False
        self.dragging = -1
        self._grab = (0.0, 0.0)
        self._press = (0.0, 0.0, 0.0, -1)
        self._clock = 0.0
        self._pulse = 0.0
        self._intro = 0.0
        self._kicks: list[list] = []
        self._frame = [0.0, 0.0, 0.0, 0.0]
        self._frame_alpha = 0.0
        self._focus = -1
        self._frame_items: dict = {}
        self._speck_items: list[int] = []
        self._cursor = ""
        self._loop_init()
        self.bind("<Configure>", self._on_configure)
        self.bind("<Motion>", self._on_move)
        self.bind("<Enter>", self._on_move)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_down)
        self.bind("<ButtonRelease-1>", self._on_up)
        self.bind("<Destroy>", lambda _e: self.stop_loop(), add="+")
        theme.on_change(self.refresh_colors)
        self.start_loop()

    # ------------------------------------------------------------------ build
    def replay(self) -> None:
        """Play the entrance again (called when the page is shown)."""
        self._intro = 0.0
        for g in self.glyphs:
            g.off[:] = [0.0, 60.0]
            g.vel[:] = [0.0, 0.0]
            g.outline = 0.0
            g.hold = 0.12 + g.index * 0.07

    def refresh_colors(self) -> None:
        self.configure(bg=theme.c(self.bg_name))
        self._build(force=True)

    def _on_configure(self, event) -> None:
        if abs(event.width - self._width) > 2:
            self._width = event.width
            self._build()

    def _build(self, force: bool = False) -> None:
        width, height = self.winfo_width(), self.winfo_height()
        if width < 50 or height < 50:
            return
        font = _load_font(self.base_size)
        total = font.getlength(self.text)
        size = self.base_size * min(1.0, width * 0.9 / max(total, 1), height * 0.62 / self.base_size)
        size = max(24, int(size))
        if not force and self.glyphs and abs(size - self._size) < 3:
            self._layout(width, height)
            return
        self._size = size
        self.delete("all")
        self._photos.clear()
        self.glyphs.clear()
        font = _load_font(size)
        ascent, descent = font.getmetrics()
        pad = 6
        ink, accent = theme.c("text"), theme.c("accent")
        for i, ch in enumerate(self.text):
            if not ch.strip():
                continue
            w = int(math.ceil(font.getlength(ch))) + pad * 2
            h = ascent + descent + pad * 2
            mask = Image.new("L", (w, h), 0)
            ImageDraw.Draw(mask).text((pad, pad), ch, font=font, fill=255)
            box = mask.getbbox() or (0, 0, w, h)
            glyph = Glyph(ch, i, 0, 0, box)
            glyph.fill = self._photo(self._colorize(mask, ink))
            glyph.dashes = self._photo(self._colorize(self._dash(mask), accent))
            glyph.hold = 0.12 + len(self.glyphs) * 0.07
            glyph.off[:] = [0.0, 60.0]
            glyph.glyph_x0 = font.getlength(self.text[:i])
            self.glyphs.append(glyph)
        for g in self.glyphs:
            g.ghost = self.create_image(0, 0, image=g.dashes, anchor="nw", state="hidden")
        for g in self.glyphs:
            g.item = self.create_image(0, 0, image=g.fill, anchor="nw", state="hidden")
        self._frame_items = {
            "rect": self.create_rectangle(0, 0, 0, 0, outline=accent, state="hidden"),
            "corners": [self.create_rectangle(0, 0, 0, 0, fill=accent, outline="", state="hidden") for _ in range(4)],
            "label": self.create_text(0, 0, text="", anchor="sw", fill=accent, font=LABEL_FONT, state="hidden"),
        }
        self._speck_items = [self.create_rectangle(0, 0, 0, 0, fill=accent, outline=accent, state="hidden")
                             for _ in range(self.specks)]
        self._total = font.getlength(self.text)
        self._pad = pad
        self._layout(width, height)

    def _layout(self, width: int, height: int) -> None:
        if not self.glyphs:
            return
        origin = (width - self._total) / 2
        top = (height - (self.glyphs[0].fill.height() if hasattr(self.glyphs[0].fill, "height") else height * 0.6)) / 2
        for g in self.glyphs:
            g.x = origin + g.glyph_x0 - self._pad
            g.y = top

    def _photo(self, image: Image.Image):
        if ImageTk is None:
            return _FakePhoto(image)
        photo = ImageTk.PhotoImage(image, master=self)
        self._photos.append(photo)
        return photo

    @staticmethod
    def _colorize(mask: Image.Image, color: str) -> Image.Image:
        r, g, b = theme.hex_to_rgb(color)
        img = Image.new("RGBA", mask.size, (r, g, b, 0))
        img.putalpha(mask)
        return img

    @staticmethod
    def _dash(mask: Image.Image) -> Image.Image:
        """Dashed vector-style silhouette outline of a letter mask."""
        edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(5)))
        out = Image.new("L", mask.size, 0)
        src, dst = edge.load(), out.load()
        w, h = mask.size
        for y in range(h):
            for x in range(w):
                v = src[x, y]
                if v and ((x + y) // 5) % 3 != 2:
                    dst[x, y] = v
        return out

    # ------------------------------------------------------------------ input
    def _on_move(self, event) -> None:
        self.pointer[:] = [event.x, event.y]
        self.inside = True

    def _on_leave(self, _event) -> None:
        if self.dragging < 0:
            self.inside = False

    def _glyph_at(self, x: float, y: float) -> int:
        best, best_d = -1, 1e9
        for i, g in enumerate(self.glyphs):
            x1, y1, x2, y2 = g.ink()
            if y < y1 - 30 or y > y2 + 30:
                continue
            d = x1 - x if x < x1 else x - x2 if x > x2 else 0
            if d < best_d:
                best, best_d = i, d
        return best if best_d < 24 else -1

    def _on_down(self, event) -> None:
        self.pointer[:] = [event.x, event.y]
        i = self._glyph_at(event.x, event.y)
        self._press = (event.x, event.y, time.perf_counter(), i)
        if i >= 0:
            g = self.glyphs[i]
            self.dragging = i
            self._grab = (event.x - g.off[0], event.y - g.off[1])

    def _on_up(self, event) -> None:
        px, py, t0, i = self._press
        self.dragging = -1
        if i >= 0 and time.perf_counter() - t0 < 0.45 and math.hypot(event.x - px, event.y - py) < 6:
            self._kick(i)
        self._press = (0, 0, 0, -1)

    def _kick(self, index: int) -> None:
        strength = self._size * 11
        self._kicks.append([self._pulse, index, strength])
        for d in range(1, len(self.glyphs)):
            v = strength * 0.62 ** d
            if v < 30:
                break
            for j in (index - d, index + d):
                if 0 <= j < len(self.glyphs):
                    self._kicks.append([self._pulse + d * 0.055, j, v])

    # ------------------------------------------------------------------ frame step
    def step(self, dt: float) -> None:
        if not self.glyphs:
            return
        self._pulse += dt
        self._intro += dt
        accent = theme.c("accent")
        bg = theme.c(self.bg_name)
        damping = 2 * math.sqrt(SPRING) * (1 - 0.4 * 0.96)

        for k in self._kicks[:]:
            if k[0] <= self._pulse:
                self.glyphs[k[1]].vel[1] -= k[2]
                self._kicks.remove(k)

        sweeping = anim.ENABLED and not self.inside and self.dragging < 0
        if sweeping:
            self._clock += dt
        for i, g in enumerate(self.glyphs):
            if self._intro < g.hold:
                continue
            if i == self.dragging:
                g.off[0] = approach(g.off[0], self.pointer[0] - self._grab[0], dt, 0.03)
                g.off[1] = approach(g.off[1], self.pointer[1] - self._grab[1], dt, 0.03)
                g.vel[:] = [0.0, 0.0]
                continue
            for a in (0, 1):
                g.vel[a] += (-SPRING * g.off[a] - damping * g.vel[a]) * dt
                g.off[a] += g.vel[a] * dt
            if abs(g.off[0]) < 0.05 and abs(g.off[1]) < 0.05 and abs(g.vel[0]) + abs(g.vel[1]) < 0.5:
                g.off[:] = [0.0, 0.0]
                g.vel[:] = [0.0, 0.0]

        # which letter is active: dragged > hovered > idle sweep
        if self.dragging >= 0:
            focus = self.dragging
        elif self.inside:
            focus = self._glyph_at(*self.pointer)
        elif sweeping and self._intro > 1.4:
            pos = (len(self.glyphs) - 1) * (0.5 - 0.5 * math.cos(self._clock * 0.45))
            focus = int(round(pos))
        else:
            focus = -1
        self._focus = focus

        cursor = "fleur" if self.dragging >= 0 else "hand2" if (self.inside and focus >= 0) else ""
        if cursor != self._cursor:
            self._cursor = cursor
            self.configure(cursor=cursor)

        # selection frame target
        if focus >= 0:
            x1, y1, x2, y2 = self.glyphs[focus].ink()
            target = [x1 - 7, y1 - 7, x2 + 7, y2 + 7]
            if self._frame_alpha < 0.03:
                self._frame[:] = target
            glide = 0.02 if focus == self.dragging else 0.08
            for a in range(4):
                self._frame[a] = approach(self._frame[a], target[a], dt, glide)
        self._frame_alpha = approach(self._frame_alpha, 1.0 if focus >= 0 else 0.0, dt, 0.1)

        for i, g in enumerate(self.glyphs):
            shown = self._intro >= g.hold
            g.outline = approach(g.outline, 1.0 if (i == focus and i != self.dragging) else 0.0, dt, 0.09)
            self.itemconfigure(g.item, state="normal" if shown else "hidden",
                               image=g.dashes if g.outline > 0.5 else g.fill)
            self.coords(g.item, g.x + g.off[0], g.y + g.off[1])
            moved = math.hypot(*g.off) > 1.5
            self.itemconfigure(g.ghost, state="normal" if (moved and shown) else "hidden")
            if moved:
                self.coords(g.ghost, g.x, g.y)

        self._draw_frame(focus, accent, bg)

    def _draw_frame(self, focus: int, accent: str, bg: str) -> None:
        items = self._frame_items
        a = self._frame_alpha
        if a < 0.03 or focus < 0:
            for key in ("rect", "label"):
                self.itemconfigure(items[key], state="hidden")
            for c in items["corners"]:
                self.itemconfigure(c, state="hidden")
            for s in self._speck_items:
                self.itemconfigure(s, state="hidden")
            return
        x1, y1, x2, y2 = (round(v) + 0.5 for v in self._frame)
        line = theme.mix(bg, accent, 0.5 * a)
        self.itemconfigure(items["rect"], state="normal", outline=line)
        self.coords(items["rect"], x1, y1, x2, y2)
        corner = theme.mix(bg, accent, 0.95 * a)
        for c, (cx, cy) in zip(items["corners"], ((x1, y1), (x2, y1), (x2, y2), (x1, y2))):
            self.itemconfigure(c, state="normal", fill=corner)
            self.coords(c, cx - 2, cy - 2, cx + 3, cy + 3)
        g = self.glyphs[focus]
        moved = math.hypot(*g.off) > 1
        if moved:
            label = f"{g.off[0]:+.0f}, {-g.off[1]:+.0f}"
        else:
            bx = g.box
            label = f"{g.char}  {bx[2] - bx[0]} × {bx[3] - bx[1]}"
        self.itemconfigure(items["label"], state="normal", text=label, fill=theme.mix(bg, accent, 0.62 * a))
        self.coords(items["label"], x1, y1 - 6)
        self._draw_specks(focus, a, accent, bg)

    def _draw_specks(self, focus: int, a: float, accent: str, bg: str) -> None:
        x1, y1, x2, y2 = self._frame
        w, h = x2 - x1, y2 - y1
        perimeter = 2 * (w + h)
        if perimeter < 8:
            return
        for k, item in enumerate(self._speck_items):
            period = 0.5 + _noise(focus, k, 11) * 1.2
            t = self._pulse / period + _noise(focus, k, 17)
            cycle, life = math.floor(t), t - math.floor(t)
            if life > 0.7:
                self.itemconfigure(item, state="hidden")
                continue
            d = _noise(focus, k, cycle) * perimeter
            if d < w:
                px, py, nx, ny = x1 + d, y1, 0, -1
            elif d < w + h:
                px, py, nx, ny = x2, y1 + d - w, 1, 0
            elif d < 2 * w + h:
                px, py, nx, ny = x2 - (d - w - h), y2, 0, 1
            else:
                px, py, nx, ny = x1, y2 - (d - 2 * w - h), -1, 0
            pick = _noise(focus, k, cycle, 2)
            size = 2 if pick < 0.46 else 3 if pick < 0.7 else 5 if pick < 0.88 else 8
            out = 4 + int(_noise(focus, k, cycle, 1) * 5) * 3
            x, y = round(px + nx * out), round(py + ny * out)
            tone = _noise(focus, k, cycle, 3)
            blink = 0.35 if (life < 0.06 or 0.32 < life < 0.36) else 1.0
            color = theme.mix(bg, accent, a * (0.3 + 0.6 * tone) * blink)
            hollow = tone < 0.26 or (size >= 8 and tone < 0.78)
            self.itemconfigure(item, state="normal", outline=color, fill="" if hollow else color)
            self.coords(item, x - size // 2, y - size // 2, x + size // 2 + 1, y + size // 2 + 1)


class _FakePhoto:  # used only when Tk imaging is unavailable (headless tests)
    def __init__(self, image):
        self._image = image

    def width(self):
        return self._image.width

    def height(self):
        return self._image.height
