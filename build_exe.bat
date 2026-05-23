@echo off
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python build_exe.py
pause
