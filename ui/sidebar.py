import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, width=220, corner_radius=0)

        self.parent = parent

        self.pack(
            side="left",
            fill="y"
        )

        logo = ctk.CTkLabel(
            self,
            text="📂\nSmart File\nOrganizer Pro",
            font=("Segoe UI", 24, "bold")
        )

        logo.pack(pady=30)

        menu = [
            ("🏠 Dashboard", "dashboard"),
            ("📁 Organize", "organize"),
            ("📜 History", "history"),
            ("⚙️ Settings", "settings"),
            ("ℹ️ About", "about")
        ]

        for text, page in menu:

            button = ctk.CTkButton(
                self,
                text=text,
                height=45,
                command=lambda p=page: self.parent.show_page(p)
            )

            button.pack(
                fill="x",
                padx=20,
                pady=8
            )