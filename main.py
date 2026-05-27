import os
import sys
import shutil
import subprocess
import json
import hashlib
import zipfile
import threading
import webbrowser
import requests
import stat
import ctypes
from datetime import datetime

from PySide6.QtCore import Qt, QSize, QTimer, QObject, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap, QFont, QImageReader
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QProgressBar,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy
)

try:
    from mutagen import File as MutagenFile
except Exception:
    MutagenFile = None

try:
    from pymediainfo import MediaInfo
except Exception:
    MediaInfo = None

# ==========================================
# GLOBAL PATH FIX (LINUX/WINDOWS)
# ==========================================
if getattr(sys, "frozen", False):
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
ORANGE_MAIN = ("#ff9f43", "#c96a1b")
ORANGE_HOVER = ("#e67e22", "#e67e22")
DANGER = ("#b94a48", "#a94442")
DANGER_HOVER = ("#803331", "#803331")

# ==========================================
# EXTENSÕES (SETS)
# ==========================================
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".mpg", ".mpeg",
    ".m4v", ".3gp", ".3g2", ".ts", ".mts", ".m2ts", ".vob", ".ogv", ".rm",
    ".rmvb", ".asf", ".divx", ".f4v", ".h264", ".hevc", ".vp9", ".amv",
    ".srt"
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".tif",
    ".ico", ".heic", ".heif", ".raw", ".cr2", ".nef", ".orf", ".sr2",
    ".psd", ".ai", ".eps", ".indd", ".jfif", ".pjpeg", ".pjp"
}

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".wma", ".alac",
    ".aiff", ".ape", ".opus", ".mid", ".midi", ".amr", ".ac3", ".dts",
    ".ra"
}

DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".ott",
    ".xlsx", ".xls", ".csv", ".ods",
    ".ppt", ".pptx", ".odp",
    ".md", ".log", ".tex", ".wpd",
    ".html", ".mhtml", ".htm", ".msg", ".eml", ".pst"
}

ARCHIVE_EXTENSIONS = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lz", ".lzma",
    ".cab", ".iso", ".arj", ".z", ".tgz", ".tbz2", ".txz"
}

EXECUTABLE_EXTENSIONS = {
    ".exe", ".msi", ".apk", ".app", ".bin", ".run", ".jar"
}

CODE_EXTENSIONS = {
    ".bat", ".cmd", ".sh", ".bash", ".zsh", ".ps1", ".vbs", ".wsf",
    ".py", ".pyc", ".ipynb", ".whl",
    ".css", ".js", ".jsx", ".ts", ".tsx", ".php", ".cgi", ".pl",
    ".c", ".cpp", ".cs", ".java", ".kt", ".swift", ".go", ".rs", ".rb",
    ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".env", ".sql",
    ".reg"
}

# ==========================================
# DICIONÁRIO DE TRADUÇÕES (LOCALIZATION)
# ==========================================
LANGS = {
    "en": {
        "title": "Zarfolder", "sub": "Smart File Management", "settings": "Settings", "about": "About",
        "s1": "1. Select Folder to Organize", "browse": "Browse", "ph_src": "Choose the messy folder...",
        "s2": "2. Automatic Classification (Check to enable)",
        "t_type": "Type (Videos, Music...)", "t_date_c": "Creation Date", "t_date_m": "Modified Date", "t_size": "Size (Small, Med...)", "t_name": "Name (A-Z)",
        "t_ext": "Extension", "t_resolution": "Resolution", "t_codec": "Codec", "t_artist": "Artist", "t_album": "Album",
        "s3": "3. Define Organization Rules (Optional)", "add_rule": "+ Add Rule",
        "btn_run": "Organize", "btn_sim": "Simulate", "btn_undo": "Undo Last", "btn_dupes": "Find Dupes",
        "r_name": "Name contains", "r_name_not": "Name does NOT contain",
        "r_name_starts": "Name starts with", "r_name_ends": "Name ends with", "r_name_exact": "Name is exactly",
        "r_ext": "Extension is", "r_ext_not": "Extension is NOT",
        "r_size_gt": "Size > (MB)", "r_size_lt": "Size < (MB)",
        "r_date_c": "Created before (YYYY-MM-DD)", "r_date_c_after": "Created after (YYYY-MM-DD)", "r_date_c_exact": "Created exactly on (YYYY-MM-DD)",
        "r_date_m": "Modified before (YYYY-MM-DD)", "r_date_m_after": "Modified after (YYYY-MM-DD)", "r_date_m_exact": "Modified exactly on (YYYY-MM-DD)",
        "folder": "Folder:", "ph_dest": "e.g. Docs",
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


class UiBridge(QObject):
    call_requested = Signal(object, object, object)


class FileOrganizerApp(QMainWindow):
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

        self.rules = []
        self.MAX_RULES = 15
        self.about_win = None
        self.update_status_lbl = None
        self.update_progress = None
        self.btn_update_app = None

        self.is_windows = os.name == "nt"
        self.load_config()

        self.ui_bridge = UiBridge()
        self.ui_bridge.call_requested.connect(self._run_ui_call)

        self.setWindowTitle("Zarfolder")
        self.resize(850, 670)
        self.setMinimumSize(850, 670)
        self.apply_window_icon(self)

        self.linux_dialog_tool = None
        if not self.is_windows:
            desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            if "kde" in desktop and shutil.which("kdialog"):
                self.linux_dialog_tool = "kdialog"
            elif shutil.which("zenity"):
                self.linux_dialog_tool = "zenity"
            elif shutil.which("kdialog"):
                self.linux_dialog_tool = "kdialog"
            else:
                self.linux_dialog_tool = "qt"

        self.build_ui()
        self.apply_theme()
        self.update_texts()
        self.apply_titlebar_theme()
        self.center_window(self, 850, 670)

    # ==========================================
    # UTILITÁRIOS VISUAIS
    # ==========================================
    def color(self, pair):
        return pair[1] if self.current_theme == "Dark" else pair[0]

    def apply_theme(self):
        bg_app = self.color(BG_APP)
        bg_frame = self.color(BG_FRAME)
        bg_input = self.color(BG_INPUT)
        text = self.color(TEXT_MAIN)
        muted = self.color(TEXT_MUTED)
        border = self.color(COLOR_BORDER)
        btn_hover = self.color(BTN_HOVER)
        orange = self.color(ORANGE_MAIN)
        orange_hover = self.color(ORANGE_HOVER)
        danger = self.color(DANGER)
        danger_hover = self.color(DANGER_HOVER)
        
        scrollbar_bg = bg_app
        scrollbar_handle = border    

        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {bg_app};
                color: {text};
                font-family: "Segoe UI";
                font-size: 13px;
            }}

            QLabel {{
                color: {text};
                background: transparent;
            }}

            QLabel#MutedLabel {{
                color: {muted};
            }}
            
            QLabel#SubTitleLabel {{
                color: {muted};
                padding-top: 7px;
                padding-left: -1px;
            }}            

            QFrame#Card {{
                background-color: {bg_frame};
                border-radius: 15px;
            }}

            QFrame#RuleRow {{
                background-color: {bg_app};
                border-radius: 8px;
            }}

            QLineEdit {{
                background-color: {bg_app};
                color: {text};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 7px 8px;
            }}

            QLineEdit#RuleLineEdit {{
                background-color: {bg_input};
                color: {text};
                border: 1px solid {border};
                border-radius: 7px;
                padding: 5px 8px;
            }}

            QLineEdit#RuleLineEdit:hover {{
                background-color: {btn_hover};
                border: 1px solid {border};
            }}

            QComboBox {{
                background-color: {bg_input};
                color: {text};
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 6px 10px;
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: {btn_hover};
            }}

            QComboBox::drop-down:hover,
            QComboBox::drop-down:on {{
                background-color: {orange};
            }}

            QComboBox QAbstractItemView {{
                background-color: {bg_input};
                color: {text};
                border: 1px solid {border};
                border-radius: 6px;
                selection-background-color: {btn_hover};
                selection-color: {text};
                outline: 0px;
            }}

            QComboBox QAbstractItemView::item {{
                color: {text};
                background-color: {bg_input};
            }}

            QComboBox QAbstractItemView::item:selected {{
                color: {text};
                background-color: {btn_hover};
            }}

            QComboBox QAbstractItemView::item:hover {{
                color: {text};
                background-color: {btn_hover};
            }}

            QPushButton {{
                background-color: {bg_input};
                color: {text};
                border: none;
                border-radius: 10px;
                padding: 0px 14px;
            }}

            QPushButton:hover {{
                background-color: {btn_hover};
            }}

            QPushButton#PrimaryButton {{
                background-color: {orange};
                color: white;
                font-weight: 700;
            }}

            QPushButton#PrimaryButton:hover {{
                background-color: {orange_hover};
            }}

            QPushButton#DangerButton {{
                background-color: {bg_input};
                color: {text};
                font-weight: 700;
                border-radius: 8px;
                padding: 0px;
                min-width: 0px;
                min-height: 0px;
            }}

            QPushButton#DangerButton:hover {{
                color: white;
                background-color: {danger};
            }}

            QMessageBox QPushButton {{
                min-width: 45px;
                min-height: 20px;
                padding: 4px 14px;
                border-radius: 6px;
            }}

            QCheckBox {{
                color: {text};
                spacing: 8px;
                padding: 2px 0px;
                border-radius: 6px;
            }}

            QCheckBox::indicator {{
                width: 19px;
                height: 19px;
                border: 2px solid {border};
                border-radius: 5px;
                background-color: transparent;
            }}

            QCheckBox::indicator:hover {{
                border: 2px solid {orange};
                background-color: {bg_input};
            }}

            QCheckBox::indicator:checked {{
                background-color: {orange};
                border: 2px solid {orange};
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {orange_hover};
                border: 2px solid {orange_hover};
            }}

            QScrollArea {{
                border: none;
                background: transparent;
            }}

            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}

            QTreeWidget {{
                background-color: {bg_frame};
                color: {text};
                border: none;
                font-size: 16px;
            }}

            QTreeWidget::item {{
                height: 24px;
            }}

            QTreeWidget::item:selected {{
                background-color: {bg_input};
                color: {orange};
            }}

            QProgressBar {{
                background-color: {bg_input};
                border: none;
                border-radius: 2px;
                max-height: 6px;
                min-height: 6px;
                text-align: center;
                color: transparent;
            }}

            QProgressBar::chunk {{
                background-color: {orange};
                border-radius: 2px;
            }}

            QScrollBar:vertical {{
                border: none;
                background: {scrollbar_bg};
                width: 12px;
                margin: 4px 0 4px 0;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                min-height: 24px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {btn_hover};
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: {scrollbar_bg};
                border-radius: 6px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    def center_window(self, win, width, height):
        screen = QApplication.primaryScreen()
        if not screen:
            return

        geo = screen.availableGeometry()
        x = geo.x() + int((geo.width() - width) / 2)
        y = geo.y() + int((geo.height() - height) / 2)
        win.move(x, y)

    def apply_window_icon(self, window):
        icon_path = os.path.join(base_dir, "bin", "icons", "icon.ico" if self.is_windows else "icon.png")
        if os.path.exists(icon_path):
            window.setWindowIcon(QIcon(icon_path))

    def get_icon_path(self, icon_name):
        theme_folder = "dark" if self.current_theme == "Dark" else "light"
        return os.path.join(base_dir, "bin", "icons", theme_folder, icon_name).replace("\\", "/")

    def set_button_icon(self, button, icon_name, size=16):
        icon_path = self.get_icon_path(icon_name)

        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(size, size))

    def apply_clickable_cursors(self, window=None):
        target = window or self

        for widget_class in (QPushButton, QComboBox, QCheckBox):
            for widget in target.findChildren(widget_class):
                widget.setCursor(Qt.CursorShape.PointingHandCursor)

    def fix_ghost_cursor(self, widget=None):
        target = widget or self.sender()

        QApplication.restoreOverrideCursor()
        self.unsetCursor()

        if target:
            target.setCursor(Qt.CursorShape.ArrowCursor)
            QTimer.singleShot(
                200,
                lambda t=target: t.setCursor(Qt.CursorShape.PointingHandCursor) if t else None
            )

    def apply_titlebar_theme(self, window=None):
        if not self.is_windows:
            return

        try:
            target = window or self
            hwnd = int(target.winId())

            dark_mode = ctypes.c_int(1 if self.current_theme == "Dark" else 0)
            caption_color = ctypes.c_int(0x00141414 if self.current_theme == "Dark" else 0x00FFFFFF)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode)
            )

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color)
            )
        except Exception:
            pass

    def safe_ui(self, func, *args, **kwargs):
        self.ui_bridge.call_requested.emit(func, args, kwargs)

    @Slot(object, object, object)
    def _run_ui_call(self, func, args, kwargs):
        try:
            func(*args, **kwargs)
        except RuntimeError:
            pass

    def begin_operation(self):
        if self.operation_running:
            self.show_warning("Warning", "Another operation is already running.", self)
            return False

        self.operation_running = True
        return True

    def finish_operation(self):
        self.operation_running = False
        self.hide_loading()

    def show_loading(self, title_key, message_key):
        t = LANGS[self.current_lang]

        self.loading_window = QDialog(self)
        self.loading_window.setWindowTitle(t[title_key])
        self.loading_window.setFixedSize(350, 150)
        self.loading_window.setWindowModality(Qt.ApplicationModal)
        self.apply_window_icon(self.loading_window)

        layout = QVBoxLayout(self.loading_window)
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        lbl = QLabel(t[message_key])
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        content_layout.addWidget(lbl)

        pb = QProgressBar()
        pb.setRange(0, 0)
        pb.setTextVisible(False)
        pb.setFixedHeight(4)
        pb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(pb)

        layout.addStretch(1)
        layout.addWidget(content)
        layout.addStretch(2)

        self.apply_titlebar_theme(self.loading_window)
        self.loading_window.show()
        self.center_window(self.loading_window, 350, 150)

    def hide_loading(self):
        win = self.loading_window
        self.loading_window = None

        if win:
            win.hide()
            QTimer.singleShot(500, win.deleteLater)

    def show_message_box(self, icon, title, message, buttons=QMessageBox.Ok, default_button=None, parent=None):
        box = QMessageBox(parent or self)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(icon)
        box.setStandardButtons(buttons)

        if default_button is not None:
            box.setDefaultButton(default_button)

        self.apply_window_icon(box)
        self.apply_clickable_cursors(box)
        self.apply_titlebar_theme(box)

        return box.exec()

    def show_info(self, title, message, parent=None):
        return self.show_message_box(QMessageBox.Information, title, message, parent=parent)

    def show_warning(self, title, message, parent=None):
        return self.show_message_box(QMessageBox.Warning, title, message, parent=parent)

    def show_error(self, title, message, parent=None):
        return self.show_message_box(QMessageBox.Critical, title, message, parent=parent)

    def ask_yes_no(self, title, message, parent=None):
        result = self.show_message_box(
            QMessageBox.Question,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
            parent
        )

        return result == QMessageBox.Yes

    def set_progress_fraction(self, value):
        if self.update_progress:
            self.update_progress.setValue(int(max(0.0, min(1.0, value)) * 100))

    def set_button_enabled_text(self, button, enabled, text):
        if button:
            button.setEnabled(enabled)
            button.setText(text)

    def get_local_version(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass

        return "Unknown"

    def load_undo_history(self):
        if not os.path.exists(self.undo_file):
            return []

        try:
            with open(self.undo_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Novo formato
            if isinstance(data, dict) and "history" in data:
                return data.get("history", [])

            # Compatibilidade com undo antigo
            if isinstance(data, dict):
                return [{
                    "type": data.get("type", "organize"),
                    "timestamp": data.get("timestamp", ""),
                    "moves": data.get("moves", data),
                    "created_dirs": data.get("created_dirs", []),
                    "deleted_dirs": data.get("deleted_dirs", [])
                }]

        except Exception:
            pass

        return []

    def save_undo_history(self, history):
        if history:
            undo_dir = os.path.dirname(self.undo_file)
            if undo_dir:
                os.makedirs(undo_dir, exist_ok=True)

            with open(self.undo_file, "w", encoding="utf-8") as f:
                json.dump({"history": history}, f, indent=2)
        else:
            if os.path.exists(self.undo_file):
                os.remove(self.undo_file)

    def add_undo_action(self, action_type, moves, created_dirs=None, deleted_dirs=None):
        created_dirs = list(dict.fromkeys(created_dirs or []))
        deleted_dirs = list(dict.fromkeys(deleted_dirs or []))

        if not moves and not created_dirs and not deleted_dirs:
            return

        history = self.load_undo_history()

        history.append({
            "type": action_type,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "moves": moves,
            "created_dirs": created_dirs,
            "deleted_dirs": deleted_dirs
        })

        self.save_undo_history(history)

    # ==========================================
    # UI PRINCIPAL
    # ==========================================
    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        logo_path = os.path.join(base_dir, "bin", "icons", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pix = QPixmap(logo_path)
            if not pix.isNull():
                logo_label.setPixmap(pix.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_label.setFixedSize(32, 32)
                title_layout.addWidget(logo_label)

        self.lbl_title = QLabel("")
        self.lbl_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_layout.addWidget(self.lbl_title)

        self.lbl_sub = QLabel("")
        self.lbl_sub.setObjectName("SubTitleLabel")
        self.lbl_sub.setFont(QFont("Segoe UI", 9))
        title_layout.addWidget(self.lbl_sub)
        title_layout.addStretch()

        self.btn_settings = QPushButton("")
        self.btn_settings.setFixedSize(100, 35)
        self.set_button_icon(self.btn_settings, "settings.svg", 16)
        self.btn_settings.clicked.connect(self.show_settings)
        title_layout.addWidget(self.btn_settings)

        self.btn_about = QPushButton("")
        self.btn_about.setFixedSize(100, 35)
        self.set_button_icon(self.btn_about, "info.svg", 16)
        self.btn_about.clicked.connect(self.show_about)
        title_layout.addWidget(self.btn_about)

        main_layout.addWidget(title_frame)

        top_frame = self.make_card()
        top_layout = QVBoxLayout(top_frame)
        top_layout.setContentsMargins(20, 15, 20, 15)
        top_layout.setSpacing(12)

        self.lbl_s1 = QLabel("")
        self.lbl_s1.setFont(QFont("Segoe UI", 12))
        top_layout.addWidget(self.lbl_s1)

        src_layout = QHBoxLayout()
        src_layout.setSpacing(10)

        self.entry_source = QLineEdit()
        self.entry_source.setMinimumHeight(38)
        src_layout.addWidget(self.entry_source, 1)

        self.btn_browse = QPushButton("")
        self.btn_browse.setFixedSize(80, 38)
        self.btn_browse.clicked.connect(self.browse_source)
        src_layout.addWidget(self.btn_browse)

        top_layout.addLayout(src_layout)
        main_layout.addWidget(top_frame)

        auto_frame = self.make_card()
        auto_layout = QVBoxLayout(auto_frame)
        auto_layout.setContentsMargins(20, 15, 20, 15)
        auto_layout.setSpacing(12)

        self.lbl_s2 = QLabel("")
        self.lbl_s2.setFont(QFont("Segoe UI", 12))
        auto_layout.addWidget(self.lbl_s2)

        chk_grid = QGridLayout()
        chk_grid.setHorizontalSpacing(24)
        chk_grid.setVerticalSpacing(8)

        self.chk_type = QCheckBox("")
        self.chk_date_c = QCheckBox("")
        self.chk_date_m = QCheckBox("")
        self.chk_size = QCheckBox("")
        self.chk_name = QCheckBox("")
        self.chk_ext = QCheckBox("")
        self.chk_resolution = QCheckBox("")
        self.chk_codec = QCheckBox("")
        self.chk_artist = QCheckBox("")
        self.chk_album = QCheckBox("")

        chk_grid.addWidget(self.chk_type, 0, 0, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_date_c, 0, 1, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_date_m, 1, 1, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_ext, 1, 2, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_resolution, 0, 3, alignment=Qt.AlignLeft)

        chk_grid.addWidget(self.chk_size, 1, 0, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_name, 0, 2, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_codec, 1, 3, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_artist, 0, 4, alignment=Qt.AlignLeft)
        chk_grid.addWidget(self.chk_album, 1, 4, alignment=Qt.AlignLeft)
        
        chk_grid.setColumnStretch(0, 0)
        chk_grid.setColumnStretch(1, 0)
        chk_grid.setColumnStretch(2, 0)
        chk_grid.setColumnStretch(3, 0)
        chk_grid.setColumnStretch(4, 0)
        chk_grid.setColumnStretch(5, 1)

        auto_layout.addLayout(chk_grid)
        main_layout.addWidget(auto_frame)

        rules_frame = self.make_card()
        rules_layout = QVBoxLayout(rules_frame)
        rules_layout.setContentsMargins(5, 5, 5, 5)
        rules_layout.setSpacing(8)

        rules_header = QHBoxLayout()
        rules_header.setContentsMargins(15, 10, 15, 0)
        self.lbl_s3 = QLabel("")
        self.lbl_s3.setFont(QFont("Segoe UI", 12))
        rules_header.addWidget(self.lbl_s3)
        rules_header.addStretch()

        self.btn_add_rule = QPushButton("")
        self.btn_add_rule.setFixedSize(140, 30)
        self.btn_add_rule.clicked.connect(self.add_rule_row)
        rules_header.addWidget(self.btn_add_rule)

        rules_layout.addLayout(rules_header)

        self.rules_scroll = QScrollArea()
        self.rules_scroll.setWidgetResizable(True)
        self.rules_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rules_scroll.setMinimumHeight(170)

        self.rules_container = QWidget()
        self.rules_container_layout = QVBoxLayout(self.rules_container)
        self.rules_container_layout.setContentsMargins(15, 5, 15, 5)
        self.rules_container_layout.setSpacing(8)
        self.rules_container_layout.addStretch()

        self.rules_scroll.setWidget(self.rules_container)
        rules_layout.addWidget(self.rules_scroll, 1)

        main_layout.addWidget(rules_frame, 1)

        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        self.btn_dupes = QPushButton("")
        self.btn_dupes.setFixedSize(140, 45)
        self.set_button_icon(self.btn_dupes, "duplicate.svg", 16)
        self.btn_dupes.clicked.connect(self.start_find_duplicates)
        bottom_layout.addWidget(self.btn_dupes)

        self.btn_undo = QPushButton("")
        self.btn_undo.setFixedSize(140, 45)
        self.set_button_icon(self.btn_undo, "undo.svg", 16)
        self.btn_undo.clicked.connect(self.start_undo_last_action)
        bottom_layout.addWidget(self.btn_undo)

        bottom_layout.addStretch()

        self.btn_sim = QPushButton("")
        self.btn_sim.setFixedSize(140, 45)
        self.set_button_icon(self.btn_sim, "simulate.svg", 16)
        self.btn_sim.clicked.connect(lambda: self.start_execute_rules(simulate=True, cursor_widget=self.btn_sim))
        bottom_layout.addWidget(self.btn_sim)

        self.btn_run = QPushButton("")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.setFixedSize(160, 45)
        self.btn_run.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.set_button_icon(self.btn_run, "play.svg", 16)
        self.btn_run.clicked.connect(lambda: self.start_execute_rules(simulate=False, cursor_widget=self.btn_run))
        bottom_layout.addWidget(self.btn_run)

        main_layout.addWidget(bottom_frame)
        
        self.apply_clickable_cursors()        

    def make_card(self):
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def update_texts(self):
        t = LANGS[self.current_lang]

        self.lbl_title.setText(t["title"])
        self.lbl_sub.setText(t["sub"])
        self.btn_settings.setText(" " + t["settings"])
        self.btn_about.setText(" " + t["about"])

        self.lbl_s1.setText(t["s1"])
        self.btn_browse.setText(t["browse"])
        self.entry_source.setPlaceholderText(t["ph_src"])

        self.lbl_s2.setText(t["s2"])
        self.chk_type.setText(t["t_type"])
        self.chk_date_c.setText(t["t_date_c"])
        self.chk_date_m.setText(t["t_date_m"])
        self.chk_size.setText(t["t_size"])
        self.chk_name.setText(t["t_name"])
        self.chk_ext.setText(t.get("t_ext", "Extension"))
        self.chk_resolution.setText(t.get("t_resolution", "Resolution"))
        self.chk_codec.setText(t.get("t_codec", "Codec"))
        self.chk_artist.setText(t.get("t_artist", "Artist"))
        self.chk_album.setText(t.get("t_album", "Album"))

        self.lbl_s3.setText(t["s3"])
        self.btn_add_rule.setText(t["add_rule"])

        self.btn_run.setText(" " + t["btn_run"])
        self.btn_sim.setText(" " + t["btn_sim"])
        self.btn_undo.setText(" " + t["btn_undo"])
        self.btn_dupes.setText(" " + t["btn_dupes"])

        opts = self.get_rule_options()
        values = list(opts.values())

        for r in self.rules:
            r["menu"].blockSignals(True)
            r["menu"].clear()
            r["menu"].addItems(values)
            r["menu"].setCurrentText(opts[r["current_key"]])
            r["menu"].blockSignals(False)

            self.set_placeholder_by_key(r["current_key"], r["val"])
            r["lbl_folder"].setText(t["folder"])
            if "folder_icon" in r:
                folder_icon_path = self.get_icon_path("folder.svg")

                if os.path.exists(folder_icon_path):
                    folder_pix = QPixmap(folder_icon_path)
                    r["folder_icon"].setPixmap(folder_pix.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))            
            r["dest"].setPlaceholderText(t["ph_dest"])

    def get_rule_options(self):
        t = LANGS[self.current_lang]
        return {
            "name": t["r_name"], "name_not": t["r_name_not"],
            "name_starts": t["r_name_starts"], "name_ends": t["r_name_ends"],
            "ext": t["r_ext"], "ext_not": t["r_ext_not"],
            "size_gt": t["r_size_gt"], "size_lt": t["r_size_lt"],
            "date_c": t["r_date_c"], "date_c_after": t["r_date_c_after"],
            "date_m": t["r_date_m"], "date_m_after": t["r_date_m_after"],
        }

    def set_placeholder_by_key(self, key, entry_widget):
        t = LANGS[self.current_lang]

        if "name" in key:
            entry_widget.setPlaceholderText(t["ph_name"])
        elif "ext" in key:
            entry_widget.setPlaceholderText(t["ph_ext"])
        elif "size" in key:
            entry_widget.setPlaceholderText(t["ph_size"])
        elif "date" in key:
            entry_widget.setPlaceholderText(t["ph_date"])

    def show_settings(self):
        self.fix_ghost_cursor()
        self.settings_win = QDialog(self)
        set_win = self.settings_win
        set_win.setWindowTitle(LANGS[self.current_lang]["settings"])
        set_win.setFixedSize(400, 300)
        set_win.setWindowModality(Qt.ApplicationModal)
        self.apply_window_icon(set_win)

        layout = QVBoxLayout(set_win)
        layout.setContentsMargins(40, 20, 40, 25)
        layout.setSpacing(18)

        title = QLabel(LANGS[self.current_lang]["settings"])
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(20)

        master_lang_map = {
            "en": "English", "pt": "Português", "es": "Español",
            "fr": "Français", "de": "Deutsch", "it": "Italiano",
            "ja": "日本語", "ko": "한국어", "ru": "Русский"
        }

        lang_map = {k: master_lang_map[k] for k in LANGS.keys() if k in master_lang_map}
        rev_lang_map = {v: k for k, v in lang_map.items()}

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))
        lang_row.addStretch()
        lang_menu = QComboBox()
        lang_menu.addItems(list(lang_map.values()))
        lang_menu.setFixedWidth(180)
        safe_lang = self.current_lang if self.current_lang in lang_map else "en"
        lang_menu.setCurrentText(lang_map[safe_lang])
        lang_row.addWidget(lang_menu)
        layout.addLayout(lang_row)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        theme_row.addStretch()
        theme_menu = QComboBox()
        theme_menu.addItems(["Dark", "Light"])
        theme_menu.setFixedWidth(180)
        theme_menu.setCurrentText(self.current_theme)
        theme_row.addWidget(theme_menu)
        layout.addLayout(theme_row)

        layout.addStretch()

        btn_save = QPushButton("Save")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedWidth(140)
        btn_save.setFixedHeight(35)

        def save_settings():
            self.current_lang = rev_lang_map[lang_menu.currentText()]
            self.current_theme = theme_menu.currentText()
            self.apply_theme()
            self.update_texts()
            self.apply_titlebar_theme()
            
            self.set_button_icon(self.btn_about, "info.svg", 16)
            self.set_button_icon(self.btn_settings, "settings.svg", 16)
            self.set_button_icon(self.btn_dupes, "duplicate.svg", 16)
            self.set_button_icon(self.btn_undo, "undo.svg", 16)
            self.set_button_icon(self.btn_sim, "simulate.svg", 16)
            self.set_button_icon(self.btn_run, "play.svg", 16)            

            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"lang": self.current_lang, "theme": self.current_theme}, f)

            set_win.close()

        btn_save.clicked.connect(save_settings)
        layout.addWidget(btn_save, 0, Qt.AlignCenter)

        self.apply_clickable_cursors(set_win)
        self.apply_titlebar_theme(set_win)
        set_win.show()
        self.center_window(set_win, 400, 300)

    def show_about(self):
        self.fix_ghost_cursor()
        self.about_win = QDialog(self)
        self.about_win.setWindowTitle(LANGS[self.current_lang].get("about", "About"))
        self.about_win.setFixedSize(640, 500)
        self.about_win.setWindowModality(Qt.ApplicationModal)
        self.apply_window_icon(self.about_win)

        main_layout = QVBoxLayout(self.about_win)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 10, 0, 10)
        content_layout.setSpacing(10)

        title = QLabel("Zarfolder")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        content_layout.addWidget(title)

        content_layout.addSpacing(-5)

        version = QLabel(f"Version {self.version}")
        version.setObjectName("MutedLabel")
        version.setFont(QFont("Segoe UI", 10))
        content_layout.addWidget(version)

        content_layout.addSpacing(10)

        dev = QLabel("Developed by DanMixerBR")
        dev.setFont(QFont("Segoe UI", 12, QFont.Bold))
        content_layout.addWidget(dev)

        content_layout.addSpacing(30)

        desc_text = LANGS[self.current_lang].get("desc", "")
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 10))
        content_layout.addWidget(desc)
        
        content_layout.addSpacing(30)

        self.update_status_lbl = QLabel("")
        self.update_status_lbl.setObjectName("MutedLabel")
        content_layout.addWidget(self.update_status_lbl)

        self.update_progress = QProgressBar()
        self.update_progress.setRange(0, 100)
        self.update_progress.setValue(0)
        self.update_progress.setTextVisible(False)
        self.update_progress.hide()
        content_layout.addWidget(self.update_progress)

        content_layout.addStretch()
        scroll.setWidget(content)

        main_layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_github = QPushButton("GitHub")
        btn_github.setFixedWidth(120)
        btn_github.setFixedHeight(35)
        self.set_button_icon(btn_github, "github.svg", 16)
        btn_github.clicked.connect(lambda: webbrowser.open_new("https://github.com/DanMixerBR/Zarfolder"))
        btn_row.addWidget(btn_github)

        self.btn_update_app = QPushButton(LANGS[self.current_lang].get("btn_update", "Check for updates"))
        self.btn_update_app.setObjectName("PrimaryButton")
        self.btn_update_app.setFixedWidth(160)
        self.btn_update_app.setFixedHeight(35)
        self.btn_update_app.clicked.connect(self.start_github_update)
        btn_row.addWidget(self.btn_update_app)

        btn_row.addStretch()
        main_layout.addLayout(btn_row)

        self.apply_clickable_cursors(self.about_win)
        self.apply_titlebar_theme(self.about_win)
        self.about_win.show()
        self.center_window(self.about_win, 640, 500)

    # ==========================================
    # UPDATE
    # ==========================================
    def handle_update_failure(self, error_msg):
        if self.update_status_lbl:
            self.update_status_lbl.setText("Update Failed!")

        parent_win = self.about_win if self.about_win else self
        self.show_error("Update Error", error_msg, parent_win)

    def start_github_update(self):
        if self.operation_running:
            self.show_warning("Warning", "Please wait for the current operation to finish.", self)
            return

        if not self.btn_update_app:
            return

        self.btn_update_app.setEnabled(False)
        self.btn_update_app.setText("Checking...")
        self.is_updating = True

        if self.update_progress:
            self.update_progress.show()
            self.update_progress.setValue(0)

        if self.update_status_lbl:
            self.update_status_lbl.setText("Checking for updates...")

        threading.Thread(target=self.check_github_version_task, daemon=True).start()

    def check_github_version_task(self):
        api_url = "https://api.github.com/repos/DanMixerBR/Zarfolder/releases/latest"

        try:
            local_v = self.get_local_version()
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            remote_v = data.get("tag_name")

            if not remote_v:
                raise Exception("Could not detect latest version from GitHub API payload.")

            clean_remote_v = "".join(filter(lambda x: x.isdigit() or x == ".", remote_v))

            if not clean_remote_v:
                raise Exception("Invalid version format received from GitHub API.")

            if clean_remote_v != local_v:
                self.safe_ui(self.prompt_user_update, local_v, clean_remote_v)
            else:
                self.is_updating = False
                self.safe_ui(self.show_info, "Up to date", "You are already using the latest version.", self.about_win or self)
                self.safe_ui(lambda: self.update_status_lbl.setText("") if self.update_status_lbl else None)
                self.safe_ui(lambda: self.update_progress.hide() if self.update_progress else None)
                self.safe_ui(self.set_button_enabled_text, self.btn_update_app, True, LANGS[self.current_lang].get("btn_update", "Check for updates"))

        except Exception as e:
            self.is_updating = False
            self.safe_ui(self.handle_update_failure, str(e))
            self.safe_ui(self.set_button_enabled_text, self.btn_update_app, True, LANGS[self.current_lang].get("btn_update", "Check for updates"))

    def prompt_user_update(self, local_v, clean_remote_v):
        msg = f"Current version: {local_v}\nLatest version: {clean_remote_v}\n\nDo you want to update?"
        parent_win = self.about_win or self

        if self.ask_yes_no("Update available", msg, parent_win):
            if self.update_status_lbl:
                self.update_status_lbl.setText("Preparing update...")

            threading.Thread(target=self.download_and_install_task, daemon=True).start()
        else:
            self.is_updating = False

            if self.update_status_lbl:
                self.update_status_lbl.setText("Update cancelled.")

            if self.update_progress:
                self.update_progress.hide()

            if self.btn_update_app:
                self.btn_update_app.setEnabled(True)
                self.btn_update_app.setText(LANGS[self.current_lang].get("btn_update", "Check for updates"))

    def download_and_install_task(self):
        download_url_windows = "https://github.com/DanMixerBR/Zarfolder/releases/latest/download/Zarfolder_Windows.zip"
        download_url_linux = "https://github.com/DanMixerBR/Zarfolder/releases/latest/download/Zarfolder_Linux.zip"

        script_ext = "bat" if self.is_windows else "sh"
        script_url = f"https://raw.githubusercontent.com/DanMixerBR/Zarfolder/refs/heads/main/update.{script_ext}"
        hash_url = "https://raw.githubusercontent.com/DanMixerBR/Zarfolder/refs/heads/main/hash.txt"
        zip_platform = "Zarfolder_Windows.zip" if self.is_windows else "Zarfolder_Linux.zip"

        dir_app = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
        script_path = os.path.join(dir_app, f"update.{script_ext}")
        zip_path = os.path.join(dir_app, zip_platform)

        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)

            self.safe_ui(lambda: self.update_status_lbl.setText("Starting update...") if self.update_status_lbl else None)
            self.safe_ui(self.set_progress_fraction, 0.0)

            target_url = download_url_windows if self.is_windows else download_url_linux

            r = requests.get(target_url, stream=True, timeout=30)
            r.raise_for_status()

            total_size = int(r.headers.get("content-length", 0))
            downloaded_size = 0
            last_reported_progress = 0.0

            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

                        if total_size > 0:
                            downloaded_size += len(chunk)
                            download_percent = downloaded_size / total_size
                            actual_progress = download_percent * 0.5

                            if actual_progress - last_reported_progress >= 0.01 or downloaded_size == total_size:
                                display_percent = int(actual_progress * 100)
                                self.safe_ui(lambda p=display_percent: self.update_status_lbl.setText(f"Downloading update... {p}%") if self.update_status_lbl else None)
                                self.safe_ui(self.set_progress_fraction, actual_progress)
                                last_reported_progress = actual_progress

            zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            if zip_size_mb < 10.0:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                raise Exception(f"ERROR: The file '{zip_platform}' is suspiciously small ({zip_size_mb:.1f} MB). Update aborted.")

            self.safe_ui(lambda: self.update_status_lbl.setText("Verifying update... 50%") if self.update_status_lbl else None)
            self.safe_ui(self.set_progress_fraction, 0.5)

            with zipfile.ZipFile(zip_path, "r") as zf:
                corrupt_file = zf.testzip()

            if corrupt_file is not None:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                raise Exception(f"ERROR: The file '{zip_platform}' structure is corrupted.")

            r_hash = requests.get(hash_url, timeout=10)
            if r_hash.status_code == 200:
                expected_hashes = [
                    line.strip().lower().replace("sha256:", "")
                    for line in r_hash.text.splitlines()
                    if line.strip()
                ]

                sha256_hash = hashlib.sha256()
                with open(zip_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)

                if sha256_hash.hexdigest().lower() not in expected_hashes:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                    raise Exception(f"Security Error: '{zip_platform}' failed Hash verification!")
            else:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                raise Exception(f"Security Error: Could not download hash.txt to verify '{zip_platform}'.")

            self.safe_ui(lambda: self.update_status_lbl.setText("Preparing update... 75%") if self.update_status_lbl else None)
            self.safe_ui(self.set_progress_fraction, 0.75)

            r_script = requests.get(script_url, timeout=10)
            r_script.raise_for_status()

            expected_hashes = [
                line.strip().lower().replace("sha256:", "")
                for line in r_hash.text.splitlines()
                if line.strip()
            ]

            script_hash = hashlib.sha256(r_script.content).hexdigest().lower()

            if script_hash not in expected_hashes:
                raise Exception(f"Security Error: update.{script_ext} failed Hash verification!")

            with open(script_path, "wb") as f:
                f.write(r_script.content)

            self.safe_ui(lambda: self.update_status_lbl.setText("Update Ready! (100%)") if self.update_status_lbl else None)
            self.safe_ui(self.set_progress_fraction, 1.0)

            def finish_update_and_restart():
                parent_win = self.about_win or self
                self.show_info("Success", "Update Ready! The app will close to complete the update.", parent_win)

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
                        clean_env = os.environ.copy()
                        clean_env.pop("LD_LIBRARY_PATH", None)
                        clean_env.pop("GTK_PATH", None)

                        comando_bash = f'cd "{dir_app}" && bash update.sh'
                        terminais = [
                            ["x-terminal-emulator", "-e"],
                            ["gnome-terminal", "--"],
                            ["konsole", "-e"],
                            ["xfce4-terminal", "-x"]
                        ]

                        opened_terminal = False
                        for term in terminais:
                            try:
                                subprocess.Popen(term + ["bash", "-c", comando_bash], env=clean_env, start_new_session=True)
                                opened_terminal = True
                                break
                            except Exception:
                                continue

                        if not opened_terminal:
                            subprocess.Popen(["bash", script_path], env=clean_env, start_new_session=True)

                os._exit(0)

            self.safe_ui(finish_update_and_restart)

        except Exception as e:
            self.is_updating = False
            self.safe_ui(self.handle_update_failure, str(e))
            self.safe_ui(self.set_button_enabled_text, self.btn_update_app, True, LANGS[self.current_lang].get("btn_update", "Check for updates"))

    # ==========================================
    # CONFIGURAÇÕES E DIÁLOGOS NATIVOS
    # ==========================================
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get("lang", "en")
                    self.current_theme = cfg.get("theme", "Light")
            except Exception:
                pass

    def native_askdirectory(self, title="Choose Directory"):
        if self.is_windows:
            return QFileDialog.getExistingDirectory(self, title, "")

        clean_env = os.environ.copy()
        clean_env.pop("LD_LIBRARY_PATH", None)
        clean_env.pop("GTK_PATH", None)

        if self.linux_dialog_tool == "zenity":
            res = subprocess.run(
                ["zenity", "--file-selection", "--directory", f"--title={title}"],
                capture_output=True,
                text=True,
                env=clean_env
            )
            return res.stdout.strip() if res.returncode == 0 else ""

        if self.linux_dialog_tool == "kdialog":
            res = subprocess.run(
                ["kdialog", "--getexistingdirectory", "/", "--title", title],
                capture_output=True,
                text=True,
                env=clean_env
            )
            return res.stdout.strip() if res.returncode == 0 else ""

        return QFileDialog.getExistingDirectory(self, title, "")

    def browse_source(self):
        folder = self.native_askdirectory(title="Select Folder")
        if folder:
            self.entry_source.setText(folder)

    # ==========================================
    # REGRAS
    # ==========================================
    def add_rule_row(self):
        if len(self.rules) >= self.MAX_RULES:
            return

        insert_index = max(0, self.rules_container_layout.count() - 1)

        rule_frame = QFrame()
        rule_frame.setObjectName("RuleRow")
        rule_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row_layout = QHBoxLayout(rule_frame)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)

        t = LANGS[self.current_lang]
        opts = self.get_rule_options()
        rule_dict = {"frame": rule_frame, "current_key": "name"}

        attr_menu = QComboBox()
        attr_menu.addItems(list(opts.values()))
        attr_menu.setCurrentText(opts["name"])
        attr_menu.setFixedWidth(250)
        row_layout.addWidget(attr_menu)

        val_entry = QLineEdit()
        val_entry.setObjectName("RuleLineEdit")
        val_entry.setPlaceholderText(t["ph_name"])
        val_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_layout.addWidget(val_entry, 1)

        folder_icon = QLabel()
        folder_icon_path = self.get_icon_path("folder.svg")

        if os.path.exists(folder_icon_path):
            folder_pix = QPixmap(folder_icon_path)
            folder_icon.setPixmap(folder_pix.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        folder_icon.setFixedSize(14, 14)
        row_layout.addWidget(folder_icon)
        
        row_layout.addSpacing(-6)

        lbl_folder = QLabel(t["folder"])
        row_layout.addWidget(lbl_folder)

        dest_entry = QLineEdit()
        dest_entry.setObjectName("RuleLineEdit")
        dest_entry.setPlaceholderText(t["ph_dest"])
        dest_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row_layout.addWidget(dest_entry, 1)

        btn_remove = QPushButton("X")
        btn_remove.setObjectName("DangerButton")
        btn_remove.setFixedSize(30, 30)
        row_layout.addWidget(btn_remove, 1)

        def on_option_change(choice):
            opts_rev = {v: k for k, v in self.get_rule_options().items()}
            rule_dict["current_key"] = opts_rev.get(choice, "name")
            self.set_placeholder_by_key(rule_dict["current_key"], val_entry)

        def remove_self():
            self.rules_container_layout.removeWidget(rule_frame)
            rule_frame.deleteLater()
            if rule_dict in self.rules:
                self.rules.remove(rule_dict)

        attr_menu.currentTextChanged.connect(on_option_change)
        btn_remove.clicked.connect(remove_self)

        rule_dict.update({
            "menu": attr_menu,
            "val": val_entry,
            "dest": dest_entry,
            "lbl_folder": lbl_folder,
            "folder_icon": folder_icon
        })

        self.rules.append(rule_dict)
        self.rules_container_layout.insertWidget(insert_index, rule_frame)
        self.apply_clickable_cursors(rule_frame)        

    # ==========================================
    # SISTEMA DE ARQUIVOS
    # ==========================================
    def force_move(self, src, dst):
        try:
            os.chmod(src, stat.S_IWRITE)
        except Exception:
            pass

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
            for d in dirs:
                dir_set.add(os.path.join(root, d))
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

    def get_unique_path(self, dest_folder, filename, original_filepath, reserved_paths=None):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_path = os.path.join(dest_folder, filename)

        if original_filepath == new_path:
            return new_path

        if reserved_paths is None:
            reserved_paths = set()

        while os.path.exists(new_path) or new_path in reserved_paths:
            new_path = os.path.join(dest_folder, f"{base} ({counter}){ext}")
            counter += 1

        reserved_paths.add(new_path)

        return new_path

    # ==========================================
    # DUPLICATAS
    # ==========================================
    def start_find_duplicates(self):
        self.fix_ghost_cursor(self.btn_dupes)
        src = self.entry_source.text().strip()
        if not os.path.exists(src):
            return

        if not self.begin_operation():
            return

        self.show_loading("load_title", "load_dupes")
        threading.Thread(target=self._task_find_duplicates, args=(src,), daemon=True).start()

    def _task_find_duplicates(self, src):
        dupes_folder = os.path.join(src, "Duplicates")
        moved = 0
        moves_dict = {}
        created_dirs = []        

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
                            self.ensure_dir(dupes_folder, created_dirs)

                            file = os.path.basename(filepath)
                            safe_path = self.get_unique_path(dupes_folder, file, filepath)
                            self.force_move(filepath, safe_path)

                            moves_dict[safe_path] = filepath
                            moved += 1
                        else:
                            full_hashes[full_hash] = filepath

                    except Exception:
                        pass

            if moved > 0:
                self.add_undo_action("duplicates", moves_dict, created_dirs, [])

        finally:
            self.safe_ui(self.finish_operation)
            self.safe_ui(self.show_info, "Duplicatas", LANGS[self.current_lang]["msg_dupes"].format(moved), self)

    # ==========================================
    # UNDO
    # ==========================================
    def start_undo_last_action(self):
        self.fix_ghost_cursor(self.btn_undo)
        if not os.path.exists(self.undo_file):
            return

        if not self.begin_operation():
            return

        self.show_loading("load_title", "load_undo")
        threading.Thread(target=self._task_undo_last_action, daemon=True).start()

    def _task_undo_last_action(self):
        restored = 0

        try:
            history = self.load_undo_history()

            if not history:
                return

            last_action = history.pop()

            moves = last_action.get("moves", {})
            created_dirs = last_action.get("created_dirs", [])
            deleted_dirs = last_action.get("deleted_dirs", [])

            for d in deleted_dirs:
                try:
                    os.makedirs(d, exist_ok=True)
                except Exception:
                    pass

            for current_pos, original_pos in moves.items():
                if os.path.exists(current_pos):
                    try:
                        original_dir = os.path.dirname(original_pos)
                        os.makedirs(original_dir, exist_ok=True)
                        self.force_move(current_pos, original_pos)
                        restored += 1
                    except Exception:
                        pass

            created_dirs.sort(key=len, reverse=True)

            for d in created_dirs:
                self.remove_empty_folders(d, remove_root=True)

            self.save_undo_history(history)

        finally:
            self.safe_ui(self.finish_operation)
            self.safe_ui(lambda: QTimer.singleShot(200, lambda: self.show_info("Undo", LANGS[self.current_lang]["msg_undo"].format(restored), self)))

    # ==========================================
    # ORGANIZAÇÃO E SIMULAÇÃO
    # ==========================================
    def start_execute_rules(self, simulate=False, cursor_widget=None):
        self.fix_ghost_cursor(cursor_widget)
        src = self.entry_source.text().strip()
        if not os.path.exists(src):
            return

        active_rules = []

        for r in self.rules:
            val = r["val"].text().strip()
            folder_name = r["dest"].text().strip()

            if val and folder_name:
                clean_folder = "".join(c for c in folder_name if c not in r'\/:*?"<>|')
                if clean_folder:
                    active_rules.append({
                        "key": r["current_key"],
                        "val": val,
                        "dest": clean_folder
                    })

        auto_opts = {
            "type": self.chk_type.isChecked(),
            "date_c": self.chk_date_c.isChecked(),
            "date_m": self.chk_date_m.isChecked(),
            "size": self.chk_size.isChecked(),
            "name": self.chk_name.isChecked(),
            "ext": self.chk_ext.isChecked(),
            "resolution": self.chk_resolution.isChecked(),
            "codec": self.chk_codec.isChecked(),
            "artist": self.chk_artist.isChecked(),
            "album": self.chk_album.isChecked()
        }

        has_auto = any(auto_opts.values())

        if not active_rules and not has_auto:
            self.show_warning("Warning", "Please select at least one automatic classification option or define a rule.", self)
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
        self._media_info_cache = {}
        self._audio_tags_cache = {}

        def add_sim_move(file_name, destination):
            if len(sim_moves) < sim_moves_limit:
                sim_moves.append((file_name, destination))

        moves_dict = {}
        created_dirs = []
        reserved_paths = set()

        try:
            for filepath in file_iterator:
                if not os.path.exists(filepath):
                    continue

                file = os.path.basename(filepath)
                file_lower = file.lower()
                file_root, ext = os.path.splitext(file)
                ext = ext.lower()
                base_name = file_root.lower()

                final_dest = None

                for rule in active_rules:
                    match = False
                    rule_val = rule["val"].lower()

                    if rule["key"] == "ext" and ext == rule_val:
                        match = True
                    elif rule["key"] == "ext_not" and ext != rule_val:
                        match = True

                    elif rule["key"] == "name" and rule_val in file_lower:
                        match = True
                    elif rule["key"] == "name_not" and rule_val not in file_lower:
                        match = True
                    elif rule["key"] == "name_starts" and base_name.startswith(rule_val):
                        match = True
                    elif rule["key"] == "name_ends" and base_name.endswith(rule_val):
                        match = True
                    elif rule["key"] == "name_exact" and base_name == rule_val:
                        match = True

                    elif rule["key"] == "size_gt":
                        try:
                            if (os.path.getsize(filepath) / (1024 * 1024)) > float(rule["val"]):
                                match = True
                        except Exception:
                            pass
                    elif rule["key"] == "size_lt":
                        try:
                            if (os.path.getsize(filepath) / (1024 * 1024)) < float(rule["val"]):
                                match = True
                        except Exception:
                            pass

                    elif rule["key"] == "date_c":
                        try:
                            if self.get_creation_date(filepath) < rule["val"]:
                                match = True
                        except Exception:
                            pass
                    elif rule["key"] == "date_c_after":
                        try:
                            if self.get_creation_date(filepath) > rule["val"]:
                                match = True
                        except Exception:
                            pass
                    elif rule["key"] == "date_c_exact":
                        try:
                            if self.get_creation_date(filepath) == rule["val"]:
                                match = True
                        except Exception:
                            pass

                    elif rule["key"] == "date_m":
                        try:
                            if self.get_modification_date(filepath) < rule["val"]:
                                match = True
                        except Exception:
                            pass
                    elif rule["key"] == "date_m_after":
                        try:
                            if self.get_modification_date(filepath) > rule["val"]:
                                match = True
                        except Exception:
                            pass
                    elif rule["key"] == "date_m_exact":
                        try:
                            if self.get_modification_date(filepath) == rule["val"]:
                                match = True
                        except Exception:
                            pass

                    if match:
                        final_dest = rule["dest"]
                        break

                if final_dest:
                    dest_folder = os.path.join(src, final_dest)
                    safe_new_path = self.get_unique_path(dest_folder, file, filepath, reserved_paths)

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
                            except Exception:
                                pass

                    continue

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
                        
                    if auto_opts["ext"]:
                        sub_paths.append(self.get_extension_category(file))

                    if auto_opts["resolution"]:
                        sub_paths.append(self.get_resolution_category(filepath))

                    if auto_opts["codec"]:
                        sub_paths.append(self.get_codec_category(filepath))

                    if auto_opts["artist"]:
                        sub_paths.append(self.get_artist_category(filepath))

                    if auto_opts["album"]:
                        sub_paths.append(self.get_album_category(filepath))                        

                    target_path = os.path.join(src, *sub_paths)
                    safe_new_path = self.get_unique_path(target_path, file, filepath, reserved_paths)

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
                            except Exception:
                                pass

            if simulate:
                self.safe_ui(self._generate_tree_and_finish, src, sim_moves)
            else:
                removed_dirs = self.remove_empty_folders(src)

                created_dirs_set = set(created_dirs)
                deleted_dirs = [d for d in removed_dirs if d not in created_dirs_set]

                created_dirs = list(dict.fromkeys(created_dirs))
                deleted_dirs = list(dict.fromkeys(deleted_dirs))

                self.add_undo_action("organize", moves_dict, created_dirs, deleted_dirs)

                self.safe_ui(self.finish_operation)
                self.safe_ui(lambda: QTimer.singleShot(200, lambda: self.show_info("Success", t["msg_success"].format(moved_count), self)))

        except Exception as e:
            self.safe_ui(self.finish_operation)
            print(f"Error: {e}")
        finally:
            if hasattr(self, "_media_info_cache"):
                self._media_info_cache.clear()

            if hasattr(self, "_audio_tags_cache"):
                self._audio_tags_cache.clear()

    def _generate_tree_and_finish(self, src, sim_moves):
        self.finish_operation()
        QTimer.singleShot(200, lambda: self._show_simulation_tree(src, sim_moves))

    def _show_simulation_tree(self, root_src, sim_moves):
        t = LANGS[self.current_lang]

        self.simulation_win = QDialog(self)
        sim_win = self.simulation_win
        sim_win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        sim_win.destroyed.connect(lambda: setattr(self, "simulation_win", None))
        sim_win.setWindowTitle(t["btn_sim"])
        sim_win.resize(650, 500)
        sim_win.setMinimumSize(650, 500)
        sim_win.setWindowModality(Qt.ApplicationModal)
        self.apply_window_icon(sim_win)

        layout = QVBoxLayout(sim_win)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Preview of Organized Folders")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        container = self.make_card()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        if not sim_moves:
            lbl = QLabel("No files matched the current rules.")
            lbl.setObjectName("MutedLabel")
            lbl.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(lbl)
            layout.addWidget(container, 1)

            self.apply_clickable_cursors(sim_win)
            self.apply_titlebar_theme(sim_win)
            sim_win.show()
            self.center_window(sim_win, 650, 500)
            return

        tree_widget = QTreeWidget()
        tree_widget.setHeaderHidden(True)
        tree_widget.setIndentation(12)
        container_layout.addWidget(tree_widget)

        tree = {}
        for original_file, dest_path in sim_moves:
            rel_path = os.path.relpath(dest_path, root_src).replace("\\", "/")
            parts = rel_path.split("/")

            current_level = tree
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

            current_level[parts[-1]] = None

        def populate_tree(parent_item, node):
            folders = {k: v for k, v in node.items() if v is not None}
            files = {k: v for k, v in node.items() if v is None}

            for f_name, sub_node in sorted(folders.items()):
                item = QTreeWidgetItem([f"📁 {f_name}"])
                if parent_item is None:
                    tree_widget.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)

                populate_tree(item, sub_node)

            for file_name in sorted(files.keys()):
                item = QTreeWidgetItem([f"📄 {file_name}"])
                if parent_item is None:
                    tree_widget.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)

        tree_widget.setUpdatesEnabled(False)

        try:
            populate_tree(None, tree)
        finally:
            tree_widget.setUpdatesEnabled(True)

        layout.addWidget(container, 1)
        self.apply_clickable_cursors(sim_win)
        self.apply_titlebar_theme(sim_win)
        sim_win.show()
        self.center_window(sim_win, 650, 500)

    def safe_folder_part(self, value, fallback="Unknown"):
        value = str(value or "").strip()

        if not value:
            value = fallback

        value = "".join(c for c in value if c not in r'\/:*?"<>|')
        value = value.strip().strip(".")

        return value[:80] if value else fallback

    def get_extension_category(self, filename):
        ext = os.path.splitext(filename)[1].lower().strip(".")

        if not ext:
            return "No Extension"

        return self.safe_folder_part(ext.upper(), "No Extension")

    def get_media_info_cached(self, filepath):
        if not hasattr(self, "_media_info_cache"):
            self._media_info_cache = {}

        if filepath in self._media_info_cache:
            return self._media_info_cache[filepath]

        if MediaInfo is None:
            self._media_info_cache[filepath] = None
            return None

        try:
            info = MediaInfo.parse(filepath)
            self._media_info_cache[filepath] = info
            return info
        except Exception:
            self._media_info_cache[filepath] = None
            return None

    def is_close_to(self, value, targets, tolerance=16):
        value = int(value)

        for target in targets:
            if abs(value - int(target)) <= tolerance:
                return True

        return False

    def get_resolution_bucket(self, width, height, kind="video"):
        width = int(width)
        height = int(height)

        short_side = min(width, height)
        long_side = max(width, height)

        if kind == "image":
            megapixels = (width * height) / 1_000_000

            if megapixels < 1:
                return "Under 1MP"

            if megapixels < 3:
                return "1MP-3MP"

            if megapixels < 8:
                return "3MP-8MP"

            if megapixels < 16:
                return "8MP-16MP"

            return "Over 16MP"

        if self.is_close_to(long_side, (3840, 3996, 4096), tolerance=32) and short_side >= 1000:
            return "4K"

        if self.is_close_to(short_side, (1440,), tolerance=16) and long_side >= 1900:
            return "1440p"

        if self.is_close_to(short_side, (1080,), tolerance=16) and long_side >= 1440:
            return "1080p"

        if self.is_close_to(short_side, (720,), tolerance=16) and long_side >= 900:
            return "720p"

        if self.is_close_to(short_side, (480,), tolerance=16) and long_side >= 480:
            return "480p"

        return self.safe_folder_part(f"Custom {width}x{height}", "Unknown Resolution")

    def get_resolution_category(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext in IMAGE_EXTENSIONS:
                reader = QImageReader(filepath)
                size = reader.size()

                if size.isValid():
                    width = int(size.width())
                    height = int(size.height())

                    return self.get_resolution_bucket(width, height, kind="image")

            if ext in VIDEO_EXTENSIONS and MediaInfo is not None:
                media_info = self.get_media_info_cached(filepath)

                if media_info is None:
                    return "Unknown Resolution"

                for track in media_info.tracks:
                    if track.track_type == "Video" and track.width and track.height:
                        width = int(track.width)
                        height = int(track.height)

                        return self.get_resolution_bucket(width, height, kind="video")

        except Exception:
            pass

        return "Unknown Resolution"

    def get_codec_category(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()

        if ext not in VIDEO_EXTENSIONS and ext not in AUDIO_EXTENSIONS:
            return "Unknown Codec"

        if MediaInfo is None:
            return "Unknown Codec"

        try:
            media_info = self.get_media_info_cached(filepath)

            if media_info is None:
                return "Unknown Codec"

            for track in media_info.tracks:
                if track.track_type in ("Video", "Audio"):
                    codec = track.format or track.codec_id or track.commercial_name

                    if codec:
                        return self.safe_folder_part(codec, "Unknown Codec")
        except Exception:
            pass

        return "Unknown Codec"

    def get_audio_tags_cached(self, filepath):
        if not hasattr(self, "_audio_tags_cache"):
            self._audio_tags_cache = {}

        if filepath in self._audio_tags_cache:
            return self._audio_tags_cache[filepath]

        ext = os.path.splitext(filepath)[1].lower()

        if ext not in AUDIO_EXTENSIONS or MutagenFile is None:
            return {}

        try:
            audio = MutagenFile(filepath, easy=True)
            tags = dict(audio.tags) if audio and audio.tags else {}

            self._audio_tags_cache[filepath] = tags
            return tags
        except Exception:
            self._audio_tags_cache[filepath] = {}
            return {}

    def get_audio_tag(self, filepath, tag_name):
        tags = self.get_audio_tags_cached(filepath)
        values = tags.get(tag_name)

        if values:
            return self.safe_folder_part(values[0], "Unknown")

        return "Unknown"

    def get_artist_category(self, filepath):
        return self.get_audio_tag(filepath, "artist")

    def get_album_category(self, filepath):
        return self.get_audio_tag(filepath, "album")

    # ==========================================
    # CLASSIFICAÇÃO
    # ==========================================
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

        return "Other"

    def get_creation_date(self, filepath):
        try:
            return datetime.fromtimestamp(os.stat(filepath).st_birthtime).strftime("%Y-%m-%d")
        except Exception:
            return datetime.fromtimestamp(os.stat(filepath).st_ctime).strftime("%Y-%m-%d")

    def get_modification_date(self, filepath):
        return datetime.fromtimestamp(os.stat(filepath).st_mtime).strftime("%Y-%m-%d")

    def get_name_category(self, filename):
        return filename[0].upper() if filename and filename[0].isalpha() else "#"

    def get_size_category(self, filepath):
        mb = os.path.getsize(filepath) / (1024 * 1024)

        if mb < 10:
            return "Small (Under 10MB)"

        if mb <= 100:
            return "Medium (10MB-100MB)"

        return "Large (Over 100MB)"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec())
