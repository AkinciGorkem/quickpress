import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import threading
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

class ImageCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickPress")
        self.root.geometry("600x700")
        self.selected_files = []
        self.output_folder = ""
        self.compression_quality = tk.StringVar(value="medium")
        self.target_size = tk.StringVar(value="")
        self.use_target_size = tk.BooleanVar(value=False)
        self.output_format = tk.StringVar(value="same")
        self.compression_stats = []
        
        self.style = ttk.Style()
        self.style.configure("TNotebook", background='#f0f0f0')
        self.style.configure("TNotebook.Tab", padding=[12, 4], font=('Helvetica', 9))
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg="#f0f0f0")
        
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
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        self.main_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text='Main')
        self.notebook.add(self.settings_tab, text='Settings')
        self.notebook.add(self.analysis_tab, text='Analysis')
        
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_analysis_tab()
        
        self.setup_drag_drop()
        
    def setup_main_tab(self):
        self.status_label = tk.Label(
            self.main_tab,
            text="No file selected",
            font=("Helvetica", 10),
            fg="#666666",
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=(10,5))
        
        list_frame = tk.Frame(self.main_tab, bg="#f0f0f0")
        list_frame.pack(fill='both', expand=True, pady=5)
        
        self.files_listbox = tk.Listbox(
            list_frame,
            width=50,
            height=8,
            selectmode=tk.MULTIPLE,
            font=("Helvetica", 10),
            bg="white"
        )
        self.files_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)
        
        button_frame = tk.Frame(self.main_tab, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        self.select_btn = tk.Button(
            button_frame,
            text="Select Images",
            command=self.select_files,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.folder_btn = tk.Button(
            button_frame,
            text="Select Folder",
            command=self.select_folder,
            bg="#FF9800",
            fg="white",
            font=("Helvetica", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.folder_btn.pack(side=tk.LEFT, padx=5)

        self.compress_btn = tk.Button(
            button_frame,
            text="Compress",
            command=self.start_compression,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.compress_btn.pack(side=tk.LEFT, padx=5)
        
        remove_button_frame = tk.Frame(self.main_tab, bg="#f0f0f0")
        remove_button_frame.pack(pady=5)
        
        remove_buttons = [
            ("Remove Selected", self.remove_selected, "#FF5252"),
            ("Clear All", self.clear_list, "#757575")
        ]
        
        for text, command, color in remove_buttons:
            tk.Button(
                remove_button_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Helvetica", 10),
                relief=tk.FLAT,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
        
        self.files_listbox.bind('<Delete>', lambda e: self.remove_selected())
        
        self.progress = ttk.Progressbar(self.main_tab, orient='horizontal', mode='determinate', length=300)
        self.progress.pack(pady=10)
        self.progress.pack_forget()
        
    def setup_settings_tab(self):
        quality_frame = ttk.LabelFrame(self.settings_tab, text="Compression Settings")
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
                variable=self.compression_quality,
                value=value
            ).pack(anchor='w', padx=10, pady=2)
        
        format_frame = ttk.LabelFrame(self.settings_tab, text="Output Format")
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
                variable=self.output_format,
                value=value
            ).pack(anchor='w', padx=10, pady=2)
        
        target_frame = ttk.LabelFrame(self.settings_tab, text="Target Size")
        target_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(
            target_frame,
            text="Use Target Size",
            variable=self.use_target_size,
            command=self.toggle_target_size
        ).pack(anchor='w', padx=10, pady=2)
        
        size_frame = ttk.Frame(target_frame)
        size_frame.pack(fill='x', padx=10, pady=2)
        
        ttk.Label(size_frame, text="Target Size (MB):").pack(side=tk.LEFT)
        self.target_size_entry = ttk.Entry(
            size_frame,
            textvariable=self.target_size,
            width=10,
            state=tk.DISABLED
        )
        self.target_size_entry.pack(side=tk.LEFT, padx=5)
        
    def setup_analysis_tab(self):
        control_frame = ttk.Frame(self.analysis_tab)
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
        
        self.stats_canvas = tk.Canvas(self.analysis_tab, bg='white')
        self.stats_canvas.pack(fill='both', expand=True, padx=10, pady=5)
        
    def select_files(self):
        try:
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
            files = filedialog.askopenfilenames(filetypes=filetypes)
            if files:
                self.selected_files.extend(list(files))
                self.update_file_list()
                total_files = len(self.selected_files)
                self.status_label.config(
                    text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}",
                    fg="#333333"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting files: {str(e)}")
    
    def select_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                valid_extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
                for root, _, filenames in os.walk(folder_path):
                    for filename in filenames:
                        if filename.lower().endswith(valid_extensions):
                            full_path = os.path.join(root, filename)
                            if full_path not in self.selected_files:
                                self.selected_files.append(full_path)
                self.update_file_list()
                total_files = len(self.selected_files)
                self.status_label.config(
                    text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}",
                    fg="#333333"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting folder: {str(e)}")
    
    def update_file_list(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, os.path.basename(file))
    
    def start_compression(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one image!")
            return
        
        self.select_btn.config(state=tk.DISABLED)
        self.compress_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Compressing...", fg="#666666")
        
        self.progress.pack()
        self.progress['mode'] = 'determinate'
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.selected_files)
        
        threading.Thread(target=self.compress_images, daemon=True).start()

    def compress_images(self):
        try:
            self.compression_stats = []
            total_original_size = 0
            total_new_size = 0
            
            if self.use_target_size.get():
                try:
                    target_mb = float(self.target_size.get())
                    target_bytes = target_mb * 1024 * 1024
                except ValueError:
                    raise ValueError("Please enter a valid target size in MB")
            
            for index, file_path in enumerate(self.selected_files):
                with Image.open(file_path) as img:
                    original_size = os.path.getsize(file_path)
                    total_original_size += original_size
                    
                    output_format = self.output_format.get()
                    if output_format == "same":
                        output_format = img.format or "JPEG"
                    
                    extension = ".jpg" if output_format == "JPEG" else ".png"
                    
                    output_path = os.path.join(
                        self.output_folder or os.path.dirname(file_path),
                        f"{os.path.splitext(os.path.basename(file_path))[0]}_compressed{extension}"
                    )
                    
                    if output_format == "JPEG" and img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    if self.use_target_size.get():
                        file_target_bytes = (original_size / total_original_size) * target_bytes
                        quality = self.find_optimal_quality(img, file_target_bytes)
                    else:
                        quality_levels = {"high": 90, "medium": 60, "low": 30}
                        quality = quality_levels[self.compression_quality.get()]
                    
                    if output_format == "PNG":
                        img.save(output_path, format=output_format, optimize=True)
                    else:
                        img.save(output_path, format=output_format, quality=quality, optimize=True)
                    
                    new_size = os.path.getsize(output_path)
                    total_new_size += new_size
                    
                    self.compression_stats.append({
                        'file': file_path,
                        'original_size': original_size,
                        'compressed_size': new_size,
                        'format': output_format
                    })
                    
                    self.root.after(0, self.update_progress, index + 1)
            
            compression_percent = ((total_original_size - total_new_size) / total_original_size) * 100
            self.root.after(0, self.compression_complete, total_original_size, total_new_size, compression_percent)
                
            self.root.after(0, self.show_compression_graph, self.compression_stats)
                
        except Exception as e:
            self.root.after(0, self.compression_error, str(e))

    def update_progress(self, value):
        self.progress['value'] = value
        self.status_label.config(text=f"Compressing... ({value}/{len(self.selected_files)})")

    def compression_complete(self, total_original_size, total_new_size, compression_percent):
        self.progress.pack_forget()
        
        format_text = ""
        if self.output_format.get() != "same":
            format_text = f" (Converted to {self.output_format.get()})"
        
        if self.use_target_size.get():
            quality_text = f"Target Size: {self.target_size.get()}MB"
        else:
            quality_text = f"Quality: {self.compression_quality.get().capitalize()}"
            
        messagebox.showinfo(
            "Success",
            f"All images compressed successfully!\n{quality_text}{format_text}"
        )
        self.status_label.config(
            text=f"Compression completed! ({quality_text}{format_text})\n"
                 f"Total Original: {total_original_size/1024/1024:.2f} MB\n"
                 f"Total New: {total_new_size/1024/1024:.2f} MB\n"
                 f"Total Reduced by: {compression_percent:.2f}%",
            fg="#4CAF50"
        )
        self.enable_buttons()
        self.save_compression_stats()

    def compression_error(self, error_message):
        self.progress.pack_forget()
        messagebox.showerror("Error", f"Error compressing images: {error_message}")
        self.enable_buttons()

    def enable_buttons(self):
        self.select_btn.config(state=tk.NORMAL)
        self.compress_btn.config(state=tk.NORMAL)

    def remove_selected(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Please select files to remove")
            return
        
        for index in sorted(selected_indices, reverse=True):
            self.selected_files.pop(index)
        
        self.update_file_list()
        total_files = len(self.selected_files)
        self.status_label.config(
            text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}"
            if total_files > 0 else "No file selected",
            fg="#333333"
        )

    def clear_list(self):
        if not self.selected_files:
            messagebox.showinfo("Info", "List is already empty")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all files?"):
            self.selected_files.clear()
            self.files_listbox.delete(0, tk.END)
            self.status_label.config(text="No file selected", fg="#333333")

    def setup_drag_drop(self):
        self.main_tab.drop_target_register(DND_FILES)
        self.main_tab.dnd_bind('<<Drop>>', self.handle_drop)
        
        self.files_listbox.drop_target_register(DND_FILES)
        self.files_listbox.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        files = self.parse_drop_data(event.data)
        if files:
            self.selected_files.extend(files)
            self.update_file_list()
            total_files = len(self.selected_files)
            self.status_label.config(
                text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}",
                fg="#333333"
            )

    def parse_drop_data(self, data):
        valid_files = []
        files = self.root.tk.splitlist(data)
        valid_extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
        
        for file in files:
            if os.path.isfile(file) and file.lower().endswith(valid_extensions):
                if file not in self.selected_files:
                    valid_files.append(file)
            elif os.path.isdir(file):
                for root, _, filenames in os.walk(file):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        if filename.lower().endswith(valid_extensions):
                            if full_path not in self.selected_files:
                                valid_files.append(full_path)
        
        if not valid_files:
            messagebox.showwarning("Warning", "No valid image files found!")
        return valid_files

    def drag_enter(self, event):
        self.files_listbox.configure(bg="#e0e0e0")
        self.status_label.config(text="Drop files here!", fg="#2196F3")

    def drag_leave(self, event):
        self.files_listbox.configure(bg="white")
        total_files = len(self.selected_files)
        self.status_label.config(
            text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}"
            if total_files > 0 else "No file selected",
            fg="#333333"
        )

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder = folder_path
            self.status_label.config(
                text=f"Output Folder: {os.path.basename(folder_path)}",
                fg="#333333"
            )

    def toggle_target_size(self):
        if self.use_target_size.get():
            self.target_size_entry.config(state=tk.NORMAL)
            self.quality_frame.pack_forget()
        else:
            self.target_size_entry.config(state=tk.DISABLED)
            self.quality_frame.pack(before=self.target_size_frame, pady=(0, 10), padx=20, fill='x')

    def find_optimal_quality(self, img, target_size_bytes):
        min_quality = 1
        max_quality = 95
        best_quality = max_quality
        best_size = float('inf')
        
        while min_quality <= max_quality:
            current_quality = (min_quality + max_quality) // 2
            
            temp_output = io.BytesIO()
            img.save(temp_output, format=img.format or 'JPEG', quality=current_quality, optimize=True)
            current_size = temp_output.tell()
            
            if abs(current_size - target_size_bytes) < abs(best_size - target_size_bytes):
                best_quality = current_quality
                best_size = current_size
            
            if current_size > target_size_bytes:
                max_quality = current_quality - 1
            else:
                min_quality = current_quality + 1
        
        return best_quality

    def show_compression_graph(self, stats):
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Compression Statistics")
        graph_window.geometry("1200x800")
        
        main_container = tk.Frame(graph_window, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        graph_frame = tk.Frame(main_container, bg='#f0f0f0')
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        fig.set_facecolor('#f0f0f0')
        
        file_names = [os.path.basename(stat['file']) for stat in stats]
        original_sizes = [stat['original_size'] / (1024 * 1024) for stat in stats]
        compressed_sizes = [stat['compressed_size'] / (1024 * 1024) for stat in stats]
        
        x = np.arange(len(file_names))
        width = 0.35
        
        ax1.bar(x - width/2, original_sizes, width, label='Original Size', color='#2196F3')
        ax1.bar(x + width/2, compressed_sizes, width, label='Compressed Size', color='#4CAF50')
        
        ax1.set_ylabel('Size (MB)')
        ax1.set_title('File Sizes Before and After Compression')
        ax1.set_xticks(x)
        ax1.set_xticklabels(file_names, rotation=45, ha='right')
        ax1.legend()
        
        compression_ratios = [(stat['original_size'] - stat['compressed_size']) / stat['original_size'] * 100 
                            for stat in stats]
        
        ax2.bar(x, compression_ratios, color='#FF9800')
        ax2.set_ylabel('Compression Ratio (%)')
        ax2.set_title('Compression Ratio by File')
        ax2.set_xticks(x)
        ax2.set_xticklabels(file_names, rotation=45, ha='right')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        details_frame = tk.Frame(main_container, bg='#f0f0f0', width=300)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        summary_frame = tk.LabelFrame(details_frame, text="General Summary", bg='#f0f0f0', font=("Helvetica", 10, "bold"))
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_original = sum(stat['original_size'] for stat in stats) / (1024 * 1024)
        total_compressed = sum(stat['compressed_size'] for stat in stats) / (1024 * 1024)
        total_saved = total_original - total_compressed
        avg_ratio = sum([(stat['original_size'] - stat['compressed_size']) / stat['original_size'] * 100 for stat in stats]) / len(stats)
        
        summary_text = (
            f"Total Original Size: {total_original:.2f} MB\n"
            f"Total Compressed Size: {total_compressed:.2f} MB\n"
            f"Total Space Saved: {total_saved:.2f} MB\n"
            f"Average Compression Ratio: {avg_ratio:.1f}%"
        )
        
        tk.Label(summary_frame, text=summary_text, bg='#f0f0f0', justify=tk.LEFT, padx=10, pady=5).pack()
        
        details_label = tk.Label(details_frame, text="File Details", bg='#f0f0f0', font=("Helvetica", 10, "bold"))
        details_label.pack(anchor='w', pady=(10, 5))
        
        canvas = tk.Canvas(details_frame, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for stat in stats:
            file_frame = tk.LabelFrame(scrollable_frame, text=os.path.basename(stat['file']), 
                                     bg='#f0f0f0', font=("Helvetica", 9))
            file_frame.pack(fill=tk.X, pady=5, padx=5)
            
            original_mb = stat['original_size'] / (1024 * 1024)
            compressed_mb = stat['compressed_size'] / (1024 * 1024)
            saved_mb = original_mb - compressed_mb
            ratio = (stat['original_size'] - stat['compressed_size']) / stat['original_size'] * 100
            
            details = (
                f"Original: {original_mb:.2f} MB\n"
                f"Compressed: {compressed_mb:.2f} MB\n"
                f"Saved: {saved_mb:.2f} MB\n"
                f"Ratio: {ratio:.1f}%\n"
                f"Format: {stat['format']}"
            )
            
            tk.Label(file_frame, text=details, bg='#f0f0f0', justify=tk.LEFT, padx=10, pady=5).pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def export_to_csv(self):
        if not self.compression_stats:
            messagebox.showinfo("Info", "No compression data to export.")
            return
        
        df = pd.DataFrame(self.compression_stats)
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if csv_path:
            df.to_csv(csv_path, index=False)
            messagebox.showinfo("Success", f"Data exported to {csv_path}")

    def export_to_pdf(self):
        if not self.compression_stats:
            messagebox.showinfo("Info", "No compression data to export.")
            return
        
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            c.drawString(30, height - 30, "Compression Statistics")
            
            y = height - 50
            for stat in self.compression_stats:
                text = (
                    f"File: {os.path.basename(stat['file'])}\n"
                    f"Original Size: {stat['original_size'] / (1024 * 1024):.2f} MB\n"
                    f"Compressed Size: {stat['compressed_size'] / (1024 * 1024):.2f} MB\n"
                    f"Format: {stat['format']}\n"
                )
                for line in text.split('\n'):
                    c.drawString(30, y, line)
                    y -= 15
                y -= 10
            
            c.save()
            messagebox.showinfo("Success", f"Data exported to {pdf_path}")

    def save_compression_stats(self):
        try:
            with open("compression_history.json", "a") as f:
                json.dump(self.compression_stats, f)
                f.write("\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving compression history: {str(e)}")

def main():
    try:
        root = TkinterDnD.Tk()
        app = ImageCompressor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()