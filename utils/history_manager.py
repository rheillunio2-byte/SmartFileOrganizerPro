from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("history/history.txt")


def save_history(folder, stats):

    HISTORY_FILE.parent.mkdir(exist_ok=True)

    with open(HISTORY_FILE, "a", encoding="utf-8") as file:

        file.write("=" * 50 + "\n")
        file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Folder: {folder}\n\n")

        for key, value in stats.items():
            file.write(f"{key}: {value}\n")

        file.write("\n")