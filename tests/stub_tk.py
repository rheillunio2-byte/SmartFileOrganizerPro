"""A permissive fake of tkinter + customtkinter so the UI code can be smoke-tested headlessly.

It cannot judge how things *look* — it catches crashes, wrong attribute names, bad logic and
wiring mistakes, and lets tests drive events on a virtual clock.
"""

import heapq
import itertools
import sys
import time
import types

CLOCK = {"t": 1000.0}
_ids = itertools.count(1)
_queue: list = []


class TclError(Exception):
    pass


class Event:
    def __init__(self, **kw):
        self.x = self.y = self.x_root = self.y_root = 0
        self.width = self.height = 0
        self.__dict__.update(kw)


class Widget:
    registry: list = []

    def __init__(self, master=None, *args, **kwargs):
        self.master = master
        self.kw = dict(kwargs)
        self.children = []
        self._binds = {}
        self._destroyed = False
        self._w = f".w{next(_ids)}"
        if master is not None and hasattr(master, "children"):
            master.children.append(self)
        Widget.registry.append(self)
        self._text = kwargs.get("text", "")
        self._value = 0

    # tk/ctk common API ---------------------------------------------------
    def configure(self, **kw):
        self.kw.update(kw)
        if "text" in kw:
            self._text = kw["text"]

    config = configure

    def cget(self, key):
        return self.kw.get(key, "normal")

    def bind(self, seq=None, fn=None, add=None):
        self._binds.setdefault(seq, []).append(fn)

    def after(self, ms, fn=None, *args):
        if self._destroyed:
            raise TclError("destroyed")
        n = next(_ids)
        heapq.heappush(_queue, (CLOCK["t"] + ms / 1000.0, n, fn, args, self))
        return n

    def after_cancel(self, ident):
        global _queue
        _queue = [e for e in _queue if e[1] != ident]
        heapq.heapify(_queue)

    def destroy(self):
        self._destroyed = True
        for c in list(self.children):
            c.destroy()
        if self.master is not None and hasattr(self.master, "children") and self in self.master.children:
            self.master.children.remove(self)

    def winfo_children(self): return list(self.children)
    def winfo_width(self): return self.kw.get("width_px", 900)
    def winfo_height(self): return self.kw.get("height_px", 400)
    def winfo_reqwidth(self): return 100
    def winfo_ismapped(self): return not self._destroyed
    def winfo_viewable(self): return True
    def winfo_fpixels(self, _): return 96.0
    def winfo_pointerxy(self): return (POINTER[0], POINTER[1])
    def winfo_pointerx(self): return POINTER[0]
    def winfo_pointery(self): return POINTER[1]
    def winfo_rootx(self): return 0
    def winfo_rooty(self): return 0
    def winfo_id(self): return 1
    def state(self): return "normal"
    def get(self): return self._value if not isinstance(self._value, str) else self._value
    def set(self, v=None): self._value = v
    def select(self): self._value = 1
    def deselect(self): self._value = 0
    def pack(self, **kw): return None
    def grid(self, **kw): return None
    def place(self, **kw): return None
    def place_forget(self): return None
    def lift(self, *a): return None
    def lower(self, *a): return None
    def delete(self, *a): return None
    def insert(self, *a): return None
    def focus_set(self): return None
    def bind_all(self, seq=None, fn=None, add=None): return None

    def __getattr__(self, name):
        if name.startswith("create_"):
            return lambda *a, **k: next(_ids)
        if name.startswith("_"):
            raise AttributeError(name)
        return lambda *a, **k: None


POINTER = [100, 100]


def fire(widget, seq, **kw):
    ev = Event(**kw)
    for fn in list(widget._binds.get(seq, [])):
        fn(ev)


def advance(seconds, step=0.016):
    """Run scheduled callbacks on a virtual clock."""
    end = CLOCK["t"] + seconds
    while True:
        if _queue and _queue[0][0] <= end:
            when, _, fn, args, widget = heapq.heappop(_queue)
            CLOCK["t"] = max(CLOCK["t"], when)
            if not widget._destroyed and fn:
                fn(*args)
        else:
            CLOCK["t"] = end
            break


def install():
    time.perf_counter = lambda: CLOCK["t"]

    tk = types.ModuleType("tkinter")
    for name in ("Canvas", "Toplevel", "Frame", "Label", "Tk", "Misc"):
        setattr(tk, name, type(name, (Widget,), {}))
    tk.TclError = TclError
    font = types.ModuleType("tkinter.font")

    class Font:
        def __init__(self, *a, **k): pass
        def measure(self, text): return 8 * len(text)

    font.Font = Font
    tk.font = font
    fd, mb = types.ModuleType("tkinter.filedialog"), types.ModuleType("tkinter.messagebox")
    fd.askdirectory = lambda **k: ""
    fd.asksaveasfilename = lambda **k: ""
    mb.askyesno = lambda *a, **k: True
    mb.showinfo = mb.showwarning = mb.showerror = lambda *a, **k: MESSAGES.append(a)
    tk.filedialog, tk.messagebox = fd, mb

    ctk = types.ModuleType("customtkinter")
    ctk.__version__ = "5.2.2"
    ctk._mode = "Dark"
    for name in ("CTk", "CTkFrame", "CTkLabel", "CTkButton", "CTkProgressBar", "CTkSwitch", "CTkEntry",
                 "CTkSegmentedButton", "CTkScrollableFrame", "CTkTextbox", "CTkOptionMenu", "CTkCheckBox"):
        setattr(ctk, name, type(name, (Widget,), {}))
    class CTkEntry(Widget):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._value = ""

        def delete(self, *a):
            self._value = ""

    ctk.CTkEntry = CTkEntry
    def _strict_place(self, **kw):
        if "width" in kw or "height" in kw:
            raise ValueError("'width' and 'height' arguments must be passed to the constructor of the widget, not the place method")

    for _n in ("CTkFrame", "CTkLabel", "CTkButton", "CTkProgressBar", "CTkSwitch", "CTkEntry",
               "CTkSegmentedButton", "CTkScrollableFrame"):
        setattr(getattr(ctk, _n), "place", _strict_place)
    ctk.CTkFont = lambda **k: ("Segoe UI", k.get("size", 12), k.get("weight", "normal"))
    ctk.get_appearance_mode = lambda: ctk._mode
    ctk.set_appearance_mode = lambda m: setattr(ctk, "_mode", "Dark" if m in ("Dark", "System") else "Light")
    ctk.set_default_color_theme = lambda t: None

    sys.modules.update({"tkinter": tk, "tkinter.font": font, "tkinter.filedialog": fd,
                        "tkinter.messagebox": mb, "customtkinter": ctk})
    return tk, ctk


MESSAGES: list = []
