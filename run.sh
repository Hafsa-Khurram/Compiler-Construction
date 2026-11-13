#!/bin/sh
# Runs a BeginnerScript program:  ./run.sh input.txt
cd "$(dirname "$0")"
[ -f build/classes/Main.class ] || ./build.sh
exec java -cp "lib/java-cup-11b-runtime.jar:build/classes" Main "$@"
