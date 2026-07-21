import customtkinter as ctk


class StatCard(ctk.CTkFrame):

    def __init__(self, parent, icon, title):

        super().__init__(
            parent,
            width=180,
            height=120,
            corner_radius=15
        )

        self.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI Emoji", 30)
        )

        icon_label.pack(pady=(15, 5))

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 16, "bold")
        )

        title_label.pack()

        self.value = ctk.CTkLabel(
            self,
            text="0",
            font=("Segoe UI", 28, "bold")
        )

        self.value.pack(pady=(5, 10))

    def update_value(self, number):

        self.value.configure(text=str(number))