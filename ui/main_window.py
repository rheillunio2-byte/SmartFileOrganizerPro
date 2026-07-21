import customtkinter as ctk

from .sidebar import Sidebar
from .dashboard import Dashboard
from .organize_page import OrganizePage
from .history_page import HistoryPage
from .settings_page import SettingsPage
from .about_page import AboutPage
from utils.statistics import get_latest_statistics

class MainWindow(ctk.CTk):

    def hide_all_pages(self):

        self.dashboard.pack_forget()

        self.organize_page.pack_forget()

        self.history_page.pack_forget()

        self.settings_page.pack_forget()

        self.about_page.pack_forget()

    def show_page(self, page):

        self.hide_all_pages()

        if page == "dashboard":
            self.dashboard.pack(
                side="right",
                fill="both",
                expand=True
            )

        elif page == "organize":
            self.organize_page.pack(
                side="right",
                fill="both",
                expand=True
            )

        elif page == "history":
            self.history_page.pack(
                side="right",
                fill="both",
                expand=True
            )

        elif page == "settings":
            self.settings_page.pack(
                side="right",
                fill="both",
                expand=True
            )

        elif page == "about":
            self.about_page.pack(
                side="right",
                fill="both",
                expand=True
            )

    def __init__(self):

        super().__init__()

        self.title("Smart File Organizer Pro")

        self.geometry("1200x700")

        self.minsize(1000, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.sidebar = Sidebar(self)

        self.dashboard = Dashboard(self)
        self.history_page = HistoryPage(self)
        self.settings_page = SettingsPage(self)
        self.about_page = AboutPage(self)

        self.organize_page = OrganizePage(self)

        self.show_page("dashboard")

        latest = get_latest_statistics()

        self.dashboard.update_statistics(latest)