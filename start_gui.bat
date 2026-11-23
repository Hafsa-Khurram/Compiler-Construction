@echo off
rem Starts BeginnerScript Compiler Studio (double-click this file).
cd /d "%~dp0"
rem Prefer the "py" launcher from python.org: it works even if Python is not on PATH, and it
rem avoids the Microsoft Store placeholder "python.exe" that only opens the Store.
set PY=py
where py >nul 2>nul || set PY=python
%PY% -c "import customtkinter" >nul 2>nul || %PY% -m pip install -r requirements.txt
%PY% gui.py
if errorlevel 1 pause
