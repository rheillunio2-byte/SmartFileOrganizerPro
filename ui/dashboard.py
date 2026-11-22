import customtkinter as ctk

from utils.file_types import CATEGORIES, CATEGORY_COLORS, empty_stats
from utils.statistics import get_lifetime_statistics

from . import theme
from .widgets import BarChart, PageHeader, StatCard, card
from .wordmark import TechWordmark
from . import anim


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PALETTE["bg"], corner_radius=0)
        self.stats = empty_stats()
        self.lifetime = {"totals": empty_stats(), "runs": 0, "last_run": ""}

        self.header = PageHeader(self, "Dashboard", "A live overview of your last organization run")
        self.header.pack(fill="x", padx=32, pady=(28, 14))

        hero = card(self, corner_radius=20)
        hero.pack(fill="x", padx=32, pady=(0, 16))
        self.wordmark = TechWordmark(hero, text="SmartFile", height=190)
        self.wordmark.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(hero, text="Hover a letter  •  drag it  •  click to kick", font=theme.font(12),
                     text_color=theme.PALETTE["muted"]).pack(pady=(0, 12))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=26, pady=(0, 6))
        self.cards: dict[str, StatCard] = {}
        for index, key in enumerate(CATEGORIES):
            stat = StatCard(grid, key, CATEGORY_COLORS[key])
            stat.grid(row=index // 3, column=index % 3, padx=6, pady=6, sticky="nsew")
            self.cards[key] = stat
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="stat")

        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=26, pady=(6, 24))
        lower.grid_columnconfigure(0, weight=3, uniform="low")
        lower.grid_columnconfigure(1, weight=2, uniform="low")

        chart_card = card(lower)
        chart_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(chart_card, text="Last run distribution", font=theme.font(15, "bold"),
                     text_color=theme.PALETTE["text"]).pack(anchor="w", padx=20, pady=(16, 6))
        self.chart = BarChart(chart_card, [(k, CATEGORY_COLORS[k]) for k in CATEGORIES])
        self.chart.pack(fill="x", padx=20, pady=(0, 16))

        total_card = card(lower)
        total_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(total_card, text="Files organized (last run)", font=theme.font(15, "bold"),
                     text_color=theme.PALETTE["text"]).pack(anchor="w", padx=20, pady=(16, 0))
        self.total_label = ctk.CTkLabel(total_card, text="0", font=theme.font(54, "bold"),
                                        text_color=theme.PALETTE["accent"], anchor="w")
        self.total_label.pack(anchor="w", padx=20)
        self.meta = ctk.CTkLabel(total_card, text="", font=theme.font(13), text_color=theme.PALETTE["muted"],
                                 justify="left", anchor="w")
        self.meta.pack(anchor="w", padx=20, pady=(0, 16))

    # called by MainWindow every time the page is shown
    def on_show(self) -> None:
        self.header.play()
        self.wordmark.replay()
        self.update_statistics(self.stats, animate=True)

    def update_statistics(self, stats: dict, animate: bool = True) -> None:
        self.stats = {k: int(stats.get(k, 0)) for k in [*CATEGORIES, "Total"]}
        self.lifetime = get_lifetime_statistics()
        total = self.stats["Total"]
        for index, key in enumerate(CATEGORIES):
            if animate:
                self.cards[key].animate_to(self.stats[key], total, delay=index * 70)
            else:
                self.cards[key].value.configure(text=f"{self.stats[key]:,}")
        self.chart.set_data(self.stats)
        if animate:
            anim.count_up(self, self.total_label, total, 1100, 200)
        else:
            self.total_label.configure(text=f"{total:,}")
        life = self.lifetime
        last = life["last_run"] or "—"
        self.meta.configure(text=f"Lifetime: {life['totals']['Total']:,} files in {life['runs']} run(s)\nLast run: {last}")
