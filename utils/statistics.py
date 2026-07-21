from pathlib import Path


def get_latest_statistics():

    history_file = Path("history/history.txt")

    statistics = {
        "Images": 0,
        "Documents": 0,
        "Videos": 0,
        "Music": 0,
        "Archives": 0,
        "Others": 0,
        "Total": 0
    }

    if not history_file.exists():
        return statistics

    with open(history_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in reversed(lines):

        line = line.strip()

        if line.startswith("Images:"):
            statistics["Images"] = int(line.split(":")[1])

        elif line.startswith("Documents:"):
            statistics["Documents"] = int(line.split(":")[1])

        elif line.startswith("Videos:"):
            statistics["Videos"] = int(line.split(":")[1])

        elif line.startswith("Music:"):
            statistics["Music"] = int(line.split(":")[1])

        elif line.startswith("Archives:"):
            statistics["Archives"] = int(line.split(":")[1])

        elif line.startswith("Others:"):
            statistics["Others"] = int(line.split(":")[1])

        elif line.startswith("Total:"):
            statistics["Total"] = int(line.split(":")[1])
            break

    return statistics