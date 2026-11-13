#!/bin/sh
# Builds the BeginnerScript compiler into build/ (macOS / Linux / Git Bash).
# Needs only a JDK (Java 11 or newer); JFlex and CUP are in lib/.
set -e
cd "$(dirname "$0")"
mkdir -p build/gen build/classes
echo "[1/3] JFlex: scanner.jflex"
java -jar lib/jflex-full-1.9.1.jar -q -d build/gen scanner.jflex
echo "[2/3] CUP: parser.cup"
java -jar lib/java-cup-11b.jar -destdir build/gen parser.cup
echo "[3/3] javac"
javac -nowarn -encoding UTF-8 -cp lib/java-cup-11b-runtime.jar -d build/classes *.java build/gen/*.java
echo
echo "Build OK. Run a program with:  ./run.sh input.txt"
