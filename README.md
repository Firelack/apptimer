# 💪 Personalized Routine App

This application allows you to create, modify, and launch personalized workout or activity routines.

## 📚 Table of Contents

- [✨ Features](#-features)
- [📁 Available Versions](#-available-versions-different-progression)
- [▶️ How to run](#-how-to-run)
- [⚠️ Known Issues](#-known-issues)
- [🌍 Language Support](#-language-support)
- [🛠️ Notes](#️-notes)

## ✨ Features

- Built-in routines with customizable exercises.
- Modify the order of exercises and routines.
- Launch routines with a built-in timer.
- Language selection.

## 📁 Available Versions (different progression)

- [`routineapp.py`](./routineapp.py) — Full GUI version with multilingual support (English, French, and more).
- [`fonctionbase.py`](./fonctionbase.py) — Minimal version using only Python logic (no GUI, French only).

⚠️ Important: The two versions use different storage formats for routines, so saved routines are not shared between them.

## ▶️ How to Run

1. Download the latest release zip file ([`app.zip`](https://github.com/Firelack/apptimer/releases/download/v1/app.zip))
2. Make sure that `routineapp.exe` and the `necessary` **folder** are in the **same folder**.
3. Double-click `routineapp.exe` to launch the application.

## ⚠️ Known Issues

- **Timer speed bug**: If the timer runs too fast, restarting the app usually fixes it. Cause unknown.

## 🌍 Language Support

Languages are loaded from  [`language.json`](./language.json).  
To add or modify a language:
1. Edit or extend the existing JSON structure.
2. Make sure keys match those in the app code.

## 🔧 Notes

- Some comments and function names are still in French; they will be updated in a future version.

## To do

- Add a .ico for the .exe