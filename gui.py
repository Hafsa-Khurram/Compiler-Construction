import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import subprocess
import os
import shutil


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernCompilerInterface:
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("BeginnerScript Compiler Studio")
        self.root.geometry("1400x900")
        self.root.configure(fg_color="#0f1419")

        # Modern color palette inspired by the reference
        self.colors = {
            "bg_primary": "#0f1419",
            "bg_secondary": "#1a2332",
            "bg_tertiary": "#243447",
            "bg_card": "#2a3f5f",
            "accent_pink": "#ff4081",
            "accent_cyan": "#00bcd4",
            "accent_green": "#4caf50",
            "accent_blue": "#2196f3",
            "accent_purple": "#9c27b0",
            "text_primary": "#ffffff",
            "text_secondary": "#b0bec5",
            "text_muted": "#78909c"
        }

        # Current theme
        self.current_theme = "Neural"

        # File status
        self.file_status = {
            "Scanner": {"selected": False, "path": ""},
            "Parser": {"selected": False, "path": ""},
            "Input": {"selected": False, "path": ""}
        }

        # Compilation step tracking
        self.compilation_step = 0

        # Initialize UI components
        self.input_textbox = None  # Will be initialized later

        self.setup_ui()

    def setup_ui(self):
        # Create header
        self.create_header()

        # Create main container
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["bg_primary"],
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Create sidebar and main content
        self.create_sidebar()
        self.create_console_area()

    def create_header(self):
        # Header frame
        header_frame = ctk.CTkFrame(
            self.root,
            height=70,
            fg_color=self.colors["bg_secondary"],
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Left side - Logo and title
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=15)

        # Logo
        logo_frame = ctk.CTkFrame(
            left_frame,
            width=40,
            height=40,
            fg_color=self.colors["accent_purple"],
            corner_radius=10
        )
        logo_frame.pack(side="left", padx=(0, 15))
        logo_frame.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="</>",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        logo_label.pack(expand=True)

        # Title section
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")

        title_label = ctk.CTkLabel(
            title_frame,
            text="BeginnerScript Compiler Studio",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Modern compiler interface with beautiful themes",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        subtitle_label.pack(anchor="w")

        # Right side - Theme buttons
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=15)

        # Theme label
        theme_label = ctk.CTkLabel(
            right_frame,
            text="Theme:",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        theme_label.pack(side="left", padx=(0, 10))

        # Theme buttons
        themes = [
            ("Neural", self.colors["accent_blue"]),
            ("Cyber", self.colors["accent_pink"]),
            ("Matrix", self.colors["accent_green"])
        ]
        for theme_name, color in themes:
            is_active = theme_name == self.current_theme
            btn = ctk.CTkButton(
                right_frame,
                text=theme_name,
                width=70,
                height=35,
                fg_color=color if is_active else self.colors["bg_tertiary"],
                hover_color=color,
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                corner_radius=8,
                command=lambda t=theme_name, c=color: self.change_theme(t, c)
            )
            btn.pack(side="left", padx=2)
    
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=320,
            fg_color=self.colors["bg_secondary"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # File Operations section
        self.create_file_operations()

        # File Status section
        self.create_file_status()

        # Quick Actions section
        self.create_quick_actions()

    def create_file_operations(self):
        # File Operations Header
        ops_header = ctk.CTkLabel(
            self.sidebar,
            text="FILE OPERATIONS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        ops_header.pack(anchor="w", padx=20, pady=(20, 15))

        # File type buttons with modern styling
        file_buttons = [
            ("Scanner File", ".jflex", self.colors["accent_pink"], "Scanner"),
            ("Parser File", ".cup", self.colors["accent_blue"], "Parser"),
        ]
        for text, ext, color, file_type in file_buttons:
            # Button frame
            btn_frame = ctk.CTkFrame(
                self.sidebar,
                fg_color=color,
                corner_radius=12,
                height=60
            )
            btn_frame.pack(fill="x", padx=20, pady=5)
            btn_frame.pack_propagate(False)

            # Make it clickable
            btn_frame.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

            # Also make child widgets clickable
            content_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
            # 8px top/bottom padding leaves room for both the name and the extension line
            content_frame.pack(fill="both", expand=True, padx=15, pady=8)
            content_frame.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

            # File icon
            icon_map = {"Scanner": "📄", "Parser": "⚙"}
            icon_label = ctk.CTkLabel(
                content_frame,
                text=icon_map[file_type],
                font=ctk.CTkFont(size=20),
                text_color="white"
            )
            icon_label.pack(side="left")
            icon_label.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

            # Text content
            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
            text_frame.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

            name_label = ctk.CTkLabel(
                text_frame,
                text=text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",
                cursor="hand2"
            )
            name_label.pack(anchor="w")
            name_label.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

            ext_label = ctk.CTkLabel(
                text_frame,
                text=ext,
                font=ctk.CTkFont(size=11),
                text_color="white",
                cursor="hand2"
            )
            ext_label.pack(anchor="w")
            ext_label.bind("<Button-1>", lambda e, ft=file_type: self.select_file(ft))

    def create_file_status(self):
        # File Status Header
        status_header = ctk.CTkLabel(
            self.sidebar,
            text="FILE STATUS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        status_header.pack(anchor="w", padx=20, pady=(30, 15))

        # Status container
        self.status_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["bg_tertiary"],
            corner_radius=12
        )
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Status items
        self.status_labels = {}
        for file_type in ["Scanner", "Parser"]:
            # Status item frame
            item_frame = ctk.CTkFrame(
                self.status_frame,
                fg_color="transparent"
            )
            item_frame.pack(fill="x", padx=15, pady=8)

            # File type label
            type_label = ctk.CTkLabel(
                item_frame,
                text=f"{file_type}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_primary"]
            )
            type_label.pack(side="left")

            # Status label
            status_label = ctk.CTkLabel(
                item_frame,
                text="❌ Not selected",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_muted"]
            )
            status_label.pack(side="right")
            self.status_labels[file_type] = status_label

    def create_quick_actions(self):
        # Quick Actions Header
        actions_header = ctk.CTkLabel(
            self.sidebar,
            text="QUICK ACTIONS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        actions_header.pack(anchor="w", padx=20, pady=(20, 15))

        # Compile button
        compile_btn = ctk.CTkButton(
            self.sidebar,
            text="🚀 Start Compilation",
            width=280,
            height=50,
            fg_color=self.colors["accent_green"],
            hover_color=self.adjust_color_brightness(self.colors["accent_green"], 0.8),
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            command=self.start_compilation
        )
        compile_btn.pack(padx=20, pady=5)

        # Action buttons row
        btn_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=10)

        clear_btn = ctk.CTkButton(
            btn_row,
            text="🧹 Clear",
            width=130,
            height=40,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["accent_pink"],
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            command=self.clear_console
        )
        clear_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_row,
            text="💾 Save",
            width=130,
            height=40,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["accent_blue"],
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            command=self.save_project
        )
        save_btn.pack(side="right")

    def create_console_area(self):
        # Console container
        console_container = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors["bg_primary"],
            corner_radius=0
        )
        console_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Console header
        console_header = ctk.CTkFrame(
            console_container,
            height=60,
            fg_color=self.colors["bg_card"],
            corner_radius=12
        )
        console_header.pack(fill="x", pady=(0, 15))
        console_header.pack_propagate(False)

        # Console title
        title_label = ctk.CTkLabel(
            console_header,
            text="📟 Console Output",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Live indicator
        live_frame = ctk.CTkFrame(
            console_header,
            fg_color=self.colors["accent_green"],
            corner_radius=12
        )
        live_frame.pack(side="right", padx=20, pady=15)

        live_label = ctk.CTkLabel(
            live_frame,
            text="🟢 Live",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white"
        )
        live_label.pack(padx=12, pady=6)

        # Console output area
        self.console_frame = ctk.CTkScrollableFrame(
            console_container,
            fg_color=self.colors["bg_card"],
            corner_radius=12
        )
        self.console_frame.pack(fill="both", expand=True)

        # Add input text box at the bottom
        input_label = ctk.CTkLabel(
            console_container,
            text="📝 Type your input below:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        input_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.input_textbox = ctk.CTkTextbox(
            console_container,
            height=100,
            fg_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.input_textbox.pack(fill="x", padx=20, pady=(0, 10))

        # Add initial console content
        self.add_welcome_message()

    def add_welcome_message(self):
        welcome_text = ctk.CTkLabel(
            self.console_frame,
            text="✨ Welcome to BeginnerScript Compiler Studio!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        welcome_text.pack(anchor="w", padx=20, pady=(20, 5))

        system_text = ctk.CTkLabel(
            self.console_frame,
            text="🧠 SYSTEM INITIALIZED - NEURAL NETWORK READY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["accent_green"]
        )
        system_text.pack(anchor="w", padx=20, pady=5)

        instructions = [
            "🎯 Ready to compile your language files with style and precision.",
            "📂 Select your files using the sidebar to get started.",
            f"🎨 Current theme: {self.current_theme}",
            "",
            "🚀 Compilation Process:",
            "• Select Scanner file (.jflex) - Generates lexical analyzer",
            "• Select Parser file (.cup) - Generates syntax analyzer",
            "• Type your input directly below",
            "• Click 'Start Compilation' for full processing",
            "",
            "💡 Pro tip: Try different themes to customize your experience!",
            "",
            "Let's build something amazing together! 🚀"
        ]

        for instruction in instructions:
            if instruction == "":
                spacer = ctk.CTkLabel(self.console_frame, text="", height=10)
                spacer.pack()
            elif instruction.startswith("🚀 Compilation Process:"):
                feature_label = ctk.CTkLabel(
                    self.console_frame,
                    text=instruction,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["text_primary"]
                )
                feature_label.pack(anchor="w", padx=20, pady=(10, 5))
            elif instruction.startswith("•"):
                feature_label = ctk.CTkLabel(
                    self.console_frame,
                    text=instruction,
                    font=ctk.CTkFont(size=13),
                    text_color=self.colors["text_secondary"]
                )
                feature_label.pack(anchor="w", padx=40, pady=2)
            elif instruction.startswith("Let's build"):
                final_label = ctk.CTkLabel(
                    self.console_frame,
                    text=instruction,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["accent_cyan"]
                )
                final_label.pack(anchor="w", padx=20, pady=(10, 30))
            else:
                inst_label = ctk.CTkLabel(
                    self.console_frame,
                    text=instruction,
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["text_secondary"]
                )
                inst_label.pack(anchor="w", padx=20, pady=3)

    def run_cmd(self, command):
        """Execute command and display output in real-time"""
        self.add_console_message(f"▶ Running: {command}", self.colors["accent_cyan"])
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                universal_newlines=True
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.add_console_message(output.strip(), self.colors["text_secondary"])
                    self.root.update()
            return_code = process.poll()
            if return_code == 0:
                self.add_console_message(f"✅ Command completed successfully", self.colors["accent_green"])
            else:
                self.add_console_message(f"❌ Command failed with return code: {return_code}", self.colors["accent_pink"])
        except Exception as e:
            self.add_console_message(f"❌ Error executing command: {str(e)}", self.colors["accent_pink"])

    def copy_if_needed(self, path):
        """Copy file to current directory if needed"""
        filename = os.path.basename(path)
        dest_path = os.path.abspath(filename)
        if os.path.abspath(path) != dest_path:
            try:
                shutil.copy(path, dest_path)
                self.add_console_message(f"📋 Copied {filename} to working directory", self.colors["accent_blue"])
                return filename
            except Exception as e:
                self.add_console_message(f"❌ Error copying file: {str(e)}", self.colors["accent_pink"])
                return None
        return filename

    def select_file(self, file_type):
        # Skip input file selection
        if file_type == "Input":
            self.add_console_message("💡 Input is now typed directly into the editor.", self.colors["text_muted"])
            return

        # File type extensions
        extensions = {
            "Scanner": [("JFlex files", "*.jflex"), ("All files", "*.*")],
            "Parser": [("CUP files", "*.cup"), ("All files", "*.*")]
        }
        filename = filedialog.askopenfilename(
            title=f"Select {file_type} File",
            filetypes=extensions[file_type]
        )
        if filename:
            self.file_status[file_type]["selected"] = True
            self.file_status[file_type]["path"] = filename
            self.status_labels[file_type].configure(
                text="✅ Selected",
                text_color=self.colors["accent_green"]
            )
            self.add_console_message(f"📁 {file_type} file selected: {os.path.basename(filename)}")

            # Process file immediately based on type
            if file_type == "Scanner":
                self.process_scanner_file(filename)
            elif file_type == "Parser":
                self.process_parser_file(filename)

    def process_scanner_file(self, path):
        self.add_console_message("🔍 Processing Scanner file...", self.colors["accent_pink"])
        def process():
            filename = self.copy_if_needed(path)
            if filename:
                self.run_cmd(f"jflex {filename}")
        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def process_parser_file(self, path):
        self.add_console_message("⚙ Processing Parser file...", self.colors["accent_blue"])
        def process():
            filename = self.copy_if_needed(path)
            if filename:
                self.run_cmd(f"java java_cup.MainDrawTree {filename}")
        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def process_input_file(self):
        self.add_console_message("📝 Saving typed input...", self.colors["accent_green"])
        content = self.input_textbox.get("1.0", "end-1c")
        filename = "user_input.txt"
        try:
            with open(filename, 'w') as f:
                f.write(content)
            self.add_console_message(f"💾 Created input file: {filename}", self.colors["accent_blue"])
            self.file_status["Input"]["selected"] = True
            self.file_status["Input"]["path"] = os.path.abspath(filename)
        except Exception as e:
            self.add_console_message(f"❌ Error saving input: {str(e)}", self.colors["accent_pink"])

    def start_compilation(self):
        missing_files = [ft for ft in ["Scanner", "Parser"] if not self.file_status[ft]["selected"]]
        if missing_files:
            messagebox.showwarning("Missing Files", f"Please select: {', '.join(missing_files)}")
            return

        self.add_console_message("🚀 Starting full compilation process...", self.colors["accent_purple"])

        def full_compile_process():
            try:
                scanner_path = self.file_status["Scanner"]["path"]
                self.add_console_message("Step 1: Processing Scanner file...", self.colors["accent_pink"])
                scanner_filename = self.copy_if_needed(scanner_path)
                if scanner_filename:
                    self.run_cmd(f"jflex {scanner_filename}")

                parser_path = self.file_status["Parser"]["path"]
                self.add_console_message("Step 2: Processing Parser file...", self.colors["accent_blue"])
                parser_filename = self.copy_if_needed(parser_path)
                if parser_filename:
                    self.run_cmd(f"java java_cup.MainDrawTree {parser_filename}")

                self.add_console_message("Step 3: Compiling Java files...", self.colors["accent_cyan"])
                self.run_cmd("javac *.java")

                self.add_console_message("Step 4: Saving and running with typed input...", self.colors["accent_green"])
                self.process_input_file()
                input_filename = self.file_status["Input"]["path"]
                if input_filename:
                    self.run_cmd(f"java Main {os.path.basename(input_filename)}")

                self.add_console_message("🎉 Full compilation process completed!", self.colors["accent_purple"])
            except Exception as e:
                self.add_console_message(f"❌ Compilation error: {str(e)}", self.colors["accent_pink"])

        thread = threading.Thread(target=full_compile_process, daemon=True)
        thread.start()

    def clear_console(self):
        for widget in self.console_frame.winfo_children():
            widget.destroy()
        self.add_welcome_message()

    def save_project(self):
        self.add_console_message("💾 Project configuration saved successfully!", self.colors["accent_blue"])

    def add_console_message(self, message, color=None):
        if color is None:
            color = self.colors["text_secondary"]
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        msg_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        msg_frame.pack(fill="x", padx=20, pady=1)
        time_label = ctk.CTkLabel(
            msg_frame,
            text=f"[{timestamp}]",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_muted"]
        )
        time_label.pack(side="left", padx=(0, 10))
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=color
        )
        msg_label.pack(side="left", anchor="w")
        self.root.after(100, lambda: self.console_frame._parent_canvas.yview_moveto(1.0))

    def change_theme(self, theme_name, color):
        self.current_theme = theme_name
        self.add_console_message(f"🎨 Theme changed to: {theme_name}", color)

    def adjust_color_brightness(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        rgb = tuple(min(255, max(0, c)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def run(self):
        self.root.mainloop()


# Create and run the application
if __name__ == "__main__":
    app = ModernCompilerInterface()
    app.run()