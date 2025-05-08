# 💪 Personalized Routine App

This application allows you to create, modify, and launch personalized workout or activity routines.

## ✨ Features

- Built-in routines with customizable exercises.
- Modify the order of exercises and routines.
- Launch routines with a built-in timer.
- Language selection (available in specific versions).

## 📁 Available Versions

- `routineapp.py`: Full-featured version with interface and language selection (English/French).
- `fonctionbase.py`: Minimal version — routines managed in pure Python, no graphical interface, only french.

## ⚠️ Known Issues

- **Timer speed bug**: If the timer runs too fast, restarting the app usually fixes it. Cause unknown.

## 🚨 Warning

- Different versions of the app code use separate files to save progress. If you switch between versions, your progress may not be saved.

## 🔧 Notes

- Some comments and function names in the codebase are still in French.
- To add a new language :
    - Add it in `routineapp.py` : *for lang in ["English", "French","Spanish",...]:*
    - Add all the text in `language.json`

## ☑️ To do

- Modification of exercices (+tab) -> change delete ex in this page and actual delete button = modification