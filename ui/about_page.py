import customtkinter as ctk


class AboutPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        title = ctk.CTkLabel(
            self,
            text="ℹ️ About Smart File Organizer Pro",
            font=("Segoe UI", 30, "bold")
        )

        title.pack(pady=(30, 20))

        version = ctk.CTkLabel(
            self,
            text="Version 1.0.0",
            font=("Segoe UI", 18)
        )

        version.pack()

        developer = ctk.CTkLabel(
            self,
            text="Developed by\nRheil Evans T. Lunio",
            font=("Segoe UI", 18, "bold"),
            justify="center"
        )

        developer.pack(pady=20)

        description = ctk.CTkTextbox(
            self,
            width=850,
            height=250,
            font=("Segoe UI", 15)
        )

        description.pack(
            padx=40,
            pady=10
        )

        description.insert(
            "1.0",
            """Smart File Organizer Pro is a desktop application designed to organize files automatically into categorized folders.

Key Features

• Organize files by type
• Dashboard with statistics
• Organization history
• Search history
• User settings
• Clean and modern interface
• Fast and lightweight

This project was developed using Python and CustomTkinter as part of my journey in learning desktop application development and Computer Science.

Thank you for using Smart File Organizer Pro!
"""
        )

        description.configure(
            state="disabled"
        )

        footer = ctk.CTkLabel(
            self,
            text="© 2026 Rheil Evans T. Lunio • All Rights Reserved",
            font=("Segoe UI", 13)
        )

        footer.pack(
            pady=(20, 10)
        )