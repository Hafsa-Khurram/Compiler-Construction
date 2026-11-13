@echo off
rem Builds the BeginnerScript compiler into the build folder.
rem Needs only a JDK (Java 11 or newer); JFlex and CUP are in lib\.
cd /d "%~dp0"
if not exist build\gen mkdir build\gen
if not exist build\classes mkdir build\classes

echo [1/3] JFlex: scanner.jflex
java -jar lib\jflex-full-1.9.1.jar -q -d build\gen scanner.jflex || goto :error
echo [2/3] CUP: parser.cup
java -jar lib\java-cup-11b.jar -destdir build\gen parser.cup || goto :error
echo [3/3] javac
javac -nowarn -encoding UTF-8 -cp lib\java-cup-11b-runtime.jar -d build\classes *.java build\gen\*.java || goto :error
echo.
echo Build OK. Run a program with:  run.bat examples\input.txt
exit /b 0

:error
echo.
echo Build FAILED
exit /b 1
