import customtkinter as ctk
from tkinter import filedialog, messagebox

from utils.organizer import organize
from utils.history_manager import save_history

class OrganizePage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.selected_folder = ""

        title = ctk.CTkLabel(
            self,
            text="📁 Organize Files",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=(30, 20))

        folder_title = ctk.CTkLabel(
            self,
            text="Selected Folder",
            font=("Segoe UI", 16, "bold")
        )

        folder_title.pack(anchor="w", padx=40)

        self.folder_label = ctk.CTkLabel(
            self,
            text="No folder selected.",
            width=700,
            anchor="w",
            corner_radius=8
        )

        self.folder_label.pack(
            padx=40,
            pady=(5, 20),
            fill="x"
        )

        select_button = ctk.CTkButton(
            self,
            text="📂 Select Folder",
            command=self.select_folder,
            width=220,
            height=45
        )

        select_button.pack(pady=10)

        organize_button = ctk.CTkButton(
            self,
            text="🚀 Organize Files",
            command=self.organize_files,
            width=220,
            height=45
        )

        organize_button.pack(pady=10)

        progress_title = ctk.CTkLabel(
            self,
            text="Progress",
            font=("Segoe UI", 16, "bold")
        )

        progress_title.pack(pady=(30, 5))

        self.progress = ctk.CTkProgressBar(self)

        self.progress.pack(
            padx=40,
            fill="x"
        )

        self.progress.set(0)

        self.status = ctk.CTkLabel(
            self,
            text="Status: Waiting..."
        )

        self.status.pack(pady=20)

    def select_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.selected_folder = folder

            self.folder_label.configure(text=folder)

            self.status.configure(
                text="Status: Folder selected."
            )

    def organize_files(self):

        if self.selected_folder == "":

            messagebox.showwarning(
                "Warning",
                "Please select a folder first."
            )

            return

        self.status.configure(
            text="Status: Organizing files..."
        )

        self.progress.set(0.25)

        self.update()

        try:

            stats = organize(self.selected_folder)

            save_history(
                self.selected_folder,
                stats
            )

            self.master.dashboard.update_statistics(stats)

            print(type(self.master))
            print(hasattr(self.master, "history_page"))

            if hasattr(self.master, "history_page"):
                print(type(self.master.history_page))
                print(dir(self.master.history_page))

            print(type(self.master.history_page))
            print(dir(self.master.history_page))

            self.master.history_page.load_history()
            
            self.progress.set(1)

            self.status.configure(
                text="Status: Completed!"
            )

            messagebox.showinfo(
                "Success",
                f"""Files organized successfully!

            Images: {stats['Images']}
            Documents: {stats['Documents']}
            Videos: {stats['Videos']}
            Music: {stats['Music']}
            Archives: {stats['Archives']}
            Others: {stats['Others']}

            Total Files: {stats['Total']}
            """
            )

        except Exception as e:

            self.progress.set(0)

            self.status.configure(
                text="Status: Failed."
            )

            messagebox.showerror(
                "Error",
                str(e)
            )