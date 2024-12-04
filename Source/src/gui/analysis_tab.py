import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.utils.stats import StatsManager

class AnalysisTab(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setup_export_frame()
        self.setup_stats_frame()
        
    def setup_export_frame(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        export_frame = ttk.LabelFrame(control_frame, text="Export Options")
        export_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            export_frame,
            text="Export to CSV",
            command=self.export_to_csv
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            export_frame,
            text="Export to PDF",
            command=self.export_to_pdf
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
    def setup_stats_frame(self):
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.canvas_container = ttk.Frame(self.stats_frame)
        self.canvas_container.pack(fill='both', expand=True)
        
    def update_statistics(self):
        for widget in self.canvas_container.winfo_children():
            widget.destroy()
            
        if self.shared_data['compression_stats']:
            try:
                stats_widget = StatsManager.create_statistics_plots(
                    self.shared_data['compression_stats'],
                    self.canvas_container
                )
                stats_widget.pack(fill='both', expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error updating statistics: {str(e)}")
        
    def export_to_csv(self):
        if not self.shared_data['compression_stats']:
            messagebox.showinfo("Info", "No compression data to export.")
            return
            
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if filepath:
                StatsManager.export_to_csv(self.shared_data['compression_stats'], filepath)
                messagebox.showinfo("Success", f"Data exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to CSV: {str(e)}")
            
    def export_to_pdf(self):
        if not self.shared_data['compression_stats']:
            messagebox.showinfo("Info", "No compression data to export.")
            return
            
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if filepath:
                StatsManager.export_to_pdf(self.shared_data['compression_stats'], filepath)
                messagebox.showinfo("Success", f"Data exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to PDF: {str(e)}")