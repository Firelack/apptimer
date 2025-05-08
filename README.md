# 💪 Personalized Routine App

This application allows you to create, modify, and launch personalized workout or activity routines with ease.

## ✨ Features

- Built-in routines with customizable exercises.
- Modify the order of exercises and routines.
- Launch routines with a built-in timer.
- Optional language selection: **English** or **French** (available in specific versions).
- Recent updates have improved the interface and are only available in the `languageversion.py` and `approutine.exe` files.

## 🤔 How to run application ?

Steps:
1. Download the approutine.exe file from the release page.
2. Locate the file on your computer.
3. Double-click the file to start the application.

Note: 
- If you encounter any issues running the application, make sure that your system meets the necessary requirements or check the troubleshooting section.
- To view the source code of the app, run the `languageversion.py` file.

## 📁 Available Versions

- `approutine.exe`: Complete and ready-to-use version of the application in executable form.
- `languageversion.py`: Full-featured version with interface and language selection (English/French).
- `fonctionbase.py`: Minimal version — routines managed in pure Python, no graphical interface.
- `routineapp.py`: Functional interface, but basic visual design.
- `betterinterface.py`: Improved interface (**French only**).

## ⚠️ Known Issues

- **Timer speed bug**: If the timer runs too fast, restarting the app usually fixes it. Cause unknown.

## 🔧 Notes

- Some comments and function names in the codebase are still in French.

## 🚨 Warning

- Different versions of the app code use separate files to save progress. If you switch between versions, your progress may not be saved.

## To add a new language 

- Add it in `languageversion.py` : *for lang in ["English", "French","Spanish"]:*
- Add all the text in `language.json`

## ☑️ To do

- Size of :
 - Text in button + if select, see all text
- Modification of exercices (+tab) -> change delete ex in this page and actual delete button = modification