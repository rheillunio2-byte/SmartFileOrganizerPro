import customtkinter as ctk


class Dashboard(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        title = ctk.CTkLabel(
            self,
            text="📊 Dashboard",
            font=("Segoe UI", 30, "bold")
        )

        title.pack(pady=25)

        self.cards = {}

        grid = ctk.CTkFrame(self)

        grid.pack(
            padx=25,
            pady=10,
            fill="both",
            expand=True
        )

        categories = [
            ("🖼 Images", "Images"),
            ("📄 Documents", "Documents"),
            ("🎥 Videos", "Videos"),
            ("🎵 Music", "Music"),
            ("📦 Archives", "Archives"),
            ("📁 Others", "Others")
        ]

        for index, (title_text, key) in enumerate(categories):

            row = index // 3
            column = index % 3

            card = ctk.CTkFrame(
                grid,
                corner_radius=15
            )

            card.grid(
                row=row,
                column=column,
                padx=15,
                pady=15,
                sticky="nsew"
            )

            label = ctk.CTkLabel(
                card,
                text=title_text,
                font=("Segoe UI", 18)
            )

            label.pack(pady=(20, 5))

            value = ctk.CTkLabel(
                card,
                text="0",
                font=("Segoe UI", 34, "bold")
            )

            value.pack(pady=(0, 20))

            self.cards[key] = value

        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

        for i in range(2):
            grid.grid_rowconfigure(i, weight=1)

        total_frame = ctk.CTkFrame(
            self,
            corner_radius=15
        )

        total_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        title = ctk.CTkLabel(
            total_frame,
            text="Total Files Organized",
            font=("Segoe UI", 18)
        )

        title.pack(pady=(15, 5))

        self.total_label = ctk.CTkLabel(
            total_frame,
            text="0",
            font=("Segoe UI", 42, "bold")
        )

        self.total_label.pack(pady=(0, 20))

    def update_statistics(self, stats):

        self.cards["Images"].configure(
            text=str(stats["Images"])
        )

        self.cards["Documents"].configure(
            text=str(stats["Documents"])
        )

        self.cards["Videos"].configure(
            text=str(stats["Videos"])
        )

        self.cards["Music"].configure(
            text=str(stats["Music"])
        )

        self.cards["Archives"].configure(
            text=str(stats["Archives"])
        )

        self.cards["Others"].configure(
            text=str(stats["Others"])
        )

        self.total_label.configure(
            text=str(stats["Total"])
        )