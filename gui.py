"""
BeginnerScript Compiler Studio

A desktop editor for BeginnerScript programs. It builds the compiler from
scanner.jflex and parser.cup with the bundled JFlex and CUP (in lib/), runs the
program, and shows every compiler phase: tokens, syntax tree, problems and the
program's output.

Run it from the project folder:   python gui.py
Needs: Python 3.8+, customtkinter (pip install customtkinter) and a JDK 11+.
"""
import os
import queue
import re
import shutil
import subprocess
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

import customtkinter as ctk

# ---------------------------------------------------------------- paths

PROJECT = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(PROJECT, "lib")
BUILD = os.path.join(PROJECT, "build")
GEN = os.path.join(BUILD, "gen")
CLASSES = os.path.join(BUILD, "classes")
JFLEX_JAR = os.path.join(LIB, "jflex-full-1.9.1.jar")
CUP_JAR = os.path.join(LIB, "java-cup-11b.jar")
CUP_RUNTIME = os.path.join(LIB, "java-cup-11b-runtime.jar")
COMPILER_SOURCES = ["scanner.jflex", "parser.cup", "Main.java", "Ast.java", "Semantic.java", "Interpreter.java"]
START_PROGRAM = os.path.join(PROJECT, "examples", "input.txt")

RUN_TIMEOUT_SECONDS = 20
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # no console pop-up on Windows

ERROR_LINE = re.compile(r"^(Lexical|Syntax|Semantic|Runtime) error at line (\d+), column (\d+): (.*)$")

KEYWORDS = ("store", "set", "input", "into", "display", "if", "then", "otherwise",
            "repeat", "times", "while", "function")
# Order matters: later patterns are applied on top of earlier ones (a # inside a string is not a comment)
SYNTAX = [
    ("keyword", re.compile(r"\b(" + "|".join(KEYWORDS) + r")\b")),
    ("function", re.compile(r"\b[A-Za-z_]\w*(?=\s*\()")),
    ("number", re.compile(r"\b\d+\b")),
    ("comment", re.compile(r"#[^\n]*")),
    ("string", re.compile(r'"[^"\n]*"?')),
]

# ---------------------------------------------------------------- look

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0f1419",
    "panel": "#1a2332",
    "card": "#243447",
    "editor": "#111a24",
    "text": "#e6edf3",
    "muted": "#8b9bb0",
    "accent": "#9c27b0",
    "green": "#2e9e5b",
    "green_hover": "#24804a",
    "blue": "#2f81f7",
    "red": "#f47067",
    "yellow": "#e3b341",
    "ok": "#56d364",
    "keyword": "#ff7ab2",
    "function": "#79c0ff",
    "number": "#ffa657",
    "string": "#a5d6a7",
    "comment": "#6e7f94",
    "line_numbers": "#4d5d70",
    "error_line": "#3b1d22",
}


def pick_font(candidates, size):
    families = set(tkfont.families())
    for name in candidates:
        if name in families:
            return (name, size)
    return ("Courier", size)


class CompilerStudio:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("BeginnerScript Compiler Studio")
        self.root.geometry("1360x860")
        self.root.minsize(1000, 640)
        self.root.configure(fg_color=COLORS["bg"])

        self.mono = pick_font(["Cascadia Code", "Consolas", "JetBrains Mono", "DejaVu Sans Mono", "Menlo"], 12)
        self.events = queue.Queue()
        self.busy = False

        self._build_layout()
        self._load_start_program()
        self.root.after(50, self._poll_events)
        if shutil.which("java") is None:
            self.set_status("Java was not found. Install a JDK (version 11 or newer) and restart.", "red")

    # ------------------------------------------------------------ layout

    def _build_layout(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self._build_header()

        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(12, 0))
        body.grid_columnconfigure(0, weight=3, uniform="cols")
        body.grid_columnconfigure(1, weight=2, uniform="cols")
        body.grid_rowconfigure(0, weight=1)
        self._build_editor_panel(body)
        self._build_results_panel(body)

        self.status = ctk.CTkLabel(self.root, text="Ready", anchor="w", text_color=COLORS["muted"],
                                   font=ctk.CTkFont(size=12))
        self.status.grid(row=2, column=0, sticky="ew", padx=20, pady=6)

    def _build_header(self):
        header = ctk.CTkFrame(self.root, height=64, corner_radius=0, fg_color=COLORS["panel"])
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        logo = ctk.CTkLabel(header, text="</>", width=40, height=40, corner_radius=10, fg_color=COLORS["accent"],
                            text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
        logo.place(x=20, y=12)
        ctk.CTkLabel(header, text="BeginnerScript Compiler Studio", text_color=COLORS["text"],
                     font=ctk.CTkFont(size=19, weight="bold")).place(x=74, y=8)
        ctk.CTkLabel(header, text="JFlex scanner  >  CUP parser  >  semantic analysis  >  interpreter",
                     text_color=COLORS["muted"], font=ctk.CTkFont(size=12)).place(x=75, y=35)

    def _build_editor_panel(self, body):
        panel = ctk.CTkFrame(body, fg_color=COLORS["panel"], corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(panel, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        self.file_label = ctk.CTkLabel(bar, text="program", text_color=COLORS["text"],
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.file_label.pack(side="left")
        self.run_button = ctk.CTkButton(bar, text="▶  Run", width=96, height=34, corner_radius=8,
                                        fg_color=COLORS["green"], hover_color=COLORS["green_hover"],
                                        font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.start("run"))
        self.run_button.pack(side="right")
        self.check_button = ctk.CTkButton(bar, text="Check", width=80, height=34, corner_radius=8,
                                          fg_color=COLORS["card"], hover_color=COLORS["blue"],
                                          font=ctk.CTkFont(size=13), command=lambda: self.start("check"))
        self.check_button.pack(side="right", padx=8)

        self.editor = self._text_widget(panel, editable=True)
        self.editor.master.grid(row=1, column=0, sticky="nsew", padx=14)
        self._add_line_numbers(self.editor)
        for tag in ("keyword", "function", "number", "comment", "string"):
            self.editor.tag_configure(tag, foreground=COLORS[tag])
        self.editor.tag_configure("error_line", background=COLORS["error_line"])
        self.editor.tag_raise("sel")
        self.editor.bind("<<Modified>>", self._on_edit)

        ctk.CTkLabel(panel, text="Program input  (one value per line, used by input statements)",
                     text_color=COLORS["muted"], font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w",
                                                                                padx=16, pady=(10, 4))
        self.stdin_box = self._text_widget(panel, editable=True, height=3)
        self.stdin_box.master.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

    def _build_results_panel(self, body):
        self.tabs = ctk.CTkTabview(body, fg_color=COLORS["panel"], corner_radius=12,
                                   segmented_button_selected_color=COLORS["accent"],
                                   segmented_button_selected_hover_color=COLORS["accent"])
        self.tabs.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.views = {}
        for name in ("Output", "Problems", "Tokens", "Syntax tree", "Build log"):
            tab = self.tabs.add(name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            view = self._text_widget(tab, editable=False, wrap=name in ("Output", "Problems", "Build log"))
            view.master.grid(row=0, column=0, sticky="nsew")
            self.views[name] = view
        self.tabs.set("Output")
        self._write("Output", "Press Run to compile and run the program.\n", "muted")

    def _text_widget(self, parent, editable, height=None, wrap=False):
        """A dark, monospace tk.Text with scrollbars, inside its own frame."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["editor"], corner_radius=8, height=20)  # size comes from the text
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        text = tk.Text(frame, wrap="word" if wrap else "none", undo=editable, font=self.mono, relief="flat",
                       borderwidth=0, highlightthickness=0, padx=10, pady=8, background=COLORS["editor"],
                       foreground=COLORS["text"], insertbackground=COLORS["text"],
                       selectbackground="#264f78", height=height or 10)
        text.grid(row=0, column=0, sticky="nsew")
        # Small requested sizes: the scrollbars stretch to fit, instead of forcing 200px
        scroll = ctk.CTkScrollbar(frame, command=text.yview, height=20)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 2), pady=2)
        text.configure(yscrollcommand=scroll.set)
        if not wrap and height is None:
            hscroll = ctk.CTkScrollbar(frame, orientation="horizontal", command=text.xview, width=20)
            hscroll.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 2))
            text.configure(xscrollcommand=hscroll.set)
        for tag, color in (("muted", COLORS["muted"]), ("error", COLORS["red"]),
                           ("ok", COLORS["ok"]), ("warn", COLORS["yellow"])):
            text.tag_configure(tag, foreground=color)
        if not editable:
            text.configure(state="disabled")
        return text

    # ------------------------------------------------------------ code editor

    def _add_line_numbers(self, text):
        """A canvas left of the editor that shows the visible line numbers."""
        frame = text.master
        self.gutter = tk.Canvas(frame, width=44, background=COLORS["editor"], highlightthickness=0, borderwidth=0)
        self.gutter.grid(row=0, column=0, sticky="nsw")
        text.grid_configure(padx=(44, 0))
        scroll_set = text.cget("yscrollcommand")

        def on_scroll(first, last):
            self.root.tk.call(scroll_set, first, last)  # keep the scrollbar in step
            self._draw_line_numbers()

        text.configure(yscrollcommand=on_scroll)
        text.bind("<Configure>", lambda e: self._draw_line_numbers(), add=True)

    def _draw_line_numbers(self):
        self.gutter.delete("all")
        index = self.editor.index("@0,0")
        while True:
            info = self.editor.dlineinfo(index)
            if info is None:
                break
            number = index.split(".")[0]
            self.gutter.create_text(36, info[1] + info[3] // 2, anchor="e", text=number,
                                    fill=COLORS["line_numbers"], font=self.mono)
            index = self.editor.index(index + "+1line")
            if self.editor.compare(index, "==", "end"):
                break

    def _on_edit(self, _event=None):
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)
        self.editor.tag_remove("error_line", "1.0", "end")  # old error marks no longer match the text
        if getattr(self, "_highlight_job", None):
            self.root.after_cancel(self._highlight_job)
        self._highlight_job = self.root.after(120, self._highlight)
        self._draw_line_numbers()

    def _highlight(self):
        self._highlight_job = None
        code = self.editor.get("1.0", "end-1c")
        for tag, _ in SYNTAX:
            self.editor.tag_remove(tag, "1.0", "end")
        for tag, pattern in SYNTAX:
            for match in pattern.finditer(code):
                start, end = "1.0+%dc" % match.start(), "1.0+%dc" % match.end()
                if tag in ("comment", "string"):
                    for other, _ in SYNTAX:  # strings and comments win over anything inside them
                        self.editor.tag_remove(other, start, end)
                self.editor.tag_add(tag, start, end)

    def mark_errors(self, problems):
        self.editor.tag_remove("error_line", "1.0", "end")
        for match in problems:
            line = match.group(2)
            self.editor.tag_add("error_line", line + ".0", line + ".0 lineend+1c")

    def go_to(self, line, column):
        index = "%s.%d" % (line, max(int(column) - 1, 0))
        self.editor.mark_set("insert", index)
        self.editor.see(index)
        self.editor.focus_set()

    # ------------------------------------------------------------ helpers

    def _load_start_program(self):
        if os.path.isfile(START_PROGRAM):
            with open(START_PROGRAM, encoding="utf-8") as f:
                self.editor.insert("1.0", f.read())
            self.file_label.configure(text="examples/input.txt")
        self.stdin_box.insert("1.0", "Hafsa\n21")
        self.editor.edit_reset()
        self._highlight()

    def _write(self, view, text, tag=None):
        widget = self.views[view]
        widget.configure(state="normal")
        widget.insert("end", text, tag or ())
        widget.configure(state="disabled")
        widget.see("end")

    def _clear(self, *views):
        for view in views:
            widget = self.views[view]
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="disabled")

    def set_status(self, text, color="muted"):
        self.status.configure(text=text, text_color=COLORS.get(color, color))

    # ------------------------------------------------------------ compile and run

    def start(self, mode):
        """mode is 'run' (compile and run) or 'check' (compile only)."""
        if self.busy:
            return
        if shutil.which("java") is None:
            messagebox.showerror("Java not found", "Install a JDK (Java 11 or newer), then restart Compiler Studio.")
            return
        self.busy = True
        for button in (self.run_button, self.check_button):
            button.configure(state="disabled")
        self._clear("Output", "Problems", "Tokens", "Syntax tree")
        self.set_status("Working...")
        source = self.editor.get("1.0", "end-1c")
        stdin = self.stdin_box.get("1.0", "end-1c")
        if stdin and not stdin.endswith("\n"):
            stdin += "\n"
        threading.Thread(target=self._worker, args=(mode, source, stdin), daemon=True).start()

    def _worker(self, mode, source, stdin):
        """Runs in a background thread. It never touches widgets: it only posts events."""
        try:
            if self._needs_build():
                if not self._build_compiler():
                    self.events.put(("build_failed",))
                    return
            program = os.path.join(BUILD, "program.txt")
            with open(program, "w", encoding="utf-8") as f:
                f.write(source)
            command = ["java", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8",
                       "-cp", os.pathsep.join([CUP_RUNTIME, CLASSES]), "Main", "--tokens", "--tree"]
            if mode == "check":
                command.append("--check")
            result = subprocess.run(command + [program], input=stdin, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", cwd=PROJECT,
                                    timeout=RUN_TIMEOUT_SECONDS, creationflags=NO_WINDOW)
            self.events.put(("result", mode, result.returncode, result.stdout, result.stderr))
        except subprocess.TimeoutExpired:
            self.events.put(("timeout",))
        except Exception as e:  # report anything unexpected instead of failing silently
            self.events.put(("crash", str(e)))

    def _needs_build(self):
        main_class = os.path.join(CLASSES, "Main.class")
        if not os.path.isfile(main_class):
            return True
        built = os.path.getmtime(main_class)
        return any(os.path.getmtime(os.path.join(PROJECT, s)) > built for s in COMPILER_SOURCES)

    def _build_compiler(self):
        os.makedirs(GEN, exist_ok=True)
        os.makedirs(CLASSES, exist_ok=True)
        sources = [os.path.join(PROJECT, s) for s in COMPILER_SOURCES if s.endswith(".java")]
        steps = [
            ("JFlex: scanner.jflex", ["java", "-jar", JFLEX_JAR, "-q", "-d", GEN, "scanner.jflex"]),
            ("CUP: parser.cup", ["java", "-jar", CUP_JAR, "-destdir", GEN, "parser.cup"]),
            ("javac", ["javac", "-nowarn", "-encoding", "UTF-8", "-cp", CUP_RUNTIME, "-d", CLASSES] + sources
             + [os.path.join(GEN, f) for f in ("MyScanner.java", "parser.java", "sym.java")]),
        ]
        self.events.put(("log", "Building the compiler...\n", "muted"))
        for title, command in steps:
            self.events.put(("log", "\n> " + title + "\n", "warn"))
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                    cwd=PROJECT, creationflags=NO_WINDOW)
            output = "\n".join(line for line in (result.stdout + result.stderr).splitlines()
                               if not line.startswith("Picked up JAVA_TOOL_OPTIONS"))
            if output.strip():
                self.events.put(("log", output.rstrip() + "\n", None))
            if result.returncode != 0:
                self.events.put(("log", "\nBuild failed.\n", "error"))
                return False
        self.events.put(("log", "\nBuild OK.\n", "ok"))
        return True

    # ------------------------------------------------------------ results (main thread)

    def _poll_events(self):
        try:
            while True:
                self._handle(self.events.get_nowait())
        except queue.Empty:
            pass
        self.root.after(50, self._poll_events)

    def _handle(self, event):
        kind = event[0]
        if kind == "log":
            self._write("Build log", event[1], event[2])
            return
        if kind == "result":
            self._show_result(*event[1:])
        elif kind == "build_failed":
            self.tabs.set("Build log")
            self.set_status("The compiler could not be built. See the Build log tab.", "red")
        elif kind == "timeout":
            self._write("Output", "\nStopped: the program ran for more than %d seconds.\n" % RUN_TIMEOUT_SECONDS,
                        "error")
            self.tabs.set("Output")
            self.set_status("Stopped after %d seconds" % RUN_TIMEOUT_SECONDS, "red")
        elif kind == "crash":
            self._write("Output", "\nCould not run the compiler: %s\n" % event[1], "error")
            self.set_status("Could not run the compiler", "red")
        self.busy = False
        for button in (self.run_button, self.check_button):
            button.configure(state="normal")

    def _show_result(self, mode, code, stdout, stderr):
        sections = {"tokens": [], "tree": [], "output": [], "other": []}
        current = "other"
        markers = {"=== Tokens ===": "tokens", "=== Syntax tree ===": "tree", "=== Program output ===": "output"}
        for line in stdout.splitlines(keepends=True):
            if line.strip() in markers:
                current = markers[line.strip()]
            elif line.startswith("No errors found in "):
                sections["other"].append("No errors found.\n")  # printed by --check
            else:
                sections[current].append(line)

        self._write("Tokens", "".join(sections["tokens"]) or "No tokens.\n")
        self._write("Syntax tree", "".join(sections["tree"]) or "No syntax tree (the program has errors).\n",
                    None if sections["tree"] else "muted")

        problems = []
        for line in stderr.splitlines():
            match = ERROR_LINE.match(line)
            if match:
                problems.append(match)
            elif re.match(r"^\d+ errors? found in ", line):
                continue  # the status bar shows the count
            elif line.strip() and not line.startswith("Picked up JAVA_TOOL_OPTIONS"):
                self._write("Problems", line + "\n", "muted")
        view = self.views["Problems"]
        for number, match in enumerate(problems):
            kind, line, column, message = match.groups()
            link = "problem%d" % number  # click a problem to jump to its line in the editor
            self._write("Problems", "%s error  line %s, col %s\n" % (kind, line, column), ("error", link))
            self._write("Problems", "    %s\n\n" % message, link)
            view.tag_bind(link, "<Button-1>", lambda e, l=line, c=column: self.go_to(l, c))
            view.tag_bind(link, "<Enter>", lambda e: view.configure(cursor="hand2"))
            view.tag_bind(link, "<Leave>", lambda e: view.configure(cursor=""))
        self.mark_errors(problems)

        output = "".join(sections["output"] + sections["other"])
        if output:
            self._write("Output", output)
        runtime = [m for m in problems if m.group(1) == "Runtime"]
        if runtime:
            self._write("Output", "\n" + runtime[0].group(0) + "\n", "error")

        compile_errors = len(problems) - len(runtime)
        if compile_errors:
            self.tabs.set("Problems")
            self.set_status("%d %s found" % (compile_errors, "problem" if compile_errors == 1 else "problems"), "red")
        elif runtime:
            self.tabs.set("Output")
            self.set_status("Runtime error on line %s" % runtime[0].group(2), "red")
        elif code != 0:
            self.tabs.set("Problems")
            self.set_status("The compiler stopped with exit code %d" % code, "red")
        else:
            self._write("Problems", "No problems found.\n", "ok")
            self.tabs.set("Output")
            self.set_status("No errors found" if mode == "check" else "Program finished", "ok")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CompilerStudio().run()
