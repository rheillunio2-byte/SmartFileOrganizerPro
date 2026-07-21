# SmartFileOrganizerPro 📁

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Pillow](https://img.shields.io/badge/Image%20Processing-Pillow-yellow)
![PyInstaller](https://img.shields.io/badge/Packaging-PyInstaller-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A **Python-based intelligent file management application** designed to automatically organize, categorize, and manage files into structured folders.

SmartFileOrganizerPro helps users maintain a cleaner digital workspace by reducing repetitive manual file sorting through automation, file detection, and user-friendly graphical controls.

---

# 🖥️ Application Preview

<table>
  <tr>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Dashboard).png" width="400">
      <br>
      <b>Dashboard</b>
    </td>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Organize).png" width="400">
      <br>
      <b>Organize Files</b>
    </td>
  </tr>

  <tr>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(History).png" width="400">
      <br>
      <b>History Tracking</b>
    </td>
    <td align="center">
      <img src="Images/SmartFileOrganizerPro%20(Settings).png" width="400">
      <br>
      <b>Application Settings</b>
    </td>
  </tr>

  <tr>
    <td align="center" colspan="2">
      <img src="Images/SmartFileOrganizerPro%20(About).png" width="400">
      <br>
      <b>About Section</b>
    </td>
  </tr>
</table>

---

# 📌 Overview

SmartFileOrganizerPro is a desktop file organization application built with **Python** and **CustomTkinter**.

The application automatically identifies file types based on their extensions and organizes them into categorized folders such as:

- 📷 Images
- 📄 Documents
- 🎵 Audio
- 🎬 Videos
- 📦 Archives
- 📁 Other file types

The goal of this project is to provide a simple, efficient, and user-friendly solution for managing digital files.

---

# ✨ Features

✅ Automatic file organization  
✅ Extension-based file classification  
✅ Automatic folder creation  
✅ File movement automation  
✅ File organization history tracking  
✅ User-friendly graphical interface  
✅ Customizable application settings  
✅ Lightweight desktop application  
✅ Executable (.exe) support using PyInstaller  

---

# 🛠️ Technologies Used

## Programming Language

- Python 3.x

## GUI Framework

- CustomTkinter

## Libraries

- `os` — File system operations
- `shutil` — File movement and management
- `pathlib` — File path handling
- `Pillow` — Image processing
- `pandas` — Data handling

## Development Tools

- Visual Studio Code
- PyInstaller

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/rheillunio2-byte/SmartFileOrganizerPro.git
```

## 2. Navigate to the project folder

```bash
cd SmartFileOrganizerPro
```

## 3. Install required dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the application

```bash
python main.py
```

---

# 📖 How It Works

1. User selects a folder to organize.
2. The application scans all files inside the folder.
3. File extensions are analyzed.
4. Files are classified into categories.
5. Required folders are created automatically.
6. Files are moved into their corresponding folders.

Example:

```
Before:

📁 Downloads
 ├── image.jpg
 ├── document.pdf
 └── song.mp3


After:

📁 Downloads
 ├── Images
 │    └── image.jpg
 │
 ├── Documents
 │    └── document.pdf
 │
 └── Music
      └── song.mp3
```

---

# 📂 Project Structure

```
SmartFileOrganizerPro/
│
├── main.py
├── Images/
│   ├── Dashboard Screenshot
│   ├── Organize Screenshot
│   ├── History Screenshot
│   ├── Settings Screenshot
│   └── About Screenshot
│
├── docs/
│   └── CONTRIBUTING.md
│
├── README.md
├── LICENSE
└── requirements.txt
```

---

# 🔮 Future Improvements

Planned improvements:

- Drag-and-drop file organization
- Custom user-defined categories
- Duplicate file detection
- Cloud backup integration
- File search functionality
- Dark/light theme customization
- More advanced file management features

---

# 👨‍💻 Developer

**Rheil Evans T. Lunio**  
Computer Science Student  
University of Science and Technology of Southern Philippines (USTP)

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

Please read the [CONTRIBUTING.md](https://github.com/rheillunio2-byte/SmartFileOrganizerPro/blob/main/docs/CONTRIBUTING.md) guide before submitting changes.

---

# 📄 License

This project is licensed under the [MIT License](https://github.com/rheillunio2-byte/SmartFileOrganizerPro/blob/main/LICENSE).
