import customtkinter as ctk
from tkinter import messagebox


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        title = ctk.CTkLabel(
            self,
            text="⚙️ Settings",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=(30, 20))

        container = ctk.CTkFrame(self)

        container.pack(
            padx=40,
            pady=10,
            fill="both",
            expand=True
        )

        appearance_title = ctk.CTkLabel(
            container,
            text="Appearance",
            font=("Segoe UI", 20, "bold")
        )

        appearance_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        appearance_label = ctk.CTkLabel(
            container,
            text="Theme Mode",
            font=("Segoe UI", 15)
        )

        appearance_label.pack(
            anchor="w",
            padx=20
        )

        self.appearance_menu = ctk.CTkOptionMenu(
            container,
            values=[
                "System",
                "Light",
                "Dark"
            ]
        )

        self.appearance_menu.set("Dark")

        self.appearance_menu.pack(
            padx=20,
            pady=(5, 20),
            anchor="w"
        )

        theme_label = ctk.CTkLabel(
            container,
            text="Color Theme",
            font=("Segoe UI", 15)
        )

        theme_label.pack(
            anchor="w",
            padx=20
        )

        self.theme_menu = ctk.CTkOptionMenu(
            container,
            values=[
                "Blue",
                "Green",
                "Dark Blue"
            ]
        )

        self.theme_menu.set("Blue")

        self.theme_menu.pack(
            padx=20,
            pady=(5, 20),
            anchor="w"
        )

        self.auto_open = ctk.CTkCheckBox(
            container,
            text="Automatically open folder after organizing"
        )

        self.auto_open.select()

        self.auto_open.pack(
            anchor="w",
            padx=20,
            pady=8
        )

        self.auto_refresh = ctk.CTkCheckBox(
            container,
            text="Automatically refresh history"
        )

        self.auto_refresh.select()

        self.auto_refresh.pack(
            anchor="w",
            padx=20,
            pady=8
        )

        button_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        button_frame.pack(
            pady=40
        )

        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            width=180,
            command=self.save_settings
        )

        save_button.pack(
            side="left",
            padx=10
        )

        reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Reset Defaults",
            width=180,
            fg_color="firebrick",
            hover_color="#8B0000",
            command=self.reset_settings
        )

        reset_button.pack(
            side="left",
            padx=10
        )

    def save_settings(self):

        mode = self.appearance_menu.get()

        if mode == "System":
            ctk.set_appearance_mode("System")

        elif mode == "Light":
            ctk.set_appearance_mode("Light")

        else:
            ctk.set_appearance_mode("Dark")

        messagebox.showinfo(
            "Settings",
            "Settings saved successfully."
        )

    def reset_settings(self):

        self.appearance_menu.set("Dark")

        self.theme_menu.set("Blue")

        self.auto_open.select()

        self.auto_refresh.select()

        ctk.set_appearance_mode("Dark")

        messagebox.showinfo(
            "Settings",
            "Settings have been reset."
        )