@echo off
:: [---------Below you have to specifiy the project directory-------------]

set project_dir_path = "C:\Users\hoisc\PycharmProjects\Grafikrechner"

::[-----------------------------------------------------------------------]
cd %project_dir_path%
pyinstaller --windowed --onefile main.py

pause
