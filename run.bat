@echo off
rem Runs a BeginnerScript program:  run.bat examples\input.txt
cd /d "%~dp0"
if not exist build\classes\Main.class call build.bat || exit /b 1
java -cp "lib\java-cup-11b-runtime.jar;build\classes" Main %*
