rem @echo off
for /f %%i in ('python -c "import site; print(site.getsitepackages()[0])"') do set PYTHON_ROOT="%%i"
rem copy %PYTHON_ROOT%\Lib\site-packages\arcade\Win64\avbin.dll .
rem copy avbin.dll avbin64.dll
rem pyinstaller --exclude-module tkinter --add-data resources;resources --add-data ./avbin64.dll;. --add-data ./avbin.dll;Win64 --onefile --noconsole sample.py
rem del avbin.dll
rem del avbin64.dll
rem pause
