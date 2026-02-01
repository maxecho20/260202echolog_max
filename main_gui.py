"""
EchoLog GUI - 智能听写助手 图形界面 v2.0
=============================================
Modern UI inspired by Typeless design.
Left sidebar navigation + Right content area.
"""

import asyncio
import threading
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import webbrowser

import customtkinter as ctk
from tkinter import filedialog, messagebox
from audio_engine import TranscriptionEngine
from config import GUIConfig, OutputConfig, DeepgramConfig


# ========================================
# Color Theme (Typeless-inspired)
# ========================================
class Colors:
    """Application color palette"""
    # Sidebar (dark)
    SIDEBAR_BG = "#1E1E2E"
    SIDEBAR_HOVER = "#2D2D3D"
    SIDEBAR_ACTIVE = "#3D3D4D"
    SIDEBAR_TEXT = "#B0B0B0"
    SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
    
    # Content area (light)
    CONTENT_BG = "#FAFAFA"
    CONTENT_CARD = "#FFFFFF"
    CONTENT_BORDER = "#E5E5E5"
    
    # Text colors
    TEXT_PRIMARY = "#1A1A2E"
    TEXT_SECONDARY = "#6B7280"
    TEXT_MUTED = "#9CA3AF"
    
    # Accent colors (Blue-Purple theme)
    ACCENT = "#6366F1"       # Indigo
    ACCENT_HOVER = "#4F46E5"
    ACCENT_LIGHT = "#E0E7FF"
    RECORDING = "#EF4444"
    RECORDING_HOVER = "#DC2626"
    PAUSED = "#F59E0B"
    DANGER = "#EF4444"
    DANGER_HOVER = "#DC2626"
    
    # Status
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"


# ========================================
# Navigation Item Widget
# ========================================
class NavItem(ctk.CTkFrame):
    """Sidebar navigation item"""
    
    def __init__(self, parent, icon: str, text: str, command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.command = command
        self._is_active = False
        
        # Configure
        self.configure(height=45, cursor="hand2")
        self.pack_propagate(False)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=18),
            text_color=Colors.SIDEBAR_TEXT,
            width=40,
        )
        self.icon_label.pack(side="left", padx=(15, 5))
        
        # Text
        self.text_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            text_color=Colors.SIDEBAR_TEXT,
            anchor="w",
        )
        self.text_label.pack(side="left", fill="x", expand=True)
        
        # Bind events
        for widget in [self, self.icon_label, self.text_label]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            
    def _on_enter(self, event):
        if not self._is_active:
            self.configure(fg_color=Colors.SIDEBAR_HOVER)
            
    def _on_leave(self, event):
        if not self._is_active:
            self.configure(fg_color="transparent")
            
    def _on_click(self, event):
        if self.command:
            self.command()
            
    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=Colors.SIDEBAR_ACTIVE)
            self.icon_label.configure(text_color=Colors.SIDEBAR_TEXT_ACTIVE)
            self.text_label.configure(text_color=Colors.SIDEBAR_TEXT_ACTIVE)
        else:
            self.configure(fg_color="transparent")
            self.icon_label.configure(text_color=Colors.SIDEBAR_TEXT)
            self.text_label.configure(text_color=Colors.SIDEBAR_TEXT)


# ========================================
# History Item Widget
# ========================================
class HistoryItem(ctk.CTkFrame):
    """History list item showing file info"""
    
    def __init__(self, parent, filepath: Path, on_click=None, on_delete=None, **kwargs):
        super().__init__(parent, fg_color=Colors.CONTENT_CARD, corner_radius=8, **kwargs)
        
        self.filepath = filepath
        self.on_click = on_click
        self.on_delete = on_delete
        self._delete_btn = None
        self._is_hovered = False
        
        # Configure
        self.configure(height=70, cursor="hand2")
        self.pack_propagate(False)
        
        # Parse file info
        filename = filepath.name
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        time_str = mod_time.strftime("%H:%M")
        date_str = mod_time.strftime("%Y-%m-%d")
        
        # Try to read first line of content
        preview = ""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() and not line.startswith("#") and not line.startswith(">") and not line.startswith("---"):
                        preview = line.strip()[:80]
                        if len(line.strip()) > 80:
                            preview += "..."
                        break
        except:
            preview = "无法读取内容"
            
        # Left content
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Time label
        self.time_label = ctk.CTkLabel(
            self.left_frame,
            text=time_str,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        )
        self.time_label.pack(anchor="w")
        
        # Preview text
        self.preview_label = ctk.CTkLabel(
            self.left_frame,
            text=preview if preview else "空文件",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            text_color=Colors.TEXT_PRIMARY if preview else Colors.TEXT_MUTED,
            anchor="w",
            wraplength=450,
        )
        self.preview_label.pack(anchor="w", pady=(3, 0))
        
        # Delete button - always packed but visibility controlled by opacity
        self._delete_btn = ctk.CTkButton(
            self,
            text="🗑️",
            font=ctk.CTkFont(size=14),
            width=35,
            height=35,
            corner_radius=17,
            fg_color="transparent",
            hover_color=Colors.DANGER,
            text_color="transparent",  # Initially invisible
            command=self._on_delete_click,
        )
        self._delete_btn.pack(side="right", padx=10)
        
        # Bind click events to left content area only (not delete button)
        for widget in [self, self.left_frame, self.time_label, self.preview_label]:
            widget.bind("<Button-1>", self._on_click)
        
        # Bind hover events to all widgets including delete button
        all_widgets = [self, self.left_frame, self.time_label, self.preview_label, self._delete_btn]
        for widget in all_widgets:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            
    def _is_mouse_inside(self, event):
        """Check if mouse is still inside the card area"""
        try:
            # Get card position and size
            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()
            
            # Get mouse position
            mouse_x = event.x_root
            mouse_y = event.y_root
            
            # Check if mouse is inside
            return x <= mouse_x <= x + w and y <= mouse_y <= y + h
        except:
            return False
            
    def _on_enter(self, event):
        self._is_hovered = True
        self.configure(fg_color="#F5F5F5")
        if self._delete_btn:
            self._delete_btn.configure(text_color=Colors.TEXT_MUTED)
        
    def _on_leave(self, event):
        # Only hide if mouse actually left the entire card
        if not self._is_mouse_inside(event):
            self._is_hovered = False
            self.configure(fg_color=Colors.CONTENT_CARD)
            if self._delete_btn:
                self._delete_btn.configure(text_color="transparent")
        
    def _on_click(self, event):
        if self.on_click:
            self.on_click(self.filepath)
            
    def _on_delete_click(self):
        if self.on_delete:
            self.on_delete(self.filepath)


# ========================================
# Main Application
# ========================================
class EchoLogApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # ========================================
        # Window Setup
        # ========================================
        self.title("EchoLog")
        self.geometry("1000x650")
        self.minsize(800, 500)
        
        # Set appearance
        ctk.set_appearance_mode("light")  # Light mode for content area
        ctk.set_default_color_theme("blue")
        
        # ========================================
        # State Management
        # ========================================
        self._is_recording = False
        self._is_paused = False
        self._engine: Optional[TranscriptionEngine] = None
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        self._async_thread: Optional[threading.Thread] = None
        self._current_interim_text = ""
        self._output_file: Optional[str] = None
        self._current_page = "home"
        self._nav_items = {}
        
        # ========================================
        # Build UI
        # ========================================
        self._build_ui()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Show home page by default
        self._show_page("home")
        
    def _build_ui(self):
        """Build the main UI layout"""
        
        # Main container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar - fixed width
        self.grid_columnconfigure(1, weight=1)  # Content - expandable
        
        # ========================================
        # Left Sidebar
        # ========================================
        self._sidebar = ctk.CTkFrame(self, fg_color=Colors.SIDEBAR_BG, corner_radius=0, width=200)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        
        # Logo
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=60)
        logo_frame.pack(fill="x", pady=(20, 30))
        logo_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_frame,
            text="🎙️ EchoLog",
            font=ctk.CTkFont(family="Microsoft YaHei", size=20, weight="bold"),
            text_color="#FFFFFF",
        ).pack(side="left", padx=20)
        
        # Navigation items
        self._nav_items["home"] = NavItem(
            self._sidebar, "🏠", "首页",
            command=lambda: self._show_page("home")
        )
        self._nav_items["home"].pack(fill="x", pady=2)
        
        self._nav_items["history"] = NavItem(
            self._sidebar, "📜", "历史记录",
            command=lambda: self._show_page("history")
        )
        self._nav_items["history"].pack(fill="x", pady=2)
        
        self._nav_items["settings"] = NavItem(
            self._sidebar, "⚙️", "设置",
            command=lambda: self._show_page("settings")
        )
        self._nav_items["settings"].pack(fill="x", pady=2)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=20)
        
        # Storage path indicator
        self._path_label = ctk.CTkLabel(
            bottom_frame,
            text=f"📁 {self._get_short_path()}",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=Colors.SIDEBAR_TEXT,
            wraplength=160,
        )
        self._path_label.pack(padx=15, pady=(0, 15))
        
        # Open folder button
        open_folder_btn = ctk.CTkButton(
            bottom_frame,
            text="📂 打开文件夹",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            fg_color=Colors.SIDEBAR_HOVER,
            hover_color=Colors.SIDEBAR_ACTIVE,
            height=35,
            corner_radius=8,
            command=self._open_output_folder,
        )
        open_folder_btn.pack(fill="x", padx=15, pady=(0, 10))
        
        # Help button
        NavItem(bottom_frame, "❓", "帮助", command=self._show_help).pack(fill="x", pady=2)
        
        # ========================================
        # Right Content Area
        # ========================================
        self._content_area = ctk.CTkFrame(self, fg_color=Colors.CONTENT_BG, corner_radius=0)
        self._content_area.grid(row=0, column=1, sticky="nsew")
        
        # Create page frames
        self._pages = {}
        self._pages["home"] = self._create_home_page()
        self._pages["history"] = self._create_history_page()
        self._pages["settings"] = self._create_settings_page()
        
    def _get_short_path(self) -> str:
        """Get shortened path for display"""
        path = str(OutputConfig.OUTPUT_DIR)
        if len(path) > 25:
            return "..." + path[-22:]
        return path
        
    # ========================================
    # Home Page (Recording)
    # ========================================
        
    def _create_home_page(self) -> ctk.CTkFrame:
        """Create the home/recording page"""
        page = ctk.CTkFrame(self._content_area, fg_color=Colors.CONTENT_BG)
        
        # Title
        title_frame = ctk.CTkFrame(page, fg_color="transparent", height=60)
        title_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="实时听写",
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")
        
        # Status indicator
        self._status_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        self._status_frame.pack(side="right")
        
        self._status_dot = ctk.CTkLabel(
            self._status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=Colors.SUCCESS,
        )
        self._status_dot.pack(side="left", padx=(0, 5))
        
        self._status_label = ctk.CTkLabel(
            self._status_frame,
            text="就绪",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            text_color=Colors.TEXT_SECONDARY,
        )
        self._status_label.pack(side="left")
        
        # Text display card
        text_card = ctk.CTkFrame(page, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        text_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Current file indicator
        self._file_indicator = ctk.CTkLabel(
            text_card,
            text="📄 点击「开始录音」创建新文件",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_MUTED,
        )
        self._file_indicator.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Text display
        self._text_display = ctk.CTkTextbox(
            text_card,
            font=ctk.CTkFont(family="Microsoft YaHei", size=15),
            wrap="word",
            state="disabled",
            fg_color=Colors.CONTENT_CARD,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=0,
            border_width=0,
        )
        self._text_display.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configure text tags
        self._text_display.tag_config("interim", foreground=Colors.TEXT_MUTED)
        self._text_display.tag_config("final", foreground=Colors.TEXT_PRIMARY)
        self._text_display.tag_config("timestamp", foreground=Colors.ACCENT)
        self._text_display.tag_config("system", foreground=Colors.WARNING)
        
        # Control buttons
        control_frame = ctk.CTkFrame(page, fg_color="transparent", height=70)
        control_frame.pack(fill="x", padx=30, pady=(0, 30))
        control_frame.pack_propagate(False)
        
        # Center the buttons
        btn_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_container.pack(expand=True)
        
        # Pause button
        self._pause_btn = ctk.CTkButton(
            btn_container,
            text="⏸️ 暂停",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            width=100,
            height=45,
            corner_radius=22,
            fg_color=Colors.CONTENT_CARD,
            hover_color=Colors.CONTENT_BORDER,
            text_color=Colors.TEXT_PRIMARY,
            border_width=1,
            border_color=Colors.CONTENT_BORDER,
            state="disabled",
            command=self._toggle_pause,
        )
        self._pause_btn.pack(side="left", padx=10)
        
        # Main record button
        self._record_btn = ctk.CTkButton(
            btn_container,
            text="🎙️ 开始录音",
            font=ctk.CTkFont(family="Microsoft YaHei", size=16, weight="bold"),
            width=160,
            height=50,
            corner_radius=25,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            text_color="#FFFFFF",
            command=self._toggle_recording,
        )
        self._record_btn.pack(side="left", padx=10)
        
        # Stop button (only visible when recording)
        self._stop_btn = ctk.CTkButton(
            btn_container,
            text="⏹️ 停止",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            width=100,
            height=45,
            corner_radius=22,
            fg_color=Colors.RECORDING,
            hover_color=Colors.RECORDING_HOVER,
            text_color="#FFFFFF",
            state="disabled",
            command=self._stop_recording,
        )
        self._stop_btn.pack(side="left", padx=10)
        
        return page
        
    # ========================================
    # History Page
    # ========================================
        
    def _create_history_page(self) -> ctk.CTkFrame:
        """Create the history page"""
        page = ctk.CTkFrame(self._content_area, fg_color=Colors.CONTENT_BG)
        
        # Title
        title_frame = ctk.CTkFrame(page, fg_color="transparent", height=60)
        title_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="历史记录",
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")
        
        # Button bar
        btn_bar = ctk.CTkFrame(title_frame, fg_color="transparent")
        btn_bar.pack(side="right")
        
        # Import button
        ctk.CTkButton(
            btn_bar,
            text="📂 导入",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=80,
            height=32,
            corner_radius=16,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            text_color="#FFFFFF",
            command=self._import_files,
        ).pack(side="left", padx=5)
        
        # Refresh button
        ctk.CTkButton(
            btn_bar,
            text="🔄 刷新",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=80,
            height=32,
            corner_radius=16,
            fg_color=Colors.CONTENT_CARD,
            hover_color=Colors.CONTENT_BORDER,
            text_color=Colors.TEXT_PRIMARY,
            border_width=1,
            border_color=Colors.CONTENT_BORDER,
            command=self._refresh_history,
        ).pack(side="left", padx=5)
        
        # Info card
        info_card = ctk.CTkFrame(page, fg_color=Colors.CONTENT_CARD, corner_radius=12, height=80)
        info_card.pack(fill="x", padx=30, pady=(0, 20))
        info_card.pack_propagate(False)
        
        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            info_inner,
            text="🔒 您的数据保持私密",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_inner,
            text="所有听写记录仅保存在本地，不会上传到云端。音频不会被保存，只保留文字记录。",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(5, 0))
        
        # Scrollable history list
        self._history_scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            corner_radius=0,
        )
        self._history_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        return page
        
    def _refresh_history(self):
        """Refresh the history list"""
        # Clear existing items
        for widget in self._history_scroll.winfo_children():
            widget.destroy()
            
        # Get all output files
        output_dir = OutputConfig.OUTPUT_DIR
        if not output_dir.exists():
            ctk.CTkLabel(
                self._history_scroll,
                text="暂无历史记录",
                font=ctk.CTkFont(family="Microsoft YaHei", size=14),
                text_color=Colors.TEXT_MUTED,
            ).pack(pady=50)
            return
            
        files_md = sorted(output_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        files_txt = sorted(output_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
        files = sorted(files_md + files_txt, key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not files:
            ctk.CTkLabel(
                self._history_scroll,
                text="暂无历史记录",
                font=ctk.CTkFont(family="Microsoft YaHei", size=14),
                text_color=Colors.TEXT_MUTED,
            ).pack(pady=50)
            return
            
        # Group by date
        current_date = None
        for filepath in files:
            mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            date_str = mod_time.strftime("%Y年%m月%d日")
            
            # Check if we need a new date header
            if date_str != current_date:
                current_date = date_str
                
                # Date header
                date_label = ctk.CTkLabel(
                    self._history_scroll,
                    text=date_str,
                    font=ctk.CTkFont(family="Microsoft YaHei", size=13),
                    text_color=Colors.TEXT_SECONDARY,
                    anchor="w",
                )
                date_label.pack(fill="x", pady=(15, 8))
                
            # File item
            item = HistoryItem(
                self._history_scroll,
                filepath,
                on_click=self._open_file,
                on_delete=self._delete_file,
            )
            item.pack(fill="x", pady=3)
            
    def _open_file(self, filepath: Path):
        """Open a file with default application"""
        try:
            os.startfile(str(filepath))
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")
            
    def _delete_file(self, filepath: Path):
        """Delete a file with confirmation"""
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除这个文件吗？\n\n{filepath.name}\n\n此操作不可撤销。"
        )
        if result:
            try:
                filepath.unlink()
                self._refresh_history()
                messagebox.showinfo("成功", "文件已删除")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
                
    def _import_files(self):
        """Import external MD/TXT files"""
        filepaths = filedialog.askopenfilenames(
            title="选择要导入的文件",
            initialdir=str(Path.home() / "Documents"),
            filetypes=[
                ("Markdown 文件", "*.md"),
                ("文本文件", "*.txt"),
                ("所有支持的文件", "*.md;*.txt"),
            ]
        )
        
        if not filepaths:
            return
            
        imported_count = 0
        for src_path in filepaths:
            src_path = Path(src_path)
            # Copy to output directory
            dest_path = OutputConfig.OUTPUT_DIR / src_path.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = src_path.stem
                suffix = src_path.suffix
                dest_path = OutputConfig.OUTPUT_DIR / f"{stem}_{counter}{suffix}"
                counter += 1
                
            try:
                import shutil
                shutil.copy2(src_path, dest_path)
                imported_count += 1
            except Exception as e:
                messagebox.showerror("导入失败", f"无法导入 {src_path.name}: {e}")
                
        if imported_count > 0:
            self._refresh_history()
            messagebox.showinfo("导入成功", f"成功导入 {imported_count} 个文件")
            
    # ========================================
    # Settings Page
    # ========================================
        
    def _create_settings_page(self) -> ctk.CTkFrame:
        """Create the settings page"""
        page = ctk.CTkFrame(self._content_area, fg_color=Colors.CONTENT_BG)
        
        # Title
        title_frame = ctk.CTkFrame(page, fg_color="transparent", height=60)
        title_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="设置",
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")
        
        # Settings cards
        settings_scroll = ctk.CTkScrollableFrame(page, fg_color="transparent")
        settings_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Storage path setting
        path_card = ctk.CTkFrame(settings_scroll, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        path_card.pack(fill="x", pady=5)
        
        path_inner = ctk.CTkFrame(path_card, fg_color="transparent")
        path_inner.pack(fill="x", padx=20, pady=15)
        
        path_left = ctk.CTkFrame(path_inner, fg_color="transparent")
        path_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            path_left,
            text="📁 存储路径",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        self._path_display = ctk.CTkLabel(
            path_left,
            text=str(OutputConfig.OUTPUT_DIR),
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
        )
        self._path_display.pack(anchor="w", pady=(3, 0))
        
        ctk.CTkButton(
            path_inner,
            text="更改",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=70,
            height=32,
            corner_radius=16,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            command=self._change_output_path,
        ).pack(side="right")
        
        # Model selection
        model_card = ctk.CTkFrame(settings_scroll, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        model_card.pack(fill="x", pady=5)
        
        model_inner = ctk.CTkFrame(model_card, fg_color="transparent")
        model_inner.pack(fill="x", padx=20, pady=15)
        
        model_left = ctk.CTkFrame(model_inner, fg_color="transparent")
        model_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            model_left,
            text="🤖 识别模型",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            model_left,
            text="选择 Deepgram 语音识别模型",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(3, 0))
        
        # Model dropdown
        model_options = ["nova-2", "nova", "enhanced", "base"]
        self._model_var = ctk.StringVar(value=DeepgramConfig.MODEL)
        self._model_dropdown = ctk.CTkOptionMenu(
            model_inner,
            values=model_options,
            variable=self._model_var,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=120,
            height=32,
            corner_radius=8,
            fg_color=Colors.ACCENT,
            button_color=Colors.ACCENT_HOVER,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CONTENT_CARD,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            dropdown_hover_color=Colors.ACCENT_LIGHT,
            command=self._on_model_change,
        )
        self._model_dropdown.pack(side="right", padx=(10, 0))
        
        # Language selection
        lang_card = ctk.CTkFrame(settings_scroll, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        lang_card.pack(fill="x", pady=5)
        
        lang_inner = ctk.CTkFrame(lang_card, fg_color="transparent")
        lang_inner.pack(fill="x", padx=20, pady=15)
        
        lang_left = ctk.CTkFrame(lang_inner, fg_color="transparent")
        lang_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            lang_left,
            text="🌐 识别语言",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            lang_left,
            text="选择语音识别的目标语言",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(3, 0))
        
        # Language dropdown
        lang_options = ["zh (中文)", "en (英文)", "ja (日语)", "ko (韩语)", "multi (多语言)"]
        current_lang = f"{DeepgramConfig.LANGUAGE} ({self._get_lang_name(DeepgramConfig.LANGUAGE)})"
        self._lang_var = ctk.StringVar(value=current_lang)
        self._lang_dropdown = ctk.CTkOptionMenu(
            lang_inner,
            values=lang_options,
            variable=self._lang_var,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=120,
            height=32,
            corner_radius=8,
            fg_color=Colors.ACCENT,
            button_color=Colors.ACCENT_HOVER,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CONTENT_CARD,
            dropdown_text_color=Colors.TEXT_PRIMARY,
            dropdown_hover_color=Colors.ACCENT_LIGHT,
            command=self._on_language_change,
        )
        self._lang_dropdown.pack(side="right", padx=(10, 0))
        
        # Timestamp setting
        timestamp_card = ctk.CTkFrame(settings_scroll, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        timestamp_card.pack(fill="x", pady=5)
        
        timestamp_inner = ctk.CTkFrame(timestamp_card, fg_color="transparent")
        timestamp_inner.pack(fill="x", padx=20, pady=15)
        
        timestamp_left = ctk.CTkFrame(timestamp_inner, fg_color="transparent")
        timestamp_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            timestamp_left,
            text="⏱️ 显示时间戳",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            timestamp_left,
            text="在每条记录前显示时间",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(3, 0))
        
        self._timestamp_switch = ctk.CTkSwitch(
            timestamp_inner,
            text="",
            width=50,
            progress_color=Colors.ACCENT,
            command=self._toggle_timestamp,
        )
        self._timestamp_switch.pack(side="right")
        if OutputConfig.INCLUDE_TIMESTAMPS:
            self._timestamp_switch.select()
            
        # About section
        about_card = ctk.CTkFrame(settings_scroll, fg_color=Colors.CONTENT_CARD, corner_radius=12)
        about_card.pack(fill="x", pady=(20, 5))
        
        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            about_inner,
            text="关于 EchoLog",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            about_inner,
            text="版本 1.0.0 | 桌面智能听写助手\n利用 Deepgram API 实现高精度实时语音转文字",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color=Colors.TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))
        
        return page
        
    def _change_output_path(self):
        """Change the output directory"""
        new_path = filedialog.askdirectory(
            title="选择存储路径",
            initialdir=str(OutputConfig.OUTPUT_DIR),
        )
        
        if new_path:
            OutputConfig.OUTPUT_DIR = Path(new_path)
            self._path_display.configure(text=new_path)
            self._path_label.configure(text=f"📁 {self._get_short_path()}")
            messagebox.showinfo("成功", f"存储路径已更改为:\n{new_path}")
            
    def _toggle_timestamp(self):
        """Toggle timestamp display"""
        OutputConfig.INCLUDE_TIMESTAMPS = self._timestamp_switch.get() == 1
        
    def _get_lang_name(self, lang_code: str) -> str:
        """Get language name from code"""
        lang_map = {
            "zh": "中文",
            "en": "英文",
            "ja": "日语",
            "ko": "韩语",
            "multi": "多语言",
        }
        return lang_map.get(lang_code, lang_code)
        
    def _on_model_change(self, choice: str):
        """Handle model selection change"""
        DeepgramConfig.MODEL = choice
        messagebox.showinfo("设置已更改", f"识别模型已切换为: {choice}\n\n下次开始录音时生效。")
        
    def _on_language_change(self, choice: str):
        """Handle language selection change"""
        # Extract language code from choice like "zh (中文)"
        lang_code = choice.split(" ")[0]
        DeepgramConfig.LANGUAGE = lang_code
        messagebox.showinfo("设置已更改", f"识别语言已切换为: {choice}\n\n下次开始录音时生效。")

    # ========================================
    # Page Navigation
    # ========================================
        
    def _show_page(self, page_name: str):
        """Show a specific page"""
        # Hide all pages
        for page in self._pages.values():
            page.pack_forget()
            
        # Update nav items
        for name, item in self._nav_items.items():
            item.set_active(name == page_name)
            
        # Show selected page
        if page_name in self._pages:
            self._pages[page_name].pack(fill="both", expand=True)
            self._current_page = page_name
            
            # Refresh history when showing
            if page_name == "history":
                self._refresh_history()
                
    # ========================================
    # Recording Control
    # ========================================
    
    def _toggle_recording(self):
        """Toggle recording on/off"""
        if self._is_recording:
            # If already recording, this button acts as resume if paused
            if self._is_paused:
                self._resume_recording()
        else:
            self._start_recording()
            
    def _toggle_pause(self):
        """Toggle pause/resume"""
        if self._is_paused:
            self._resume_recording()
        else:
            self._pause_recording()
            
    def _start_recording(self):
        """Start a new recording session"""
        if self._is_recording:
            return
            
        # Update UI
        self._record_btn.configure(
            text="🎙️ 录音中...",
            fg_color=Colors.RECORDING,
            hover_color=Colors.RECORDING_HOVER,
            state="disabled",
        )
        self._pause_btn.configure(state="normal")
        self._stop_btn.configure(state="normal")
        
        self._is_recording = True
        self._is_paused = False
        
        # Initialize output file
        self._init_output_file()
        
        # Clear interim text
        self._current_interim_text = ""
        
        # Add start message
        self._text_display.configure(state="normal")
        self._text_display.delete("1.0", "end")
        self._text_display.configure(state="disabled")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_text(f"🔴 开始录音 [{timestamp}]\n\n", "system")
        
        # Start async engine
        self._async_loop = asyncio.new_event_loop()
        self._async_thread = threading.Thread(target=self._run_async_engine, daemon=True)
        self._async_thread.start()
        
    def _pause_recording(self):
        """Pause the current recording"""
        if not self._is_recording or self._is_paused:
            return
            
        self._is_paused = True
        
        # Update UI
        self._pause_btn.configure(text="▶️ 继续")
        self._record_btn.configure(
            text="⏸️ 已暂停",
            fg_color=Colors.PAUSED,
            hover_color=Colors.WARNING,
        )
        
        self._update_status("paused")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_text(f"\n⏸️ 已暂停 [{timestamp}]\n", "system")
        
    def _resume_recording(self):
        """Resume a paused recording"""
        if not self._is_recording or not self._is_paused:
            return
            
        self._is_paused = False
        
        # Update UI
        self._pause_btn.configure(text="⏸️ 暂停")
        self._record_btn.configure(
            text="🎙️ 录音中...",
            fg_color=Colors.RECORDING,
            hover_color=Colors.RECORDING_HOVER,
        )
        
        self._update_status("recording")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_text(f"▶️ 继续录音 [{timestamp}]\n\n", "system")
        
    def _stop_recording(self):
        """Stop the recording session"""
        if not self._is_recording:
            return
            
        self._is_recording = False
        self._is_paused = False
        
        # Stop engine
        if self._async_loop and self._engine:
            asyncio.run_coroutine_threadsafe(
                self._engine.stop(),
                self._async_loop
            )
            
        # Wait for thread
        if self._async_thread and self._async_thread.is_alive():
            self._async_thread.join(timeout=5)
            
        # Update UI
        self._record_btn.configure(
            text="🎙️ 开始录音",
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            state="normal",
        )
        self._pause_btn.configure(text="⏸️ 暂停", state="disabled")
        self._stop_btn.configure(state="disabled")
        
        # Clear interim and add end message
        self._clear_interim_text()
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_text(f"\n⏹️ 录音结束 [{timestamp}]\n", "system")
        
        self._update_status("idle")
        
    def _run_async_engine(self):
        """Run the transcription engine in background thread"""
        asyncio.set_event_loop(self._async_loop)
        
        self._engine = TranscriptionEngine(
            on_interim=self._handle_interim,
            on_final=self._handle_final,
            on_error=self._handle_error,
            on_status_change=self._update_status,
        )
        
        self._engine._output_file = self._output_file
        
        try:
            self._async_loop.run_until_complete(self._run_engine())
        except Exception as e:
            self._handle_error(e)
        finally:
            self._async_loop.close()
            self._async_loop = None
            self._engine = None
            
    async def _run_engine(self):
        """Start and run the engine"""
        if not self._engine:
            return
            
        self._engine._on_status_change("connecting")
        
        if not await self._engine._connect_websocket():
            self._engine._on_status_change("error")
            return
            
        self._engine._is_running = True
        self._engine._on_status_change("recording")
        
        while not self._engine._audio_queue.empty():
            try:
                self._engine._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
                
        self._engine._tasks = [
            asyncio.create_task(self._engine._capture_audio()),
            asyncio.create_task(self._send_audio_with_pause()),
            asyncio.create_task(self._engine._receive_transcription()),
        ]
        
        while self._engine._is_running and self._is_recording:
            await asyncio.sleep(0.1)
            
        await self._engine.stop()
        
    async def _send_audio_with_pause(self):
        """Send audio with pause support"""
        while self._engine and self._engine._is_running:
            try:
                # Skip sending when paused
                if self._is_paused:
                    await asyncio.sleep(0.1)
                    continue
                    
                audio_data = await asyncio.wait_for(
                    self._engine._audio_queue.get(),
                    timeout=0.5
                )
                
                if self._engine._websocket and not self._is_paused:
                    try:
                        await self._engine._websocket.send(audio_data)
                    except:
                        break
                        
            except asyncio.TimeoutError:
                continue
            except Exception:
                break
                
    # ========================================
    # Callbacks
    # ========================================
    
    def _handle_interim(self, text: str):
        """Handle interim result"""
        if self._is_paused:
            return
        self.after(0, lambda: self._update_interim_text(f"💭 {text}"))
        
    def _handle_final(self, text: str):
        """Handle final result"""
        if self._is_paused:
            return
            
        self.after(0, self._clear_interim_text)
        
        timestamp = datetime.now().strftime(OutputConfig.CONTENT_TIME_FORMAT)
        
        if OutputConfig.INCLUDE_TIMESTAMPS:
            self.after(0, lambda: self._append_text(f"{timestamp} ", "timestamp"))
            self.after(0, lambda: self._append_text(f"{text}\n\n", "final"))
        else:
            self.after(0, lambda: self._append_text(f"{text}\n\n", "final"))
            
        self._write_to_file(text, timestamp)
        
    def _handle_error(self, error: Exception):
        """Handle error"""
        self.after(0, lambda: self._append_text(f"\n⚠️ 错误: {error}\n", "system"))
        
    def _update_status(self, status: str):
        """Update status indicator"""
        status_map = {
            "idle": ("就绪", Colors.SUCCESS),
            "connecting": ("连接中...", Colors.WARNING),
            "recording": ("录音中", Colors.RECORDING),
            "paused": ("已暂停", Colors.PAUSED),
            "stopping": ("停止中...", Colors.WARNING),
            "error": ("错误", Colors.ERROR),
        }
        
        text, color = status_map.get(status, ("未知", Colors.TEXT_MUTED))
        
        self.after(0, lambda: self._status_dot.configure(text_color=color))
        self.after(0, lambda: self._status_label.configure(text=text))
        
    # ========================================
    # Text Display
    # ========================================
    
    def _append_text(self, text: str, tag: str = "final"):
        """Append text with tag"""
        self._text_display.configure(state="normal")
        self._text_display.insert("end", text, tag)
        self._text_display.configure(state="disabled")
        self._text_display.see("end")
        
    def _update_interim_text(self, text: str):
        """Update interim text"""
        self._text_display.configure(state="normal")
        
        if self._current_interim_text:
            try:
                start_idx = self._text_display.search(
                    self._current_interim_text,
                    "end-2c",
                    backwards=True,
                    exact=True
                )
                if start_idx:
                    end_idx = f"{start_idx}+{len(self._current_interim_text)}c"
                    self._text_display.delete(start_idx, end_idx)
            except:
                pass
                
        self._current_interim_text = text
        self._text_display.insert("end", text, "interim")
        self._text_display.configure(state="disabled")
        self._text_display.see("end")
        
    def _clear_interim_text(self):
        """Clear interim text"""
        if self._current_interim_text:
            self._text_display.configure(state="normal")
            try:
                start_idx = self._text_display.search(
                    self._current_interim_text,
                    "end-2c",
                    backwards=True,
                    exact=True
                )
                if start_idx:
                    end_idx = f"{start_idx}+{len(self._current_interim_text)}c"
                    self._text_display.delete(start_idx, end_idx)
            except:
                pass
            self._text_display.configure(state="disabled")
        self._current_interim_text = ""
        
    # ========================================
    # File Operations
    # ========================================
    
    def _init_output_file(self):
        """Initialize output file"""
        OutputConfig.ensure_output_dir()
        
        timestamp = datetime.now().strftime(OutputConfig.FILENAME_TIME_FORMAT)
        filename = f"{OutputConfig.FILE_PREFIX}_{timestamp}{OutputConfig.FILE_EXTENSION}"
        filepath = OutputConfig.OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# EchoLog 听写记录\n")
            f.write(f"> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
        self._output_file = str(filepath)
        self._file_indicator.configure(text=f"📄 {filename}")
        
    def _write_to_file(self, text: str, timestamp: str):
        """Write to output file"""
        if not self._output_file:
            return
            
        try:
            with open(self._output_file, "a", encoding="utf-8") as f:
                if OutputConfig.INCLUDE_TIMESTAMPS:
                    f.write(f"{timestamp} {text}\n\n")
                else:
                    f.write(f"{text}\n\n")
        except Exception as e:
            self.after(0, lambda: self._handle_error(e))
            
    def _open_output_folder(self):
        """Open the output folder in explorer"""
        folder = str(OutputConfig.OUTPUT_DIR)
        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
            
    def _show_help(self):
        """Show help dialog"""
        webbrowser.open("https://github.com/your-repo/echolog")
        
    # ========================================
    # Window Events
    # ========================================
        
    def _on_closing(self):
        """Handle window close"""
        if self._is_recording:
            self._stop_recording()
        self.destroy()
        sys.exit(0)


# ========================================
# Main Entry
# ========================================
def main():
    """Main entry point"""
    
    if not DeepgramConfig.API_KEY or DeepgramConfig.API_KEY == "your_deepgram_api_key_here":
        print("⚠️ 错误: 请先在 .env 文件中设置 DEEPGRAM_API_KEY")
        
        root = ctk.CTk()
        root.withdraw()
        messagebox.showerror(
            "配置错误",
            "DEEPGRAM_API_KEY 未配置\n\n请在 .env 文件中设置 API Key\n获取地址: https://console.deepgram.com/"
        )
        root.destroy()
        sys.exit(1)
        return
        
    app = EchoLogApp()
    app.mainloop()


if __name__ == "__main__":
    main()
