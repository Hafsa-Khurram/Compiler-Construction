#!/usr/bin/env python3
"""
Automated tests for the BeginnerScript compiler.

Builds the compiler, runs every example program (and some programs with
mistakes in them) and checks the exact output and exit code.

Usage (from the project folder):   python tests/run_tests.py
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEP = ";" if os.name == "nt" else ":"
CLASSPATH = SEP.join([os.path.join(ROOT, "lib", "java-cup-11b-runtime.jar"), os.path.join(ROOT, "build", "classes")])

# (name, program file or source code, program input, exit code, expected stdout, expected stderr)
CASES = [
    ("sample program, adult", "examples/input.txt", "Hafsa\n21\n", 0,
     "Enter your name: Hafsa\n"
     "Enter your age: 21\n"
     "Hello, Hafsa\n"
     "You are eligible to vote.\n"
     "Welcome to BeginnerScript!\n"
     "Thank you for using BeginnerScript, Hafsa\n"
     "Thank you for using BeginnerScript, Hafsa\n"
     "Thank you for using BeginnerScript, Hafsa\n", ""),

    ("sample program, only one if branch runs", "examples/input.txt", "Ali\n12\n", 0,
     "Enter your name: Ali\n"
     "Enter your age: 12\n"
     "Hello, Ali\n"
     "You are not eligible to vote yet.\n"
     "Welcome to BeginnerScript!\n"
     "Thank you for using BeginnerScript, Ali\n"
     "Thank you for using BeginnerScript, Ali\n"
     "Thank you for using BeginnerScript, Ali\n", ""),

    ("sample with errors reports all of them", "examples/input2.txt", "", 1, "",
     "Syntax error at line 15, column 40: unexpected ']'\n"
     "Lexical error at line 21, column 17: invalid character '$'\n"
     "Syntax error at line 29, column 10: unexpected name 'timez'\n"
     "3 errors found in input2.txt\n"),

    ("while and repeat loops", "examples/loops.txt", "", 0,
     "The sum of 1 to 10 is 55\n"
     "7 x 1 = 7\n7 x 2 = 14\n7 x 3 = 21\n7 x 4 = 28\n7 x 5 = 35\n"
     + "BeginnerScript makes loops easy!\n" * 3, ""),

    ("functions with parameters and recursion", "examples/functions.txt", "Zainab\n", 0,
     "Enter your name: Zainab\n"
     "Welcome to BeginnerScript, Zainab!\n"
     "12 + 30 = 42\n"
     "3\n2\n1\n"
     "Lift off!\n", ""),

    ("nested if / otherwise", "examples/grades.txt", "72\n", 0,
     "Enter your marks (0-100): 72\nGrade B - very good\n", ""),

    ("arithmetic follows * / before + -",
     "display [2 + 3 * 4];\ndisplay [20 - 6 / 2];\ndisplay [10 - 2 - 3];\ndisplay [7 / 2];\n", "", 0,
     "14\n17\n5\n3\n", ""),

    ("empty program and empty blocks",
     "# only comments\nif 1 > 2 then [ ] otherwise [ ]\n", "", 0, "", ""),

    ("missing semicolon gets a hint",
     "store x\nset x = 5;\n", "", 1, "",
     "Syntax error at line 2, column 1: unexpected 'set' (is a ';' missing before it?)\n"
     "1 error found in program.txt\n"),

    ("bad characters, unclosed string and huge number",
     "store x;\nset x = 5 @ 2;\ndisplay [\"oops];\nset x = 99999999999;\n", "", 1, "",
     "Lexical error at line 2, column 11: invalid character '@'\n"
     "Syntax error at line 2, column 13: unexpected number 2\n"
     "Lexical error at line 3, column 10: this string has no closing quote (\")\n"
     "Lexical error at line 4, column 9: number 99999999999 is too large (the largest number is 2147483647)\n"
     "4 errors found in program.txt\n"),

    ("semantic errors",
     "store a;\nstore a;\nset b = 1;\ndisplay [\"hi\" * 2];\nGreet();\n"
     "function greet(name) [ display [name]; ]\ngreet();\n", "", 1, "",
     "Semantic error at line 2, column 1: variable 'a' is already stored at line 1\n"
     "Semantic error at line 3, column 1: variable 'b' is used before it is stored (add: store b;)\n"
     "Semantic error at line 4, column 15: '*' only works with numbers (use + to join text)\n"
     "Semantic error at line 5, column 1: function 'Greet' is not defined (did you mean 'greet'?)\n"
     "Semantic error at line 7, column 1: function 'greet' needs 1 argument but was given 0\n"
     "5 errors found in program.txt\n"),

    ("division by zero stops the program",
     "store x;\nset x = 0;\ndisplay [\"before\"];\ndisplay [10 / x];\ndisplay [\"not shown\"];\n", "", 3,
     "before\n", "Runtime error at line 4, column 13: division by zero\n"),

    ("endless while loop is stopped",
     "store x;\nset x = 1;\nwhile x > 0 [ set x = x + 1; ]\n", "", 3, "",
     "Runtime error at line 3, column 1: this while loop has run 100000 times; "
     "does its condition ever become false?\n"),

    ("missing program input",
     "store n;\ninput \"Number: \" into n;\n", "", 3, "Number: \n",
     "Runtime error at line 2, column 1: no input left for 'n' (type one value per line in the program input)\n"),
]


def build():
    script = os.path.join(ROOT, "build.bat" if os.name == "nt" else "build.sh")
    result = subprocess.run([script], cwd=ROOT, capture_output=True, text=True, shell=os.name == "nt")
    if result.returncode != 0:
        print(result.stdout + result.stderr)
        sys.exit("Build failed")


def run(program_path, stdin):
    result = subprocess.run(["java", "-cp", CLASSPATH, "Main", program_path], cwd=ROOT,
                            input=stdin, capture_output=True, text=True)
    clean = lambda s: "\n".join(l for l in s.replace("\r\n", "\n").split("\n")
                                if not l.startswith("Picked up JAVA_TOOL_OPTIONS"))
    return result.returncode, clean(result.stdout), clean(result.stderr)


def main():
    build()
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, program, stdin, code, out, err in CASES:
            if program.endswith(".txt") and "\n" not in program:
                path = os.path.join(ROOT, program)
            else:
                path = os.path.join(tmp, "program.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(program)
            got = run(path, stdin)
            if got == (code, out, err):
                print("PASS  " + name)
            else:
                failed += 1
                print("FAIL  " + name)
                print("      expected exit %d, got %d" % (code, got[0]))
                for label, want, have in (("stdout", out, got[1]), ("stderr", err, got[2])):
                    if want != have:
                        print("      expected %s:\n%s      got:\n%s" % (label, indent(want), indent(have)))
    print()
    print("%d passed, %d failed" % (len(CASES) - failed, failed))
    sys.exit(1 if failed else 0)


def indent(text):
    return "".join("        | " + line + "\n" for line in text.split("\n"))


if __name__ == "__main__":
    main()
