from pathlib import Path
import shutil

from .file_types import FILE_TYPES

def organize(folder_path):

    print("organize() started")

    folder = Path(folder_path)
    
def organize(folder_path):

    folder = Path(folder_path)

    statistics = {
        "Images": 0,
        "Documents": 0,
        "Videos": 0,
        "Music": 0,
        "Archives": 0,
        "Others": 0,
        "Total": 0
    }

    for file in folder.iterdir():

        if file.is_dir():
            continue

        moved = False

        for category, extensions in FILE_TYPES.items():

            if file.suffix.lower() in extensions:

                destination = folder / category
                destination.mkdir(exist_ok=True)

                shutil.move(
                    str(file),
                    str(destination / file.name)
                )

                statistics[category] += 1
                statistics["Total"] += 1

                moved = True
                break

        if not moved:

            other = folder / "Others"
            other.mkdir(exist_ok=True)

            shutil.move(
                str(file),
                str(other / file.name)
            )

            statistics["Others"] += 1
            statistics["Total"] += 1

    print("Returning:", statistics)
    return statistics