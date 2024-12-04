import tkinter as tk
from tkinter import ttk
from src.gui.main_tab import MainTab
from src.gui.settings_tab import SettingsTab
from src.gui.analysis_tab import AnalysisTab

class ImageCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickPress")
        self.root.geometry("600x700")
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg="#f0f0f0")
        self.setup_header()
        self.setup_notebook()
        self.setup_style()
        
    def setup_style(self):
        self.style = ttk.Style()
        self.style.configure("TNotebook", background='#f0f0f0')
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=('Helvetica', 9))
        
    def setup_header(self):
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill='x', padx=20, pady=(20,10))
        
        tk.Label(
            header_frame,
            text="QuickPress",
            font=("Helvetica", 24, "bold"),
            fg="#333333",
            bg="#f0f0f0"
        ).pack()
        
        tk.Label(
            header_frame,
            text="Compress your images without quality loss",
            font=("Helvetica", 10),
            fg="#666666",
            bg="#f0f0f0"
        ).pack()
        
    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        self.shared_data = {
            'selected_files': [],
            'compression_stats': [],
            'output_folder': "",
            'compression_quality': tk.StringVar(value="medium"),
            'target_size': tk.StringVar(value=""),
            'use_target_size': tk.BooleanVar(value=False),
            'output_format': tk.StringVar(value="same")
        }
        
        self.main_tab = MainTab(self.notebook, self.shared_data)
        self.settings_tab = SettingsTab(self.notebook, self.shared_data)
        self.analysis_tab = AnalysisTab(self.notebook, self.shared_data)
        
        self.notebook.add(self.main_tab, text='Main')
        self.notebook.add(self.settings_tab, text='Settings')
        self.notebook.add(self.analysis_tab, text='Analysis')