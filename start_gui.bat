@echo off
rem Starts BeginnerScript Compiler Studio (double-click this file).
cd /d "%~dp0"
set PY=python
where python >nul 2>nul || set PY=py
%PY% -c "import customtkinter" >nul 2>nul || %PY% -m pip install -r requirements.txt
%PY% gui.py
if errorlevel 1 pause
