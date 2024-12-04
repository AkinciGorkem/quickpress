import tkinter as tk
from tkinter import ttk, filedialog

class SettingsTab(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setup_quality_frame()
        self.setup_format_frame()
        self.setup_target_size_frame()
        self.setup_output_frame()
        
    def setup_quality_frame(self):
        quality_frame = ttk.LabelFrame(self, text="Compression Quality")
        quality_frame.pack(fill='x', padx=10, pady=5)
        
        qualities = [
            ("High Quality", "high"),
            ("Medium Quality", "medium"),
            ("Low Quality", "low")
        ]
        
        for text, value in qualities:
            ttk.Radiobutton(
                quality_frame,
                text=text,
                variable=self.shared_data['compression_quality'],
                value=value
            ).pack(anchor='w', padx=10, pady=2)
            
    def setup_format_frame(self):
        format_frame = ttk.LabelFrame(self, text="Output Format")
        format_frame.pack(fill='x', padx=10, pady=5)
        
        formats = [
            ("Keep Original", "same"),
            ("Convert to JPEG", "JPEG"),
            ("Convert to PNG", "PNG")
        ]
        
        for text, value in formats:
            ttk.Radiobutton(
                format_frame,
                text=text,
                variable=self.shared_data['output_format'],
                value=value
            ).pack(anchor='w', padx=10, pady=2)
            
    def setup_target_size_frame(self):
        target_frame = ttk.LabelFrame(self, text="Target Size")
        target_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(
            target_frame,
            text="Use Target Size",
            variable=self.shared_data['use_target_size'],
            command=self.toggle_target_size
        ).pack(anchor='w', padx=10, pady=2)
        
        size_frame = ttk.Frame(target_frame)
        size_frame.pack(fill='x', padx=10, pady=2)
        
        ttk.Label(size_frame, text="Target Size (MB):").pack(side=tk.LEFT)
        self.target_size_entry = ttk.Entry(
            size_frame,
            textvariable=self.shared_data['target_size'],
            width=10,
            state=tk.DISABLED
        )
        self.target_size_entry.pack(side=tk.LEFT, padx=5)
        
    def setup_output_frame(self):
        output_frame = ttk.LabelFrame(self, text="Output Directory")
        output_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            output_frame,
            text="Select Output Folder",
            command=self.select_output_folder
        ).pack(padx=10, pady=5)
        
        self.output_label = ttk.Label(
            output_frame,
            text="Default: Same as input file"
        )
        self.output_label.pack(padx=10, pady=5)
        
    def toggle_target_size(self):
        if self.shared_data['use_target_size'].get():
            self.target_size_entry.config(state=tk.NORMAL)
        else:
            self.target_size_entry.config(state=tk.DISABLED)
            
    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.shared_data['output_folder'] = folder_path
            self.output_label.config(
                text=f"Selected: {folder_path}"
            )