import os
import sys
import shutil
import subprocess
import json
import hashlib
import zipfile
import threading
import queue
import webbrowser
import requests
import stat
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
from PIL import Image

# ==========================================
# GLOBAL PATH FIX (LINUX/WINDOWS)
# ==========================================
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(os.path.realpath(sys.executable))
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# ESQUEMA DE CORES DINÂMICAS (Light, Dark)
# ==========================================
BG_APP = ("#FFFFFF", "#141414")   
BG_FRAME = ("#F3F4F6", "#1f1f1f")    
BG_INPUT = ("#E5E7EB", "#2e2e2e")     
COLOR_BORDER = ("#9CA3AF", "#404040") 
BTN_HOVER = ("#D1D5DB", "#404040") 
TEXT_MAIN = ("#111827", "#e0e0e0")
TEXT_MUTED = ("#6B7280", "#8a8a8a")    
ORANGE_MAIN = ("#d35400", "#d35400")   
ORANGE_HOVER = ("#e67e22", "#e67e22")  

# ==========================================
# EXTENSÕES (SETS)
# ==========================================

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.mpg', '.mpeg',
    '.m4v', '.3gp', '.3g2', '.ts', '.mts', '.m2ts', '.vob', '.ogv', '.rm',
    '.rmvb', '.asf', '.divx', '.f4v', '.h264', '.hevc', '.vp9', '.amv',
    '.srt'
}

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.tif',
    '.ico', '.heic', '.heif', '.raw', '.cr2', '.nef', '.orf', '.sr2',
    '.psd', '.ai', '.eps', '.indd', '.jfif', '.pjpeg', '.pjp'
}

AUDIO_EXTENSIONS = {
    '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', '.alac',
    '.aiff', '.ape', '.opus', '.mid', '.midi', '.amr', '.ac3', '.dts',
    '.ra'
}

DOCUMENT_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt', '.ott',
    '.xlsx', '.xls', '.csv', '.ods',
    '.ppt', '.pptx', '.odp',
    '.md', '.log', '.tex', '.wpd',
    '.html', '.mhtml', '.htm', '.msg', '.eml', '.pst'
}

ARCHIVE_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz', '.lzma',
    '.cab', '.iso', '.arj', '.z', '.tgz', '.tbz2', '.txz'
}

EXECUTABLE_EXTENSIONS = {
    '.exe', '.msi', '.apk', '.app', '.bin', '.run', '.jar'
}

CODE_EXTENSIONS = {
    # Scripts e Automação
    '.bat', '.cmd', '.sh', '.bash', '.zsh', '.ps1', '.vbs', '.wsf',
    # Python
    '.py', '.pyc', '.ipynb', '.whl',
    # Web (Front/Back)
    '.css', '.js', '.jsx', '.ts', '.tsx', '.php', '.cgi', '.pl',
    # Outras Linguagens
    '.c', '.cpp', '.cs', '.java', '.kt', '.swift', '.go', '.rs', '.rb',
    # Dados e Configurações
    '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.env', '.sql', 
    '.reg'
}

# ==========================================
# DICIONÁRIO DE TRADUÇÕES (LOCALIZATION)
# ==========================================
LANGS = {
    "en": {
        "title": "Zarfolder", "sub": "Smart File Management", "settings": "⚙ Settings", "about": "ℹ About",
        "s1": "1. Select Folder to Organize", "browse": "Browse", "ph_src": "Choose the messy folder...",
        "s2": "2. Automatic Classification (Check to enable)",
        "t_type": "Type (Videos, Music...)", "t_date_c": "Creation Date", "t_date_m": "Modified Date", "t_size": "Size (Small, Med...)", "t_name": "Name (A-Z)", 
        "s3": "3. Define Organization Rules (Optional)", "add_rule": "+ Add Rule",
        "btn_run": "▶ Organize", "btn_sim": "Simulate (Dry Run)", "btn_undo": "Undo Last", "btn_dupes": "Find Dupes",
        "r_name": "Name contains", "r_name_not": "Name does NOT contain", 
        "r_name_starts": "Name starts with", "r_name_ends": "Name ends with", "r_name_exact": "Name is exactly",
        "r_ext": "Extension is", "r_ext_not": "Extension is NOT", 
        "r_size_gt": "Size > (MB)", "r_size_lt": "Size < (MB)", 
        "r_date_c": "Created before (YYYY-MM-DD)", "r_date_c_after": "Created after (YYYY-MM-DD)", "r_date_c_exact": "Created exactly on (YYYY-MM-DD)",
        "r_date_m": "Modified before (YYYY-MM-DD)", "r_date_m_after": "Modified after (YYYY-MM-DD)", "r_date_m_exact": "Modified exactly on (YYYY-MM-DD)",
        "folder": "➡ Folder:", "ph_dest": "e.g. Docs",
        "ph_name": "e.g. report", "ph_ext": "e.g. .mp4", "ph_size": "e.g. 500", "ph_date": "e.g. 2024-01-01",
        "msg_success": "Organization complete! Moved {} files.", 
        "msg_dupes": "Duplicate scan complete! Moved {} duplicates.", 
        "msg_undo": "Undo successful! Restored {} files.",
        "desc": "The ultimate cross-platform file organizer. Organize your files and folders in seconds with smart rules, hybrid conditions, and automated classification.",
        "btn_update": "Check for updates",
        "load_title": "Processing...", "load_org": "Organizing your files...\nPlease wait.", "load_dupes": "Scanning for duplicates...\nThis may take a while.",
        "load_sim": "Simulating organization...\nPlease wait.", "load_undo": "Restoring files...\nPlease wait."
    }
}

try:
    sys.path.insert(0, os.path.join(base_dir, "bin"))
    import translations
    LANGS.update(translations.EXTRA_LANGS)
except Exception as e:
    print(f"Warning: Could not load translations.py: {e}")

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config_file = os.path.join(base_dir, "bin", "z_config.json")
        self.undo_file = os.path.join(base_dir, "bin", "z_undo_log.json")
        self.version_file = os.path.join(base_dir, "bin", "version.txt")
        self.current_lang = "en"
        self.current_theme = "Light"
        
        self.version = self.get_local_version()
        self.is_updating = False
        self.loading_window = None 
        self.operation_running = False
        self.SIMULATION_PREVIEW_LIMIT = 5000
        self.ui_queue = queue.Queue() 
        
        self.load_config()
        ctk.set_appearance_mode(self.current_theme)

        self.title("Zarfolder")
        self.center_window(self, 850, 670)
        self.minsize(850, 670)
        self.resizable(True, True)
        self.configure(fg_color=BG_APP)
        self.is_windows = os.name == 'nt'
        self.apply_window_icon(self)

        # ===================================================
        # [LINUX/MAC FIX] DETECÇÃO DE SISTEMA OPERACIONAL
        # ===================================================
        self.linux_dialog_tool = None
        if not self.is_windows:
            desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            # Se for KDE Plasma, a prioridade absoluta é o Kdialog (Abre instantaneamente)
            if "kde" in desktop and shutil.which("kdialog"):
                self.linux_dialog_tool = "kdialog"
            # Se for GNOME/Outros, a prioridade é o Zenity
            elif shutil.which("zenity"):
                self.linux_dialog_tool = "zenity"
            elif shutil.which("kdialog"):
                self.linux_dialog_tool = "kdialog"
            else:
                self.linux_dialog_tool = "tkinter"
        
        self.source_folder = ctk.StringVar(value="")
        self.rules = []
        self.MAX_RULES = 15 # Aumentei um pouco para Power Users

        self.chk_type_var = ctk.BooleanVar(value=False)
        self.chk_date_c_var = ctk.BooleanVar(value=False)
        self.chk_date_m_var = ctk.BooleanVar(value=False)
        self.chk_size_var = ctk.BooleanVar(value=False)
        self.chk_name_var = ctk.BooleanVar(value=False)

        self.build_ui()
        self.update_texts() 
        self.process_ui_queue()
        
        if not self.is_windows:
            self.bind_all("<Button-4>", lambda e: e.widget.event_generate("<MouseWheel>", delta=1))
            self.bind_all("<Button-5>", lambda e: e.widget.event_generate("<MouseWheel>", delta=-1))
        
    # ==========================================
    # UTILITÁRIOS BASE E CARREGAMENTO
    # ==========================================
    def center_window(self, win, width, height):
        win.update_idletasks()
        x = int((win.winfo_screenwidth() / 2) - (width / 2))
        y = int((win.winfo_screenheight() / 2) - (height / 2))
        win.geometry(f"{width}x{height}+{x}+{y}")
    
    def apply_window_icon(self, window):
        if self.is_windows:
            # 1. Ícone do Windows
            icon_path = os.path.join(base_dir, "bin", "icon.ico").replace("\\", "/")
            if os.path.exists(icon_path):
                try: 
                    window.after(200, lambda: window.iconbitmap(icon_path))
                except Exception as e: 
                    print(f"Warning: Failed to load icon.ico: {e}")
        else:
            # 2. Ícone do Linux/Mac
            icon_path = os.path.join(base_dir, "bin", "icon.png").replace("\\", "/")
            if os.path.exists(icon_path):
                try: 
                    from tkinter import PhotoImage
                    img_tk = PhotoImage(file=icon_path)
                    window.after(200, lambda: window.iconphoto(False, img_tk))
                except Exception as e: 
                    print(f"Warning: Failed to load icon.png: {e}")
    
    def apply_modal_fix(self, modal_win):
        def on_unmap(e):
            try:
                if e.widget is self and modal_win.winfo_exists():
                    modal_win.grab_release()
            except tk.TclError:
                pass

        def on_map(e):
            try:
                if e.widget is self and modal_win.winfo_exists():
                    modal_win.grab_set()
            except tk.TclError:
                pass

        id_unmap = self.bind("<Unmap>", on_unmap, add="+")
        id_map = self.bind("<Map>", on_map, add="+")

        def on_destroy(e):
            if e.widget is modal_win:
                try:
                    self.unbind("<Unmap>", id_unmap)
                    self.unbind("<Map>", id_map)
                except tk.TclError:
                    pass

        modal_win.bind("<Destroy>", on_destroy, add="+")
    
    def safe_ui(self, func, *args, **kwargs):
        self.ui_queue.put((func, args, kwargs))

    def process_ui_queue(self):
        try:
            while True:
                func, args, kwargs = self.ui_queue.get_nowait()
                try:
                    if self.winfo_exists():
                        func(*args, **kwargs)
                except tk.TclError:
                    pass
        except queue.Empty:
            pass

        try:
            if self.winfo_exists():
                self.after(50, self.process_ui_queue)
        except tk.TclError:
            pass

    def begin_operation(self):
        if self.operation_running:
            messagebox.showwarning("Warning", "Another operation is already running.")
            return False
        self.operation_running = True
        return True

    def finish_operation(self):
        self.operation_running = False
        self.hide_loading()

    def show_loading(self, title_key, message_key):
        t = LANGS[self.current_lang]
        self.loading_window = ctk.CTkToplevel(self)
        self.apply_window_icon(self.loading_window)
        self.loading_window.title(t[title_key])
        self.center_window(self.loading_window, 350, 150)
        self.loading_window.resizable(False, False)
        self.loading_window.configure(fg_color=BG_APP)
        
        self.loading_window.update_idletasks()
        self.loading_window.transient(self)
        self.loading_window.grab_set()
        self.apply_modal_fix(self.loading_window)

        lbl = ctk.CTkLabel(self.loading_window, text=t[message_key], font=("Segoe UI", 14), text_color=TEXT_MAIN)
        lbl.pack(pady=(30, 15))
        
        pb = ctk.CTkProgressBar(self.loading_window, mode="indeterminate", progress_color=ORANGE_MAIN, fg_color=BG_INPUT)
        pb.pack(fill="x", padx=40)
        pb.start()

    def hide_loading(self):
        win = self.loading_window
        self.loading_window = None
        if win and win.winfo_exists():
            win.grab_release()
            win.withdraw() 
            self.after(500, lambda: win.destroy() if win.winfo_exists() else None) 

    def get_local_version(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, "r", encoding='utf-8') as f: 
                    return f.read().strip()
            except: pass
        return "Unknown"

    def build_ui(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        logo_path = os.path.join(base_dir, "bin", "logo.png")
        
        if os.path.exists(logo_path):
            try:
                img_data = Image.open(logo_path)
                self.logo_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(32, 32))
                ctk.CTkLabel(title_frame, image=self.logo_img, text="").pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Warning: Failed to load logo.png: {e}")

        self.lbl_title = ctk.CTkLabel(title_frame, text="", font=("Segoe UI", 20, "bold"), text_color=ORANGE_MAIN)
        self.lbl_title.pack(side="left")
        self.lbl_sub = ctk.CTkLabel(title_frame, text="", font=("Segoe UI", 12), text_color=TEXT_MUTED)
        self.lbl_sub.pack(side="left", padx=(10, 0), pady=(10, 0))

        self.btn_settings = ctk.CTkButton(title_frame, text="", width=100, height=35, corner_radius=10, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.show_settings)
        self.btn_settings.pack(side="right")
        
        self.btn_about = ctk.CTkButton(title_frame, text="", width=100, height=35, corner_radius=10, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.show_about)
        self.btn_about.pack(side="right", padx=(0, 10))

        top_frame = ctk.CTkFrame(self, fg_color=BG_FRAME, corner_radius=15)
        top_frame.pack(fill="x", padx=30, pady=(20, 15))
        
        self.lbl_s1 = ctk.CTkLabel(top_frame, text="", font=("Segoe UI", 15), text_color=TEXT_MAIN)
        self.lbl_s1.pack(anchor="w", padx=20, pady=(15, 5))
        
        src_inner_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        src_inner_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_source = ctk.CTkEntry(src_inner_frame, textvariable=self.source_folder, height=38, fg_color=BG_APP, text_color=TEXT_MAIN, border_width=1, border_color=COLOR_BORDER)
        self.entry_source.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(src_inner_frame, text="", width=80, height=38, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.browse_source)
        self.btn_browse.pack(side="right")

        auto_frame = ctk.CTkFrame(self, fg_color=BG_FRAME, corner_radius=15)
        auto_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        self.lbl_s2 = ctk.CTkLabel(auto_frame, text="", font=("Segoe UI", 15), text_color=TEXT_MAIN)
        self.lbl_s2.pack(anchor="w", padx=20, pady=(15, 5))
        
        chk_inner_frame = ctk.CTkFrame(auto_frame, fg_color="transparent")
        chk_inner_frame.pack(fill="x", padx=20, pady=(0, 15))

        chk_style = {"fg_color": ORANGE_MAIN, "hover_color": ORANGE_HOVER, "border_color": COLOR_BORDER, "text_color": TEXT_MAIN}

        self.chk_type = ctk.CTkCheckBox(chk_inner_frame, text="", variable=self.chk_type_var, **chk_style)
        self.chk_type.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=5)
        
        self.chk_date_c = ctk.CTkCheckBox(chk_inner_frame, text="", variable=self.chk_date_c_var, **chk_style)
        self.chk_date_c.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)
        
        self.chk_date_m = ctk.CTkCheckBox(chk_inner_frame, text="", variable=self.chk_date_m_var, **chk_style)
        self.chk_date_m.grid(row=0, column=2, sticky="w", padx=(0, 20), pady=5)

        self.chk_size = ctk.CTkCheckBox(chk_inner_frame, text="", variable=self.chk_size_var, **chk_style)
        self.chk_size.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=5)
        
        self.chk_name = ctk.CTkCheckBox(chk_inner_frame, text="", variable=self.chk_name_var, **chk_style)
        self.chk_name.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=5)

        self.rules_scroll = ctk.CTkScrollableFrame(self, fg_color=BG_FRAME, corner_radius=15)
        self.rules_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        header_rules_frame = ctk.CTkFrame(self.rules_scroll, fg_color="transparent")
        header_rules_frame.pack(fill="x", pady=(5, 10), padx=5)

        self.lbl_s3 = ctk.CTkLabel(header_rules_frame, text="", font=("Segoe UI", 15), text_color=TEXT_MAIN)
        self.lbl_s3.pack(side="left")
        
        self.btn_add_rule = ctk.CTkButton(header_rules_frame, text="", width=100, height=30, corner_radius=8, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.add_rule_row)
        self.btn_add_rule.pack(side="right")

        self.rules_container = ctk.CTkFrame(self.rules_scroll, fg_color="transparent")
        self.rules_container.pack(fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        self.btn_dupes = ctk.CTkButton(bottom_frame, text="", height=45, corner_radius=10, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.start_find_duplicates)
        self.btn_dupes.pack(side="left", padx=(0, 10))

        self.btn_undo = ctk.CTkButton(bottom_frame, text="", height=45, corner_radius=10, fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=self.start_undo_last_action)
        self.btn_undo.pack(side="left")

        self.btn_run = ctk.CTkButton(bottom_frame, text="", width=160, height=45, corner_radius=10, font=("Segoe UI", 14, "bold"), fg_color=ORANGE_MAIN, hover_color=ORANGE_HOVER, command=lambda: self.start_execute_rules(simulate=False))
        self.btn_run.pack(side="right")

        self.btn_sim = ctk.CTkButton(bottom_frame, text="", width=120, height=45, corner_radius=10, font=("Segoe UI", 14), fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, command=lambda: self.start_execute_rules(simulate=True))
        self.btn_sim.pack(side="right", padx=(0, 10))

    def update_texts(self):
        t = LANGS[self.current_lang]
        self.lbl_title.configure(text=t["title"])
        self.lbl_sub.configure(text=t["sub"])
        self.btn_settings.configure(text=t["settings"])
        self.btn_about.configure(text=t["about"])
        
        self.lbl_s1.configure(text=t["s1"])
        self.btn_browse.configure(text=t["browse"])
        self.entry_source.configure(placeholder_text=t["ph_src"])
        
        self.lbl_s2.configure(text=t["s2"])
        self.chk_type.configure(text=t["t_type"])
        self.chk_date_c.configure(text=t["t_date_c"])
        self.chk_date_m.configure(text=t["t_date_m"])
        self.chk_size.configure(text=t["t_size"])
        self.chk_name.configure(text=t["t_name"])
        
        self.lbl_s3.configure(text=t["s3"])
        self.btn_add_rule.configure(text=t["add_rule"])
        
        self.btn_run.configure(text=t["btn_run"])
        self.btn_sim.configure(text=t["btn_sim"])
        self.btn_undo.configure(text=t["btn_undo"])
        self.btn_dupes.configure(text=t["btn_dupes"])

        opts = self.get_rule_options()
        for r in self.rules:
            r["menu"].configure(values=list(opts.values()))
            r["attr_var"].set(opts[r["current_key"]])
            self.set_placeholder_by_key(r["current_key"], r["val"])
            r["lbl_folder"].configure(text=t["folder"])
            r["dest"].configure(placeholder_text=t["ph_dest"])

    def get_rule_options(self):
        t = LANGS[self.current_lang]
        return {
            "name": t["r_name"], "name_not": t["r_name_not"],
            "name_starts": t["r_name_starts"], "name_ends": t["r_name_ends"], 
            # "name_exact": t["r_name_exact"],
            "ext": t["r_ext"], "ext_not": t["r_ext_not"], 
            "size_gt": t["r_size_gt"], "size_lt": t["r_size_lt"], 
            "date_c": t["r_date_c"], "date_c_after": t["r_date_c_after"], 
            # "date_c_exact": t["r_date_c_exact"],
            "date_m": t["r_date_m"], "date_m_after": t["r_date_m_after"], 
            # "date_m_exact": t["r_date_m_exact"]
        }

    def set_placeholder_by_key(self, key, entry_widget):
        t = LANGS[self.current_lang]
        if "name" in key: entry_widget.configure(placeholder_text=t["ph_name"])
        elif "ext" in key: entry_widget.configure(placeholder_text=t["ph_ext"])
        elif "size" in key: entry_widget.configure(placeholder_text=t["ph_size"])
        elif "date" in key: entry_widget.configure(placeholder_text=t["ph_date"])

    def show_settings(self):
        set_win = ctk.CTkToplevel(self)
        self.apply_window_icon(set_win)
        set_win.title(LANGS[self.current_lang]["settings"])
        self.center_window(set_win, 400, 300)
        set_win.resizable(False, False)
        set_win.configure(fg_color=BG_APP)
        set_win.transient(self)
        set_win.after(100, lambda: set_win.grab_set() if set_win.winfo_exists() else None)
        self.apply_modal_fix(set_win)

        ctk.CTkLabel(set_win, text=LANGS[self.current_lang]["settings"], font=("Segoe UI", 18, "bold"), text_color=TEXT_MAIN).pack(pady=20)

        master_lang_map = {
            "en": "English", "pt": "Português", "es": "Español", 
            "fr": "Français", "de": "Deutsch", "it": "Italiano", 
            "ja": "日本語", "ko": "한국어", "ru": "Русский"
        }
        
        # Só cria as opções se a sigla (k) existir no dicionário LANGS carregado!
        lang_map = {k: master_lang_map[k] for k in LANGS.keys() if k in master_lang_map}
        rev_lang_map = {v: k for k, v in lang_map.items()}

        f1 = ctk.CTkFrame(set_win, fg_color="transparent")
        f1.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(f1, text="Language:", text_color=TEXT_MAIN).pack(side="left")
        
        lang_menu = ctk.CTkOptionMenu(
            f1, 
            values=list(lang_map.values()),   # <--- LISTA DINÂMICA
            fg_color=BG_INPUT, 
            text_color=TEXT_MAIN, 
            button_color=BG_INPUT,
            button_hover_color=BTN_HOVER    
        )
        lang_menu.pack(side="right")
        
        # Trava de segurança: Se o idioma salvo não existir mais, volta pro Inglês
        safe_lang = self.current_lang if self.current_lang in lang_map else "en"
        lang_menu.set(lang_map[safe_lang])

        f2 = ctk.CTkFrame(set_win, fg_color="transparent")
        f2.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(f2, text="Theme:", text_color=TEXT_MAIN).pack(side="left")
        
        theme_menu = ctk.CTkOptionMenu(
            f2, 
            values=["Dark", "Light"], 
            fg_color=BG_INPUT, 
            text_color=TEXT_MAIN, 
            button_color=BG_INPUT,
            button_hover_color=BTN_HOVER   
        )
        theme_menu.pack(side="right")
        theme_menu.set(self.current_theme)

        def save_settings():
            self.current_lang = rev_lang_map[lang_menu.get()]
            self.current_theme = theme_menu.get()
            ctk.set_appearance_mode(self.current_theme)
            self.update_texts()
            
            # ==============================================================
            # 2. PROTEÇÃO ANTI-QUEBRA DE DIRETÓRIO
            # ==============================================================
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True) # Cria a pasta bin se ela não existir
                
            with open(self.config_file, "w") as f:
                json.dump({"lang": self.current_lang, "theme": self.current_theme}, f)
            set_win.destroy()

        ctk.CTkButton(set_win, text="Save", fg_color=ORANGE_MAIN, hover_color=ORANGE_HOVER, command=save_settings).pack(pady=30)

    def show_about(self):
        self.about_win = ctk.CTkToplevel(self)
        self.apply_window_icon(self.about_win)
        self.about_win.title(LANGS[self.current_lang].get("about", "About"))
        self.center_window(self.about_win, 640, 500)
        self.about_win.resizable(False, False)
        self.about_win.configure(fg_color=BG_APP)
        self.about_win.transient(self)
        self.about_win.after(100, lambda: self.about_win.grab_set() if self.about_win.winfo_exists() else None)
        self.apply_modal_fix(self.about_win)

        scroll_frame = ctk.CTkScrollableFrame(self.about_win, width=580, height=350, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        ctk.CTkLabel(scroll_frame, text="Zarfolder", font=("Segoe UI", 24, "bold"), text_color=TEXT_MAIN).pack(anchor="w", pady=(15, 0))
        ctk.CTkLabel(scroll_frame, text=f"Version {self.version}", text_color=TEXT_MUTED, font=("Segoe UI", 13)).pack(anchor="w", pady=(0, 15))
        ctk.CTkLabel(scroll_frame, text="Developed by DanMixerBR", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 25))

        desc_text = LANGS[self.current_lang].get("desc")
        ctk.CTkLabel(scroll_frame, text=desc_text, font=("Segoe UI", 13), text_color=TEXT_MAIN, justify="left", wraplength=550).pack(anchor="w", pady=10)

        self.update_status_lbl = ctk.CTkLabel(scroll_frame, text="", font=("Segoe UI", 12), text_color=TEXT_MUTED)
        self.update_status_lbl.pack(anchor="w", pady=(20, 5))
        
        self.update_progress = ctk.CTkProgressBar(scroll_frame, height=6, progress_color=ORANGE_MAIN, fg_color=BG_INPUT)
        self.update_progress.set(0)
        self.update_progress.pack(fill="x", pady=(0, 10))
        self.update_progress.pack_forget() 

        btn_frame = ctk.CTkFrame(self.about_win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="GitHub", fg_color=BG_INPUT, text_color=TEXT_MAIN, hover_color=BTN_HOVER, width=120, command=lambda: webbrowser.open_new("https://github.com/DanMixerBR/Zarfolder")).pack(side="left", padx=10)
        self.btn_update_app = ctk.CTkButton(btn_frame, text=LANGS[self.current_lang].get("btn_update", "Check for updates"), width=150, command=self.start_github_update, fg_color=ORANGE_MAIN, hover_color=ORANGE_HOVER)
        self.btn_update_app.pack(side="left", padx=10)

    def handle_update_failure(self, error_msg):
        """Método unificado para relatar falhas na atualização."""
        self.safe_ui(self.update_status_lbl.configure, text="Update Failed!", text_color="#a94442")
        self.safe_ui(self.update_progress.configure, progress_color="#a94442")
        
        parent_win = self.about_win if (hasattr(self, 'about_win') and self.about_win.winfo_exists()) else self
        self.safe_ui(messagebox.showerror, "Update Error", error_msg, parent=parent_win)

    def start_github_update(self):
        if self.operation_running:
            messagebox.showwarning("Warning", "Please wait for the current operation to finish.")
            return
        self.btn_update_app.configure(state="disabled", text="Checking...")
        self.is_updating = True 
        self.update_progress.pack(fill="x", pady=(0, 10))
        self.update_progress.set(0)
        self.update_status_lbl.configure(text="Checking for updates...", text_color=TEXT_MAIN)
        
        # FASE 1: Vai pros bastidores apenas checar a versão na API
        threading.Thread(target=self.check_github_version_task, daemon=True).start()

    def check_github_version_task(self):
        api_url = "https://api.github.com/repos/DanMixerBR/Zarfolder/releases/latest"
        try:
            local_v = self.get_local_version()
            response = requests.get(api_url, timeout=10)
            
            # Trava 1: API recusou a conexão (Rate Limit, Erro de Servidor, etc)
            response.raise_for_status() 
            
            data = response.json()
            remote_v = data.get('tag_name')
            
            # Trava 2: API respondeu 200 OK, mas o pacote não tem a tag de versão
            if not remote_v:
                raise Exception("Could not detect latest version from GitHub API payload.")

            clean_remote_v = ''.join(filter(lambda x: x.isdigit() or x == '.', remote_v))
            
            # Trava 3: A tag da versão existe, mas está num formato alienígena sem números
            if not clean_remote_v:
                raise Exception("Invalid version format received from GitHub API.")

            if clean_remote_v != local_v:
                # O SEGREDO DO ASKYYESNO: Envia a pergunta para a Interface Principal com segurança
                self.safe_ui(self.prompt_user_update, local_v, clean_remote_v)
            else:
                self.is_updating = False
                parent_win = self.about_win if (hasattr(self, 'about_win') and self.about_win.winfo_exists()) else self
                self.safe_ui(messagebox.showinfo, "Up to date", "You are already using the latest version.", parent=parent_win)
                self.safe_ui(self.update_status_lbl.configure, text="")
                self.safe_ui(self.update_progress.pack_forget)
                self.safe_ui(self.btn_update_app.configure, state="normal", text=LANGS[self.current_lang].get("btn_update", "Check for updates"))

        except Exception as e:
            self.is_updating = False
            self.safe_ui(self.handle_update_failure, str(e))
            self.safe_ui(self.btn_update_app.configure, state="normal", text=LANGS[self.current_lang].get("btn_update", "Check for updates"))

    def prompt_user_update(self, local_v, clean_remote_v):
        # FASE 2: Pergunta na UI Principal (A Thread só avança com a resposta)
        msg = f"Current version: {local_v}\nLatest version: {clean_remote_v}\n\nDo you want to update?"
        parent_win = self.about_win if (hasattr(self, 'about_win') and self.about_win.winfo_exists()) else self
        
        if messagebox.askyesno("Update available", msg, parent=parent_win):
            self.update_status_lbl.configure(text="Preparing update...", text_color=TEXT_MAIN)
            # Se aceitou, volta para os bastidores para fazer o download (Sem travar a GUI!)
            threading.Thread(target=self.download_and_install_task, daemon=True).start()
        else:
            self.is_updating = False
            self.update_status_lbl.configure(text="Update cancelled.")
            self.update_progress.pack_forget()
            self.btn_update_app.configure(state="normal", text=LANGS[self.current_lang].get("btn_update", "Check for updates"))

    def download_and_install_task(self):
        # FASE 3: O Download Robusto em Stream (Baixo uso de RAM)
        download_url_windows = "https://github.com/DanMixerBR/Zarfolder/releases/latest/download/Zarfolder_Windows.zip"
        download_url_linux = "https://github.com/DanMixerBR/Zarfolder/releases/latest/download/Zarfolder_Linux.zip"
        
        script_ext = "bat" if self.is_windows else "sh"
        script_url = f"https://raw.githubusercontent.com/DanMixerBR/Zarfolder/refs/heads/main/update.{script_ext}"
        hash_url = "https://raw.githubusercontent.com/DanMixerBR/Zarfolder/refs/heads/main/hash.txt"
        zip_platform = "Zarfolder_Windows.zip" if self.is_windows else "Zarfolder_Linux.zip"
        
        dir_app = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        script_path = os.path.join(dir_app, f"update.{script_ext}")
        zip_path = os.path.join(dir_app, zip_platform)
        
        try:
            if os.path.exists(zip_path): os.remove(zip_path)
                
            # 1. Início
            self.safe_ui(self.update_status_lbl.configure, text="Starting update...", text_color=TEXT_MAIN)
            self.safe_ui(self.update_progress.set, 0.0)
            
            target_url = download_url_windows if self.is_windows else download_url_linux
            
            # Puxa o cabeçalho do arquivo
            r = requests.get(target_url, stream=True, timeout=30)
            r.raise_for_status()
            
            # 2. Pega o tamanho total do arquivo
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            last_reported_progress = 0.0
            
            # 3. Download em Stream com atualização em tempo real (0 a 50%)
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: 
                        f.write(chunk)
                        if total_size > 0:
                            downloaded_size += len(chunk)
                            download_percent = downloaded_size / total_size
                            
                            # Mapeia para a metade da barra (0.0 a 0.5)
                            actual_progress = download_percent * 0.5
                            
                            # Só atualiza a tela a cada 1% para não travar a interface!
                            if actual_progress - last_reported_progress >= 0.01 or downloaded_size == total_size:
                                display_percent = int(actual_progress * 100)
                                self.safe_ui(self.update_status_lbl.configure, text=f"Downloading update... {display_percent}%")
                                self.safe_ui(self.update_progress.set, actual_progress)
                                last_reported_progress = actual_progress
            
            # Trava de Segurança Mínima: 10MB para o Zarfolder
            zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            if zip_size_mb < 10.0:
                if os.path.exists(zip_path): os.remove(zip_path)
                raise Exception(f"ERROR: The file '{zip_platform}' is suspiciously small ({zip_size_mb:.1f} MB). Update aborted.")
            
            # 4. Verificação (Hash e Zip)
            self.safe_ui(self.update_status_lbl.configure, text="Verifying update... 50%")
            self.safe_ui(self.update_progress.set, 0.5)
            
            with zipfile.ZipFile(zip_path, 'r') as zf: 
                corrupt_file = zf.testzip()
            
            if corrupt_file is not None:
                if os.path.exists(zip_path): os.remove(zip_path)
                raise Exception(f"ERROR: The file '{zip_platform}' structure is corrupted.")
            
            r_hash = requests.get(hash_url, timeout=10)
            if r_hash.status_code == 200:
                expected_hashes = [line.strip().lower().replace("sha256:", "") for line in r_hash.text.splitlines() if line.strip()]
                sha256_hash = hashlib.sha256()
                with open(zip_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""): 
                        sha256_hash.update(byte_block)
                        
                if sha256_hash.hexdigest().lower() not in expected_hashes:
                    if os.path.exists(zip_path): os.remove(zip_path)
                    raise Exception(f"Security Error: '{zip_platform}' failed Hash verification!")
            else:
                if os.path.exists(zip_path): os.remove(zip_path)
                raise Exception(f"Security Error: Could not download hash.txt to verify '{zip_platform}'.")
                
            # 5. Preparação (Baixando o script de atualização)
            self.safe_ui(self.update_status_lbl.configure, text="Preparing update... 75%")
            self.safe_ui(self.update_progress.set, 0.75)
            
            r_script = requests.get(script_url, timeout=10)
            r_script.raise_for_status()

            # Reutiliza o mesmo hash.txt já baixado anteriormente
            expected_hashes = [
                line.strip().lower().replace("sha256:", "")
                for line in r_hash.text.splitlines()
                if line.strip()
            ]

            script_hash = hashlib.sha256(r_script.content).hexdigest().lower()

            if script_hash not in expected_hashes:
                raise Exception(f"Security Error: update.{script_ext} failed Hash verification!")

            with open(script_path, 'wb') as f:
                f.write(r_script.content)
            
            # 6. Conclusão
            self.safe_ui(self.update_status_lbl.configure, text="Update Ready! (100%)", text_color=ORANGE_MAIN[0])
            self.safe_ui(self.update_progress.set, 1.0)

            # =====================================================================
            # O SEGREDO DO SHOWINFO: Empacotado para fechar somente após o 'OK'
            # =====================================================================
            def finish_update_and_restart():
                parent_win = self.about_win if (hasattr(self, 'about_win') and self.about_win.winfo_exists()) else self
                messagebox.showinfo("Success", "Update Ready! The app will close to complete the update.", parent=parent_win)
                
                if os.path.exists(script_path):
                    if self.is_windows:
                        subprocess.Popen(
                            ["cmd.exe", "/c", "start", "", script_path, str(os.getpid())],
                            cwd=base_dir,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            close_fds=True,
                            creationflags=0x00000010
                        )
                    else:
                        os.chmod(script_path, 0o755) 
                        limpo_env = os.environ.copy()
                        limpo_env.pop("LD_LIBRARY_PATH", None)
                        limpo_env.pop("GTK_PATH", None)
                        comando_bash = f'cd "{dir_app}" && bash update.sh'
                        terminais = [['x-terminal-emulator', '-e'], ['gnome-terminal', '--'], ['konsole', '-e'], ['xfce4-terminal', '-x']]
                        abriu_terminal = False
                        for term in terminais:
                            try:
                                subprocess.Popen(term + ['bash', '-c', comando_bash], env=limpo_env, start_new_session=True)
                                abriu_terminal = True
                                break
                            except Exception: continue
                        if not abriu_terminal:
                            subprocess.Popen(['bash', script_path], env=limpo_env, start_new_session=True)
                    
                os._exit(0)

            # Envia a ordem final e segura para a Interface!
            self.safe_ui(finish_update_and_restart)

        except Exception as e:
            self.is_updating = False
            self.safe_ui(self.handle_update_failure, str(e))
            self.safe_ui(self.btn_update_app.configure, state="normal", text=LANGS[self.current_lang].get("btn_update", "Check for updates"))

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get("lang", "en")
                    self.current_theme = cfg.get("theme", "Light")
            except: pass

    def native_askdirectory(self, title="Choose Directory"):
        if self.is_windows: 
            return filedialog.askdirectory(parent=self, title=title)
            
        # LINUX FIX: Clean PyInstaller's toxic environment variables so system dialogs don't crash
        clean_env = os.environ.copy()
        clean_env.pop("LD_LIBRARY_PATH", None)
        clean_env.pop("GTK_PATH", None)
        
        # Vai direto na ferramenta certa sem tentar e falhar!
        if self.linux_dialog_tool == "zenity":
            res = subprocess.run(['zenity', '--file-selection', '--directory', f'--title={title}'], capture_output=True, text=True, env=clean_env)
            return res.stdout.strip() if res.returncode == 0 else ""
            
        elif self.linux_dialog_tool == "kdialog":
            res = subprocess.run(['kdialog', '--getexistingdirectory', '/', '--title', title], capture_output=True, text=True, env=clean_env)
            return res.stdout.strip() if res.returncode == 0 else ""
            
        # Fallback de segurança: Tkinter Dinosaur Dialog
        return filedialog.askdirectory(parent=self, title=title)

    def browse_source(self):
        folder = self.native_askdirectory(title="Select Folder")
        if folder: self.source_folder.set(folder)

    def add_rule_row(self):
        if len(self.rules) >= self.MAX_RULES: return

        rule_frame = ctk.CTkFrame(self.rules_container, fg_color=BG_APP, corner_radius=8)
        rule_frame.pack(fill="x", pady=5, padx=5)
        
        t = LANGS[self.current_lang]
        opts = self.get_rule_options()
        rule_dict = {"frame": rule_frame, "current_key": "name"}
        attr_var = ctk.StringVar(value=opts["name"])

        def on_option_change(choice):
            opts_rev = {v: k for k, v in self.get_rule_options().items()}
            rule_dict["current_key"] = opts_rev.get(choice)
            self.set_placeholder_by_key(rule_dict["current_key"], val_entry)

        attr_menu = ctk.CTkOptionMenu(
            rule_frame, 
            values=list(opts.values()), 
            variable=attr_var, 
            command=on_option_change, 
            width=280, 
            fg_color=BG_INPUT, 
            text_color=TEXT_MAIN, 
            button_color=BG_INPUT,
            button_hover_color=BTN_HOVER
        )
        attr_menu.pack(side="left", padx=10, pady=10)

        val_entry = ctk.CTkEntry(rule_frame, placeholder_text=t["ph_name"], width=130, fg_color=BG_INPUT, text_color=TEXT_MAIN, border_width=1, border_color=COLOR_BORDER)
        val_entry.pack(side="left", padx=(0, 10))

        lbl_folder = ctk.CTkLabel(rule_frame, text=t["folder"], text_color=TEXT_MAIN)
        lbl_folder.pack(side="left", padx=(5, 5))

        dest_entry = ctk.CTkEntry(rule_frame, placeholder_text=t["ph_dest"], fg_color=BG_INPUT, text_color=TEXT_MAIN, border_width=1, border_color=COLOR_BORDER)
        dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def remove_self():
            rule_frame.destroy()
            self.rules.remove(rule_dict)

        btn_remove = ctk.CTkButton(rule_frame, text="X", width=30, fg_color="#a94442", hover_color="#803331", command=remove_self)
        btn_remove.pack(side="right", padx=10)

        rule_dict.update({"menu": attr_menu, "attr_var": attr_var, "val": val_entry, "dest": dest_entry, "lbl_folder": lbl_folder})
        self.rules.append(rule_dict)

    # ==========================================
    # FORÇA BRUTA: Módulo de Permissões
    # ==========================================
    def force_move(self, src, dst):
        try: os.chmod(src, stat.S_IWRITE)
        except: pass
        shutil.move(src, dst)

    def _force_rmdir(self, dir_path):
        try:
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.chmod(dir_path, stat.S_IWRITE)
                os.rmdir(dir_path)
                return True
        except Exception:
            pass

        return False

    def remove_empty_folders(self, path, remove_root=False):
        removed_dirs = []

        if not os.path.exists(path):
            return removed_dirs

        for root, dirs, files in os.walk(path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)

                if self._force_rmdir(dir_path):
                    removed_dirs.append(dir_path)

        if remove_root:
            if self._force_rmdir(path):
                removed_dirs.append(path)

        return removed_dirs

    def snapshot_dirs(self, src):
        dir_set = set()
        for root, dirs, files in os.walk(src):
            for d in dirs: dir_set.add(os.path.join(root, d))
        return dir_set

    def iter_files(self, src):
        for root, dirs, files in os.walk(src):
            for file in files:
                yield os.path.join(root, file)

    def ensure_dir(self, path, created_dirs=None):
        if os.path.isdir(path):
            return

        dirs_to_create = []
        current = path

        while current and not os.path.exists(current):
            dirs_to_create.append(current)
            parent = os.path.dirname(current)

            if parent == current:
                break

            current = parent

        os.makedirs(path, exist_ok=True)

        if created_dirs is not None:
            created_dirs.extend(reversed(dirs_to_create))

    def hash_file_partial(self, filepath, block_size=1024 * 1024):
        file_size = os.path.getsize(filepath)
        hasher = hashlib.sha256()
        hasher.update(str(file_size).encode("utf-8"))

        with open(filepath, "rb") as f:
            first_block = f.read(block_size)
            hasher.update(first_block)

            if file_size > block_size:
                f.seek(max(file_size - block_size, 0))
                last_block = f.read(block_size)
                hasher.update(last_block)

        return hasher.hexdigest()

    def hash_file_full(self, filepath, chunk_size=1024 * 1024):
        hasher = hashlib.sha256()

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    # ==========================================
    # PREVENÇÃO DE COLISÃO DE ARQUIVOS 
    # ==========================================
    def get_unique_path(self, dest_folder, filename, original_filepath):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_path = os.path.join(dest_folder, filename)
        
        if original_filepath == new_path:
            return new_path
            
        while os.path.exists(new_path):
            new_path = os.path.join(dest_folder, f"{base} ({counter}){ext}")
            counter += 1
            
        return new_path

    # ==========================================
    # PROCESSAMENTO EM BACKGROUND (MULTI-THREADING)
    # ==========================================
    def start_find_duplicates(self):
        src = self.source_folder.get()
        if not os.path.exists(src):
            return

        if not self.begin_operation():
            return

        self.show_loading("load_title", "load_dupes")
        threading.Thread(target=self._task_find_duplicates, args=(src,), daemon=True).start()

    def _task_find_duplicates(self, src):
        dupes_folder = os.path.join(src, "Duplicates")
        moved = 0

        try:
            size_dict = {}

            for root, _, files in os.walk(src):
                try:
                    if os.path.commonpath([root, dupes_folder]) == dupes_folder:
                        continue
                except ValueError:
                    pass

                for file in files:
                    filepath = os.path.join(root, file)

                    try:
                        size = os.path.getsize(filepath)
                        size_dict.setdefault(size, []).append(filepath)
                    except Exception:
                        pass

            partial_groups = {}

            for size, file_paths in size_dict.items():
                if len(file_paths) < 2:
                    continue

                for filepath in file_paths:
                    try:
                        partial_hash = self.hash_file_partial(filepath)
                        partial_groups.setdefault((size, partial_hash), []).append(filepath)
                    except Exception:
                        pass

            for _, file_paths in partial_groups.items():
                if len(file_paths) < 2:
                    continue

                full_hashes = {}

                for filepath in file_paths:
                    try:
                        full_hash = self.hash_file_full(filepath)

                        if full_hash in full_hashes:
                            if not os.path.exists(dupes_folder):
                                os.makedirs(dupes_folder, exist_ok=True)

                            file = os.path.basename(filepath)
                            safe_path = self.get_unique_path(dupes_folder, file, filepath)
                            self.force_move(filepath, safe_path)
                            moved += 1
                        else:
                            full_hashes[full_hash] = filepath

                    except Exception:
                        pass

        finally:
            self.safe_ui(self.finish_operation)
            self.safe_ui(messagebox.showinfo, "Duplicatas", LANGS[self.current_lang]["msg_dupes"].format(moved))

    def start_undo_last_action(self):
        if not os.path.exists(self.undo_file):
            return

        if not self.begin_operation():
            return

        self.show_loading("load_title", "load_undo")
        threading.Thread(target=self._task_undo_last_action, daemon=True).start()

    def _task_undo_last_action(self):
        try:
            with open(self.undo_file, "r") as f: log_data = json.load(f)
            
            moves = log_data.get("moves", log_data) 
            created_dirs = log_data.get("created_dirs", [])
            deleted_dirs = log_data.get("deleted_dirs", [])
            
            restored = 0
            
            for d in deleted_dirs:
                try: os.makedirs(d, exist_ok=True)
                except: pass

            for current_pos, original_pos in moves.items():
                if os.path.exists(current_pos):
                    try:
                        original_dir = os.path.dirname(original_pos)
                        os.makedirs(original_dir, exist_ok=True)
                        self.force_move(current_pos, original_pos)
                        restored += 1
                    except: pass

            created_dirs.sort(key=len, reverse=True)
            for d in created_dirs: self.remove_empty_folders(d, remove_root=True)

            os.remove(self.undo_file)
        finally:
            self.safe_ui(self.finish_operation)
            self.safe_ui(lambda: self.after(200, lambda: messagebox.showinfo("Undo", LANGS[self.current_lang]["msg_undo"].format(restored))))

    def start_execute_rules(self, simulate=False):
        src = self.source_folder.get()
        if not os.path.exists(src):
            return

        active_rules = []

        for r in self.rules:
            val = r["val"].get().strip()
            folder_name = r["dest"].get().strip()

            if val and folder_name:
                clean_folder = "".join(c for c in folder_name if c not in r'\/:*?"<>|')
                if clean_folder:
                    active_rules.append({
                        "key": r["current_key"],
                        "val": val,
                        "dest": clean_folder
                    })

        auto_opts = {
            "type": self.chk_type_var.get(),
            "date_c": self.chk_date_c_var.get(),
            "date_m": self.chk_date_m_var.get(),
            "size": self.chk_size_var.get(),
            "name": self.chk_name_var.get()
        }

        has_auto = any(auto_opts.values())

        if not active_rules and not has_auto:
            messagebox.showwarning("Warning", "Please select at least one automatic classification option or define a rule.")
            return

        if not self.begin_operation():
            return

        if simulate:
            self.show_loading("load_title", "load_sim")
        else:
            self.show_loading("load_title", "load_org")

        threading.Thread(
            target=self._task_execute_rules,
            args=(src, simulate, active_rules, auto_opts),
            daemon=True
        ).start()

    def _task_execute_rules(self, src, simulate, active_rules, auto_opts):
        t = LANGS[self.current_lang]
        has_auto = any(auto_opts.values())
        file_iterator = self.iter_files(src)

        moved_count = 0
        sim_moves = [] 
        sim_moves_limit = self.SIMULATION_PREVIEW_LIMIT

        def add_sim_move(file_name, destination):
            if len(sim_moves) < sim_moves_limit:
                sim_moves.append((file_name, destination))

        moves_dict = {}
        created_dirs = []

        if not simulate and os.path.exists(self.undo_file):
            os.remove(self.undo_file)

        try:
            for filepath in file_iterator:
                if not os.path.exists(filepath): continue
                
                file = os.path.basename(filepath)
                file_lower = file.lower()
                file_root, ext = os.path.splitext(file)
                ext = ext.lower()
                base_name = file_root.lower()
                
                # === NOVA LÓGICA DE REGRAS EM CASCATA ===
                final_dest = None # Guarda a decisão final
                
                for rule in active_rules:
                    match = False
                    rule_val = rule["val"].lower()
                    
                    if rule["key"] == "ext" and ext == rule_val: match = True
                    elif rule["key"] == "ext_not" and ext != rule_val: match = True
                    
                    elif rule["key"] == "name" and rule_val in file_lower: match = True
                    elif rule["key"] == "name_not" and rule_val not in file_lower: match = True
                    elif rule["key"] == "name_starts" and base_name.startswith(rule_val): match = True
                    elif rule["key"] == "name_ends" and base_name.endswith(rule_val): match = True
                    elif rule["key"] == "name_exact" and base_name == rule_val: match = True
                    
                    elif rule["key"] == "size_gt":
                        try:
                            if (os.path.getsize(filepath) / (1024 * 1024)) > float(rule["val"]): match = True
                        except: pass
                    elif rule["key"] == "size_lt":
                        try:
                            if (os.path.getsize(filepath) / (1024 * 1024)) < float(rule["val"]): match = True
                        except: pass
                        
                    elif rule["key"] == "date_c":
                        try:
                            if self.get_creation_date(filepath) < rule["val"]: match = True
                        except: pass
                    elif rule["key"] == "date_c_after":  
                        try:
                            if self.get_creation_date(filepath) > rule["val"]: match = True
                        except: pass
                    elif rule["key"] == "date_c_exact":  
                        try:
                            if self.get_creation_date(filepath) == rule["val"]: match = True
                        except: pass
                        
                    elif rule["key"] == "date_m":
                        try:
                            if self.get_modification_date(filepath) < rule["val"]: match = True
                        except: pass
                    elif rule["key"] == "date_m_after":  
                        try:
                            if self.get_modification_date(filepath) > rule["val"]: match = True
                        except: pass
                    elif rule["key"] == "date_m_exact":  
                        try:
                            if self.get_modification_date(filepath) == rule["val"]: match = True
                        except: pass

                    if match:
                        # Com break a primeira regra vence, sem break a última regra vence
                        final_dest = rule["dest"]
                        break
                
                # Aplicando a movimentação baseada na última regra vitoriosa
                if final_dest:
                    dest_folder = os.path.join(src, final_dest)
                    safe_new_path = self.get_unique_path(dest_folder, file, filepath)
                    
                    if simulate: 
                        add_sim_move(file, safe_new_path)
                        if len(sim_moves) >= sim_moves_limit:
                            break
                    else:
                        if filepath != safe_new_path: 
                            try:
                                self.ensure_dir(dest_folder, created_dirs)
                                self.force_move(filepath, safe_new_path)
                                moves_dict[safe_new_path] = filepath
                                moved_count += 1
                            except:
                                pass
                            
                    # Se caiu em uma regra manual, o loop "continue" pula a Classificação Automática!
                    continue 

                # ===============================================
                # CLASSIFICAÇÃO AUTOMÁTICA (Só age se NENHUMA regra manual pegou o arquivo)
                if has_auto:
                    sub_paths = []
                    if auto_opts["type"]:
                        sub_paths.append(self.get_file_type(file))

                    if auto_opts["date_c"]:
                        sub_paths.append(self.get_creation_date(filepath)[:7])

                    if auto_opts["date_m"]:
                        sub_paths.append(self.get_modification_date(filepath)[:7])

                    if auto_opts["size"]:
                        sub_paths.append(self.get_size_category(filepath))

                    if auto_opts["name"]:
                        sub_paths.append(self.get_name_category(file))

                    target_path = os.path.join(src, *sub_paths)
                    safe_new_path = self.get_unique_path(target_path, file, filepath)
                    
                    if simulate: 
                        add_sim_move(file, safe_new_path)
                        if len(sim_moves) >= sim_moves_limit:
                            break
                    else:
                        if filepath != safe_new_path:
                            try:
                                self.ensure_dir(target_path, created_dirs)
                                self.force_move(filepath, safe_new_path)
                                moves_dict[safe_new_path] = filepath
                                moved_count += 1
                            except:
                                pass

            if simulate:
                self.safe_ui(self._generate_tree_and_finish, src, sim_moves)
            else:
                removed_dirs = self.remove_empty_folders(src)

                created_dirs_set = set(created_dirs)
                deleted_dirs = [d for d in removed_dirs if d not in created_dirs_set]

                created_dirs = list(dict.fromkeys(created_dirs))
                deleted_dirs = list(dict.fromkeys(deleted_dirs))

                log_data = {
                    "moves": moves_dict,
                    "created_dirs": created_dirs,
                    "deleted_dirs": deleted_dirs
                }
                with open(self.undo_file, "w") as f: json.dump(log_data, f)
                    
                self.safe_ui(self.finish_operation)
                self.safe_ui(lambda: self.after(200, lambda: messagebox.showinfo("Success", t["msg_success"].format(moved_count))))
                
        except Exception as e:
            self.safe_ui(self.finish_operation)
            print(f"Erro Crítico: {e}")

    def _generate_tree_and_finish(self, src, sim_moves):
        self.finish_operation()
        self.after(200, lambda: self._show_simulation_tree(src, sim_moves))

    # ==========================================
    # ÁRVORE GRÁFICA USANDO TTK.TREEVIEW (ALTO DESEMPENHO)
    # ==========================================
    def _show_simulation_tree(self, root_src, sim_moves):
        t = LANGS[self.current_lang]
        sim_win = ctk.CTkToplevel(self)
        self.apply_window_icon(sim_win)
        sim_win.title(t["btn_sim"])
        self.center_window(sim_win, 650, 500)
        sim_win.configure(fg_color=BG_APP)
        sim_win.transient(self) 
        sim_win.after(100, lambda: sim_win.grab_set() if sim_win.winfo_exists() else None)
        self.apply_modal_fix(sim_win)
        
        ctk.CTkLabel(sim_win, text="Preview of Organized Folders", font=("Segoe UI", 18, "bold"), text_color=TEXT_MAIN).pack(pady=(15, 5))
        
        container = ctk.CTkFrame(sim_win, fg_color=BG_FRAME, corner_radius=10)
        container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        if not sim_moves:
            ctk.CTkLabel(container, text="No files matched the current rules.", text_color=TEXT_MUTED).pack(pady=20)
            return

        style = ttk.Style(sim_win)
        style.theme_use("default")

        bg_color = BG_FRAME[1] if self.current_theme == "Dark" else BG_FRAME[0]
        text_color = TEXT_MAIN[1] if self.current_theme == "Dark" else TEXT_MAIN[0]
        select_bg = BG_INPUT[1] if self.current_theme == "Dark" else BG_INPUT[0]

        style.configure("Custom.Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, font=("Segoe UI", 12))
        style.map("Custom.Treeview", background=[("selected", select_bg)], foreground=[("selected", ORANGE_MAIN[0])]) 
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])

        tree_widget = ttk.Treeview(container, style="Custom.Treeview", show="tree", selectmode="browse")
        
        scrollbar = ctk.CTkScrollbar(container, command=tree_widget.yview, fg_color="transparent", button_color=COLOR_BORDER)
        tree_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", pady=5)
        tree_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tree = {}
        for original_file, dest_path in sim_moves:
            rel_path = os.path.relpath(dest_path, root_src).replace('\\', '/')
            parts = rel_path.split('/')
            
            current_level = tree
            for part in parts[:-1]:
                if part not in current_level: current_level[part] = {}
                current_level = current_level[part]
            current_level[parts[-1]] = None

        def populate_tree(parent_id, node):
            folders = {k: v for k, v in node.items() if v is not None}
            files = {k: v for k, v in node.items() if v is None}

            for f_name, sub_node in sorted(folders.items()):
                folder_id = tree_widget.insert(parent_id, "end", text=f"📁 {f_name}", open=False)
                populate_tree(folder_id, sub_node)

            for file_name in sorted(files.keys()):
                tree_widget.insert(parent_id, "end", text=f"📄 {file_name}")

        populate_tree("", tree)

    def get_file_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()

        if ext in VIDEO_EXTENSIONS:
            return "Videos"

        if ext in IMAGE_EXTENSIONS:
            return "Pictures"

        if ext in AUDIO_EXTENSIONS:
            return "Music"

        if ext in DOCUMENT_EXTENSIONS:
            return "Documents"

        if ext in ARCHIVE_EXTENSIONS:
            return "Archives"

        if ext in EXECUTABLE_EXTENSIONS:
            return "Executables"
        
        if ext in CODE_EXTENSIONS:
            return "Code & Scripts"
        
        return "Other files"

    def get_creation_date(self, filepath):
        try: return datetime.fromtimestamp(os.stat(filepath).st_birthtime).strftime('%Y-%m-%d')
        except: return datetime.fromtimestamp(os.stat(filepath).st_ctime).strftime('%Y-%m-%d')
        
    def get_modification_date(self, filepath):
        return datetime.fromtimestamp(os.stat(filepath).st_mtime).strftime('%Y-%m-%d')

    def get_name_category(self, filename):
        return filename[0].upper() if filename[0].isalpha() else "#" 

    def get_size_category(self, filepath):
        mb = os.path.getsize(filepath) / (1024 * 1024)
        if mb < 10: return "Small (Under 10MB)"
        if mb <= 100: return "Medium (10MB-100MB)"
        return "Large (Over 100MB)"

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
