"""FolderFloat — a folder that releases floating, draggable category pills.

A native Tkinter re-implementation of the *behaviour* of the React Bits "FolderFloat" component
(the flap tilts open, pills spring out one by one from behind it, then a zero-gravity world takes
over: they drift, collide, can be dragged and thrown). Here the pills are functional: clicking one
toggles whether that category will be organised.
"""

from __future__ import annotations

import math
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass, field

from . import theme
from .anim import CanvasLoop, approach, clamp, ease_out_cubic

PILL_H = 34
GAP = 12
ROW = 52
LIFT = 26


def rounded(x1, y1, x2, y2, r):
    r = max(0.0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
            x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1, x1 + r, y1]


@dataclass
class Pill:
    key: str
    label: str
    color: str
    w: float = 100.0
    h: float = PILL_H
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    tx: float = 0.0
    ty: float = 0.0
    scale: float = 0.5
    mode: str = "hidden"   # hidden | rise | free | return
    delay: float = 0.0
    phase: float = 0.0
    pop: float = 0.0
    items: tuple = field(default_factory=tuple)


class FolderFloat(tk.Canvas, CanvasLoop):
    def __init__(self, master, items: list[dict], on_toggle=None, title: str = "Categories",
                 height: int = 300, bg_name: str = "surface", spread: int = 230, drift: float = 0.5, **kwargs):
        self.bg_name = bg_name
        super().__init__(master, height=theme.px(height), bg=theme.c(bg_name), highlightthickness=0, bd=0, **kwargs)
        self.title, self.on_toggle, self.spread, self.drift = title, on_toggle, spread, drift
        self.pills = [Pill(i["key"], i["label"], i["color"], phase=(n * 2.399) % (2 * math.pi))
                      for n, i in enumerate(items)]
        self.selected = {p.key for p in self.pills}
        self.counts: dict[str, int] = {}
        self.open = True
        self.open_p = 0.0
        self.t_open = 0.0
        self.clock = 0.0
        self.hover = -1
        self.pointer = [0.0, 0.0]
        self.inside = False
        self._drag: dict | None = None
        self._geo: dict = {}
        self._static: dict = {}
        self._font = tkfont.Font(root=self, family=theme.FONT_FAMILY, size=-theme.px(13), weight="bold")
        self._loop_init()
        self.bind("<Configure>", lambda e: self._build(e.width, e.height))
        self.bind("<Motion>", self._on_move)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_down)
        self.bind("<ButtonRelease-1>", self._on_up)
        self.bind("<Destroy>", lambda _e: self.stop_loop(), add="+")
        theme.on_change(self.refresh_colors)
        self.start_loop()

    # ------------------------------------------------------------------ public API
    def set_counts(self, counts: dict[str, int]) -> None:
        self.counts = dict(counts)
        self._measure()
        self._layout_targets()
        self._update_sublabel()

    def set_selected(self, keys) -> None:
        self.selected = set(keys)
        self._update_sublabel()

    def get_selected(self) -> list[str]:
        return [p.key for p in self.pills if p.key in self.selected]

    def replay(self) -> None:
        """Close instantly and spring the pills out again."""
        self.open = True
        self.open_p = 0.0
        self.t_open = self.clock
        for n, p in enumerate(self.pills):
            p.mode, p.scale, p.delay = "rise", 0.5, 0.06 + n * 0.045
            p.vx = p.vy = 0.0
            self._to_mouth(p)

    def refresh_colors(self) -> None:
        self.configure(bg=theme.c(self.bg_name))
        self._build(self.winfo_width(), self.winfo_height(), keep_state=True)

    # ------------------------------------------------------------------ geometry
    def _measure(self) -> None:
        for p in self.pills:
            n = self.counts.get(p.key)
            p.w = self._font.measure(p.label + (f"   {n}" if n is not None else "")) + theme.px(44)
            p.h = theme.px(PILL_H)

    def _build(self, width: int, height: int, keep_state: bool = False) -> None:
        if width < 80 or height < 80:
            return
        S = theme.S
        keep_state = keep_state or bool(self._geo)  # only the very first build plays the entrance
        fw, fh = 210 * S, 118 * S
        fx, fy = width / 2 - fw / 2, height - fh - 14 * S
        self._geo = {"W": width, "H": height, "fx": fx, "fy": fy, "fw": fw, "fh": fh}
        self._measure()
        self.delete("all")
        bg, ink = theme.c(self.bg_name), theme.c("text")
        back_c = theme.mix(theme.c("surface2"), ink, 0.10)
        front_c = theme.mix(theme.c("surface2"), ink, 0.20)
        r = 14 * S
        tab = rounded(fx, fy - 14 * S, fx + fw * 0.42, fy + 30 * S, r)
        self._static["back"] = self.create_polygon(rounded(fx, fy, fx + fw, fy + fh, r), smooth=True, fill=back_c, outline="")
        self._static["tab"] = self.create_polygon(tab, smooth=True, fill=back_c, outline="")
        self._static["paper"] = self.create_polygon(rounded(0, 0, 1, 1, 1), smooth=True, fill=theme.mix(bg, "#ffffff", 0.85),
                                                    outline="")
        for p in self.pills:  # pills sit between paper and front => they emerge from behind the flap
            p.items = (
                self.create_polygon(rounded(0, 0, 1, 1, 1), smooth=True, fill="", outline="", width=1.5, state="hidden"),
                self.create_oval(0, 0, 0, 0, fill="", outline="", state="hidden"),
                self.create_text(0, 0, text="", anchor="w", font=self._font_tuple(), state="hidden"),
                self.create_text(0, 0, text="", anchor="e", font=self._font_tuple(), state="hidden"),
            )
        self._static["front"] = self.create_polygon(rounded(0, 0, 1, 1, 1), smooth=True, fill=front_c, outline="")
        self._static["shine"] = self.create_line(0, 0, 0, 0, fill=theme.mix(front_c, "#ffffff", 0.18), width=1)
        self._static["title"] = self.create_text(fx + 18 * S, fy + fh - 40 * S, anchor="w", text=self.title,
                                                 fill=ink, font=theme.canvas_font(14, "bold"))
        self._static["sub"] = self.create_text(fx + 18 * S, fy + fh - 20 * S, anchor="w", text="",
                                               fill=theme.c("muted"), font=theme.canvas_font(11))
        self._update_sublabel()
        self._layout_targets()
        if not keep_state:
            for p in self.pills:
                self._to_mouth(p)
            self.replay()
        self._draw_folder()

    def _mouth(self):
        g = self._geo
        return g["fx"] + g["fw"] / 2, g["fy"] + 22 * theme.S

    def _to_mouth(self, p: Pill) -> None:
        p.x, p.y = self._mouth()

    def _zone(self):
        g, S = self._geo, theme.S
        spread = min(self.spread * S, g["W"] / 2 - 14 * S)
        return (g["W"] / 2 - spread - 8 * S, 8 * S, g["W"] / 2 + spread + 8 * S, g["fy"] - 4 * S), spread

    def _layout_targets(self) -> None:
        if not self._geo:
            return
        S = theme.S
        (zl, zt, zr, zb), spread = self._zone()
        rows, row, width = [], [], 0.0
        for p in self.pills:
            if row and width + GAP * S + p.w > spread * 2:
                rows.append((row, width))
                row, width = [], 0.0
            row.append(p)
            width += (GAP * S if len(row) > 1 else 0) + p.w
        if row:
            rows.append((row, width))
        base = self._geo["fy"] - LIFT * S - PILL_H * S / 2
        for ri, (members, total) in enumerate(rows):
            x = self._geo["W"] / 2 - total / 2
            shift = (1 if ri % 2 else -1) * min(16 * S, spread * 0.1)
            for p in members:
                j = (math.sin(self.pills.index(p) * 12.9898 + 4.14) * 43758.5453) % 1
                p.tx = x + p.w / 2 + shift + (j - 0.5) * 6 * S
                p.ty = max(zt + PILL_H * S, base - ri * ROW * S - j * 6 * S)
                x += p.w + GAP * S

    def _font_tuple(self):
        return theme.canvas_font(13, "bold")

    def _update_sublabel(self) -> None:
        if "sub" in self._static:
            self.itemconfigure(self._static["sub"], text=f"{len(self.selected)} of {len(self.pills)} categories active")

    # ------------------------------------------------------------------ input
    def _pill_at(self, x: float, y: float) -> int:
        for i in range(len(self.pills) - 1, -1, -1):
            p = self.pills[i]
            if p.mode in ("hidden",) or p.scale < 0.8:
                continue
            if abs(x - p.x) <= p.w / 2 and abs(y - p.y) <= p.h / 2:
                return i
        return -1

    def _on_move(self, event) -> None:
        self.pointer[:] = [event.x, event.y]
        self.inside = True
        d = self._drag
        if d is not None and not d["moved"] and math.hypot(event.x - d["sx"], event.y - d["sy"]) >= 4:
            d["moved"] = True
        if d is None:
            self.hover = self._pill_at(event.x, event.y)
            over_folder = self._over_folder(event.x, event.y)
            self.configure(cursor="hand2" if (self.hover >= 0 or over_folder) else "")

    def _on_leave(self, _event) -> None:
        if self._drag is None:
            self.inside = False
            self.hover = -1

    def _over_folder(self, x: float, y: float) -> bool:
        g = self._geo
        return bool(g) and g["fx"] <= x <= g["fx"] + g["fw"] and g["fy"] + 22 * theme.S <= y <= g["fy"] + g["fh"]

    def _on_down(self, event) -> None:
        i = self._pill_at(event.x, event.y)
        if i >= 0 and self.pills[i].mode == "free":
            p = self.pills[i]
            self._drag = {"i": i, "dx": p.x - event.x, "dy": p.y - event.y, "sx": event.x, "sy": event.y,
                          "moved": False, "last": (event.x, event.y), "v": (0.0, 0.0)}
        elif i >= 0:
            self._drag = {"i": i, "moved": False, "sx": event.x, "sy": event.y, "toggle_only": True}
        elif self._over_folder(event.x, event.y):
            self._set_open(not self.open)

    def _on_up(self, _event) -> None:
        d, self._drag = self._drag, None
        if not d:
            return
        p = self.pills[d["i"]]
        if not d["moved"]:
            self._toggle(p)
        elif not d.get("toggle_only"):
            p.vx, p.vy = d["v"]

    def _toggle(self, p: Pill) -> None:
        if p.key in self.selected:
            self.selected.discard(p.key)
        else:
            self.selected.add(p.key)
        p.pop = 1.0
        self._update_sublabel()
        if self.on_toggle:
            self.on_toggle(p.key, p.key in self.selected)

    def _set_open(self, value: bool) -> None:
        if value == self.open:
            return
        self.open = value
        self.t_open = self.clock
        for n, p in enumerate(self.pills):
            p.mode = "rise" if value else "return"
            p.delay = (0.06 + n * 0.045) if value else (len(self.pills) - n) * 0.02

    # ------------------------------------------------------------------ simulation
    def step(self, dt: float) -> None:
        if not self._geo:
            return
        self.clock += dt
        since = self.clock - self.t_open
        self.open_p = approach(self.open_p, 1.0 if self.open else 0.0, dt, 0.12)
        (zl, zt, zr, zb), _ = self._zone()
        S = theme.S
        mouth = self._mouth()
        damping = 2 * math.sqrt(180) * (1 - 0.3 * 0.96)

        for i, p in enumerate(self.pills):
            if self._drag and self._drag["i"] == i and self._drag["moved"] and p.mode == "free":
                d = self._drag
                nx = min(zr - p.w / 2, max(zl + p.w / 2, self.pointer[0] + d["dx"]))
                ny = min(zb - p.h / 2, max(zt + p.h / 2, self.pointer[1] + d["dy"]))
                d["v"] = ((nx - p.x) / max(dt, 1e-3) * 0.5, (ny - p.y) / max(dt, 1e-3) * 0.5)
                p.x, p.y, p.vx, p.vy = nx, ny, 0.0, 0.0
                continue
            if p.mode == "rise":
                if since < p.delay:
                    continue
                p.vx += (180 * (p.tx - p.x) - damping * p.vx) * dt
                p.vy += (180 * (p.ty - p.y) - damping * p.vy) * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.scale = approach(p.scale, 1.0, dt, 0.09)
                if since > p.delay + 0.7 and math.hypot(p.tx - p.x, p.ty - p.y) < 8 * S:
                    p.mode = "free"
            elif p.mode == "free":
                t = self.clock
                k = self.drift * 55 * S * min(1.0, since / 2)
                p.vx += math.sin(t * 0.9 + p.phase) * k * dt
                p.vy += math.cos(t * 1.3 + p.phase * 1.7) * k * dt
                damp = math.exp(-1.1 * dt)
                p.vx *= damp
                p.vy *= damp
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.scale = approach(p.scale, 1.06 if i == self.hover else 1.0, dt, 0.06)
            elif p.mode == "return":
                if since < p.delay:
                    continue
                p.vx += (260 * (mouth[0] - p.x) - 30 * p.vx) * dt
                p.vy += (260 * (mouth[1] - p.y) - 30 * p.vy) * dt
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.scale = approach(p.scale, 0.5, dt, 0.1)
                if math.hypot(mouth[0] - p.x, mouth[1] - p.y) < 6 * S:
                    p.mode = "hidden"
            p.pop = approach(p.pop, 0.0, dt, 0.12)

        self._collide(zl, zt, zr, zb)
        self._draw_folder()
        self._draw_pills()

    def _collide(self, zl, zt, zr, zb) -> None:
        free = [(i, p) for i, p in enumerate(self.pills) if p.mode == "free"]
        dragged = self._drag["i"] if self._drag and self._drag["moved"] else -1
        for _, p in free:  # walls
            hw, hh = p.w / 2, p.h / 2
            if p.x - hw < zl:
                p.x, p.vx = zl + hw, abs(p.vx) * 0.55
            elif p.x + hw > zr:
                p.x, p.vx = zr - hw, -abs(p.vx) * 0.55
            if p.y - hh < zt:
                p.y, p.vy = zt + hh, abs(p.vy) * 0.55
            elif p.y + hh > zb:
                p.y, p.vy = zb - hh, -abs(p.vy) * 0.55
        for a in range(len(free)):
            for b in range(a + 1, len(free)):
                (ia, pa), (ib, pb) = free[a], free[b]
                dx, dy = pb.x - pa.x, pb.y - pa.y
                ox = (pa.w + pb.w) / 2 + 4 - abs(dx)
                oy = (pa.h + pb.h) / 2 + 4 - abs(dy)
                if ox <= 0 or oy <= 0:
                    continue
                wa = 0.0 if ia == dragged else (1.0 if ib != dragged else 2.0)
                wb = 0.0 if ib == dragged else (1.0 if ia != dragged else 2.0)
                total = (wa + wb) or 1.0
                if ox < oy:
                    s = 1 if dx >= 0 else -1
                    pa.x -= s * ox * wa / total
                    pb.x += s * ox * wb / total
                    pa.vx, pb.vx = -abs(pa.vx) * 0.55 * s if wa else pa.vx, abs(pb.vx) * 0.55 * s if wb else pb.vx
                else:
                    s = 1 if dy >= 0 else -1
                    pa.y -= s * oy * wa / total
                    pb.y += s * oy * wb / total
                    pa.vy, pb.vy = -abs(pa.vy) * 0.55 * s if wa else pa.vy, abs(pb.vy) * 0.55 * s if wb else pb.vy

    # ------------------------------------------------------------------ drawing
    def _draw_folder(self) -> None:
        g, S = self._geo, theme.S
        if not g or "paper" not in self._static:
            return
        o = ease_out_cubic(clamp(self.open_p))
        fx, fy, fw, fh = g["fx"], g["fy"], g["fw"], g["fh"]
        r = 14 * S
        # paper edge rises as the flap opens
        top = fy + 20 * S - 26 * S * o
        self.coords(self._static["paper"], *rounded(fx + fw * 0.08, top, fx + fw * 0.92, fy + fh * 0.7, 6 * S))
        self.itemconfigure(self._static["paper"], state="normal" if o > 0.02 else "hidden")
        # flap tilts toward the viewer: top edge drops and widens slightly
        ft = fy + fh * (0.26 + 0.07 * o)
        e = 7 * S * o
        self.coords(self._static["front"], *rounded(fx - e, ft, fx + fw + e, fy + fh, r))
        self.coords(self._static["shine"], fx - e + r, ft + 1, fx + fw + e - r, ft + 1)
        lift = 5 * S * o
        self.coords(self._static["title"], fx + 18 * S, fy + fh - 40 * S + lift)
        self.coords(self._static["sub"], fx + 18 * S, fy + fh - 20 * S + lift)

    def _draw_pills(self) -> None:
        bg, ink = theme.c(self.bg_name), theme.c("text")
        for i, p in enumerate(self.pills):
            poly, dot, label, count = p.items
            if p.mode == "hidden" or (p.mode in ("rise",) and self.clock - self.t_open < p.delay):
                for it in p.items:
                    self.itemconfigure(it, state="hidden")
                continue
            active = p.key in self.selected
            s = p.scale * (1 + 0.12 * math.sin(p.pop * math.pi)) * (1.0 if active else 0.97)
            w, h = p.w * s, p.h * s
            self.coords(poly, *rounded(p.x - w / 2, p.y - h / 2, p.x + w / 2, p.y + h / 2, h / 2))
            hot = i == self.hover
            if active:
                fill = theme.mix(bg, p.color, 0.32 if hot else 0.22)
                self.itemconfigure(poly, state="normal", fill=fill, outline=p.color)
                self.itemconfigure(dot, fill=p.color)
                text_c = ink
            else:
                self.itemconfigure(poly, state="normal", fill=theme.c("surface2"), outline=theme.c("border"))
                self.itemconfigure(dot, fill=theme.c("border"))
                text_c = theme.c("muted")
            d = 4.5 * theme.S * s
            dx = p.x - w / 2 + 16 * theme.S * s
            self.itemconfigure(dot, state="normal")
            self.coords(dot, dx - d, p.y - d, dx + d, p.y + d)
            self.itemconfigure(label, state="normal", text=p.label, fill=text_c)
            self.coords(label, dx + 12 * theme.S * s, p.y)
            n = self.counts.get(p.key)
            self.itemconfigure(count, state="normal" if n is not None else "hidden",
                               text="" if n is None else str(n), fill=theme.mix(bg, p.color if active else text_c, 0.9))
            self.coords(count, p.x + w / 2 - 14 * theme.S * s, p.y)
