@echo off
:: [---------Below you have to specifiy the project directory-------------]

set project_dir_path = "C:\Users\hoisc\PycharmProjects\Grafikrechner"
set source_path = C:\Users\hoisc\PycharmProjects\Grafikrechner\GraphCalc\source

::[-----------------------------------------------------------------------]
cd %project_dir_path%

pyinstaller --windowed --onefile --name GrafiXRechner --icon C:\Users\hoisc\PycharmProjects\Grafikrechner\source\img\icon.ico --path C:\Users\hoisc\PycharmProjects\Grafikrechner\venv\Lib\site-packages --add-data "C:\Users\hoisc\PycharmProjects\Grafikrechner\source;source"  main.py

pause
