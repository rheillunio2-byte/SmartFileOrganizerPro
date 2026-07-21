import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox


class HistoryPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        title = ctk.CTkLabel(
            self,
            text="📜 Organization History",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=(30, 20))

        search_frame = ctk.CTkFrame(self)

        search_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search folder, date, or category..."
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 5),
            pady=10
        )

        search_button = ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=120,
            command=self.search_history
        )

        search_button.pack(
            side="right",
            padx=(5, 10),
            pady=10
        )

        self.textbox = ctk.CTkTextbox(
            self,
            width=900,
            height=500,
            font=("Consolas", 14)
        )

        self.textbox.pack(
            padx=30,
            pady=10,
            fill="both",
            expand=True
        )

        button_frame = ctk.CTkFrame(self)

        button_frame.pack(
            pady=15
        )

        refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            width=150,
            command=self.refresh_history
        )

        refresh_button.pack(
            side="left",
            padx=10
        )

        clear_button = ctk.CTkButton(
            button_frame,
            text="🗑 Clear History",
            width=150,
            fg_color="firebrick",
            hover_color="#8B0000",
            command=self.clear_history
        )

        clear_button.pack(
            side="left",
            padx=10
        )

        self.load_history()

    def load_history(self):

        history_file = Path("history/history.txt")

        self.textbox.delete("1.0", "end")

        if history_file.exists():

            with open(history_file, "r", encoding="utf-8") as file:

                self.textbox.insert(
                    "end",
                    file.read()
                )

        else:

            self.textbox.insert(
                "end",
                "No history available yet."
            )

    def search_history(self):

        history_file = Path("history/history.txt")

        keyword = self.search_entry.get().lower()

        self.textbox.delete("1.0", "end")

        if not history_file.exists():

            self.textbox.insert(
                "end",
                "No history available."
            )

            return

        with open(history_file, "r", encoding="utf-8") as file:

            content = file.read()

        records = content.split("=" * 50)

        found = False

        for record in records:

            if keyword in record.lower():

                self.textbox.insert(
                    "end",
                    "=" * 50 + "\n"
                )

                self.textbox.insert(
                    "end",
                    record.strip() + "\n\n"
                )

                found = True

        if not found:

            self.textbox.insert(
                "end",
                "No matching records found."
            )

    def refresh_history(self):

        self.search_entry.delete(0, "end")

        self.load_history()

    def clear_history(self):

        answer = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to delete all history?"
        )

        if not answer:
            return

        history_file = Path("history/history.txt")

        history_file.parent.mkdir(exist_ok=True)

        history_file.write_text("", encoding="utf-8")

        self.load_history()

        messagebox.showinfo(
            "Success",
            "History cleared successfully."
        )