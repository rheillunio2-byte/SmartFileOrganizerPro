"""Small animation toolkit built on ``widget.after`` (no threads, no dependencies)."""

from __future__ import annotations

import math
import time
import tkinter as tk
from typing import Callable

ENABLED = True  # toggled from Settings


def linear(t: float) -> float:
    return t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)


def ease_out_back(t: float, s: float = 1.4) -> float:
    t -= 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def approach(current: float, target: float, dt: float, seconds: float) -> float:
    """Frame-rate independent exponential smoothing."""
    return current + (target - current) * (1 - math.exp(-dt / max(seconds, 1e-4)))


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class Tween:
    """Run ``update(eased_t)`` for ``duration`` ms. Safe if the widget is destroyed mid-way."""

    def __init__(self, widget, duration: int, update: Callable[[float], None],
                 easing: Callable[[float], float] = ease_out_cubic,
                 done: Callable[[], None] | None = None, delay: int = 0):
        self.widget, self.duration, self.update = widget, max(1, duration), update
        self.easing, self.done = easing, done
        self.running = True
        self._job = None
        self._start = 0.0
        if not ENABLED:
            self._finish()
            return
        self._job = widget.after(max(1, int(delay)), self._begin)

    def _finish(self) -> None:
        self.running = False
        try:
            self.update(self.easing(1.0))
            if self.done:
                self.done()
        except tk.TclError:
            pass

    def _begin(self) -> None:
        self._start = time.perf_counter()
        self._step()

    def _step(self) -> None:
        if not self.running:
            return
        t = (time.perf_counter() - self._start) * 1000 / self.duration
        if t >= 1:
            self._finish()
            return
        try:
            self.update(self.easing(t))
            self._job = self.widget.after(16, self._step)
        except tk.TclError:
            self.running = False

    def cancel(self) -> None:
        self.running = False
        if self._job is not None:
            try:
                self.widget.after_cancel(self._job)
            except (tk.TclError, ValueError):
                pass


def count_up(widget, label, target: int, duration: int = 900, delay: int = 0,
             fmt: Callable[[int], str] = lambda n: f"{n:,}") -> Tween:
    """Animate a label's text from 0 to ``target``."""
    return Tween(widget, duration, lambda t: label.configure(text=fmt(int(round(target * t)))),
                 easing=ease_out_cubic, delay=delay)


class CanvasLoop:
    """Mixin for canvases that animate continuously. Pauses automatically when hidden."""

    fps_delay = 16

    def _loop_init(self) -> None:
        self._loop_job = None
        self._loop_last = time.perf_counter()
        self._loop_alive = True

    def start_loop(self) -> None:
        if self._loop_job is None and self._loop_alive:
            self._loop_last = time.perf_counter()
            self._loop_job = self.after(self.fps_delay, self._loop_tick)

    def stop_loop(self) -> None:
        self._loop_alive = False
        if self._loop_job is not None:
            try:
                self.after_cancel(self._loop_job)
            except (tk.TclError, ValueError):
                pass
            self._loop_job = None

    def _loop_tick(self) -> None:
        self._loop_job = None
        if not self._loop_alive:
            return
        try:
            if not self.winfo_ismapped():  # on a hidden page: idle cheaply
                self._loop_job = self.after(300, self._loop_tick)
                return
            now = time.perf_counter()
            dt = min(0.05, max(0.001, now - self._loop_last))
            self._loop_last = now
            self.step(dt)
            self._loop_job = self.after(self.fps_delay, self._loop_tick)
        except tk.TclError:
            self._loop_alive = False

    def step(self, dt: float) -> None:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError
