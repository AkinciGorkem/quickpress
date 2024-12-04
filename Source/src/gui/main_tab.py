import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES
import threading
import os
from src.core.compressor import ImageCompressor
from src.core.file_handler import FileHandler
from src.utils.stats import StatsManager
from PIL import Image, ImageTk, ImageGrab

class MainTab(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        self.setup_drag_drop()
        self.setup_clipboard()
        self.preview_window = None
        
    def setup_ui(self):
        self.status_label = tk.Label(
            self,
            text="Drag & drop images or press Ctrl+V to paste",
            font=("Helvetica", 10),
            fg="#666666",
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=(10,5))
        self.setup_file_list()
        self.setup_buttons()
        self.progress = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=300)
        
    def setup_file_list(self):
        list_frame = tk.Frame(self, bg="#f0f0f0")
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
        
        self.files_listbox.bind('<Motion>', self.create_preview)
        self.files_listbox.bind('<Leave>', self.hide_preview)
        
    def setup_buttons(self):
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        buttons = [
            ("Select Images", self.select_files, "#4CAF50"),
            ("Select Folder", self.select_folder, "#FF9800"),
            ("Compress", self.start_compression, "#2196F3")
        ]
        
        for text, command, color in buttons:
            tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Helvetica", 10),
                relief=tk.FLAT,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
        remove_frame = tk.Frame(self, bg="#f0f0f0")
        remove_frame.pack(pady=5)
        
        remove_buttons = [
            ("Remove Selected", self.remove_selected, "#FF5252"),
            ("Clear All", self.clear_list, "#757575")
        ]
        
        for text, command, color in remove_buttons:
            tk.Button(
                remove_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Helvetica", 10),
                relief=tk.FLAT,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
    
    def setup_drag_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        self.files_listbox.drop_target_register(DND_FILES)
        self.files_listbox.dnd_bind('<<Drop>>', self.handle_drop)
        
    def setup_clipboard(self):
        self.bind_all('<Control-v>', self.handle_paste)
        
    def handle_paste(self, event=None):
        try:
            from PIL import ImageGrab
            clipboard_content = ImageGrab.grabclipboard()
            
            if isinstance(clipboard_content, Image.Image):
                temp_path = os.path.join(os.path.expanduser('~'), '.quickpress_temp.png')
                clipboard_content.save(temp_path)
                self.shared_data['selected_files'].append(temp_path)
                self.update_file_list()
                return
            
            if isinstance(clipboard_content, list):
                valid_files = []
                for item in clipboard_content:
                    if isinstance(item, str) and FileHandler.validate_file(item):
                        valid_files.append(item)
                
                if valid_files:
                    self.shared_data['selected_files'].extend(valid_files)
                    self.update_file_list()
                    return
                
            try:
                clipboard_text = self.clipboard_get()
                paths = clipboard_text.split('\n')
                valid_files = []
                
                for path in paths:
                    path = path.strip()
                    if path and FileHandler.validate_file(path):
                        valid_files.append(path)
                    
                if valid_files:
                    self.shared_data['selected_files'].extend(valid_files)
                    self.update_file_list()
                    return
                
            except tk.TclError:
                pass
            
            messagebox.showinfo("Info", "No valid images found in clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error handling clipboard: {str(e)}")
            
    def select_files(self):
        try:
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
            files = filedialog.askopenfilenames(filetypes=filetypes)
            if files:
                self.shared_data['selected_files'].extend(list(files))
                self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting files: {str(e)}")
            
    def select_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                new_files = FileHandler.get_files_from_folder(folder_path)
                self.shared_data['selected_files'].extend(new_files)
                self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting folder: {str(e)}")
            
    def handle_drop(self, event):
        try:
            valid_files, invalid_files = FileHandler.parse_dropped_files(event.data)
            if invalid_files:
                messagebox.showwarning(
                    "Warning",
                    f"Some files were skipped as they are not valid images:\n{', '.join(invalid_files)}"
                )
            if valid_files:
                self.shared_data['selected_files'].extend(valid_files)
                self.update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error handling dropped files: {str(e)}")
            
    def update_file_list(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.shared_data['selected_files']:
            self.files_listbox.insert(tk.END, os.path.basename(file))
        total_files = len(self.shared_data['selected_files'])
        self.status_label.config(
            text=f"Selected: {total_files} {'file' if total_files == 1 else 'files'}",
            fg="#333333"
        )
        
    def remove_selected(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Please select files to remove")
            return
        
        for index in sorted(selected_indices, reverse=True):
            self.shared_data['selected_files'].pop(index)
        
        self.update_file_list()
        
    def clear_list(self):
        if not self.shared_data['selected_files']:
            messagebox.showinfo("Info", "List is already empty")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all files?"):
            self.shared_data['selected_files'].clear()
            self.update_file_list()
            
    def start_compression(self):
        if not self.shared_data['selected_files']:
            messagebox.showwarning("Warning", "Please select at least one image!")
            return
            
        self.progress.pack()
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.shared_data['selected_files'])
        
        compression_thread = threading.Thread(target=self.compress_images, daemon=True)
        compression_thread.start()
        
    def compress_images(self):
        try:
            self.shared_data['compression_stats'] = []
            
            quality_levels = {"high": 90, "medium": 60, "low": 30}
            quality = quality_levels[self.shared_data['compression_quality'].get()]
            
            target_size = None
            if self.shared_data['use_target_size'].get():
                try:
                    target_mb = float(self.shared_data['target_size'].get())
                    target_size = target_mb * 1024 * 1024
                except ValueError:
                    raise ValueError("Please enter a valid target size in MB")
            
            for index, file_path in enumerate(self.shared_data['selected_files']):
                stat = ImageCompressor.compress_image(
                    file_path=file_path,
                    output_folder=self.shared_data['output_folder'] or os.path.dirname(file_path),
                    quality=quality,
                    output_format=self.shared_data['output_format'].get(),
                    target_size=target_size
                )
                self.shared_data['compression_stats'].append(stat)
                self.update_progress(index + 1)
            
            self.compression_complete()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during compression: {str(e)}")
        finally:
            self.progress.pack_forget()
            
    def update_progress(self, value):
        self.progress['value'] = value
        self.status_label.config(text=f"Compressing... ({value}/{len(self.shared_data['selected_files'])})")
        
    def compression_complete(self):
        if not self.shared_data['compression_stats']:
            return
            
        total_original = sum(stat['original_size'] for stat in self.shared_data['compression_stats'])
        total_compressed = sum(stat['compressed_size'] for stat in self.shared_data['compression_stats'])
        compression_percent = ((total_original - total_compressed) / total_original) * 100
        
        messagebox.showinfo(
            "Success",
            f"All images compressed successfully!\n"
            f"Total space saved: {(total_original - total_compressed) / (1024 * 1024):.2f} MB"
        )
        
        try:
            StatsManager.save_compression_stats(self.shared_data['compression_stats'])
        except Exception as e:
            messagebox.showwarning("Warning", f"Error saving compression stats: {str(e)}")
        
    def create_preview(self, event):
        widget = event.widget
        index = widget.nearest(event.y)
    
        bbox = widget.bbox(index)
        if not bbox:
            self.hide_preview()
            return
        
        if not (bbox[1] <= event.y <= bbox[1] + bbox[3]):
            self.hide_preview()
            return
        
        try:
            file_path = self.shared_data['selected_files'][index]
            
            if (self.preview_window is None or 
                getattr(self, '_current_preview_path', None) != file_path):
                
                if self.preview_window:
                    self.preview_window.destroy()
                    
                self.preview_window = tk.Toplevel()
                self.preview_window.overrideredirect(True)
                self.preview_window.withdraw()
                
                image = Image.open(file_path)
                preview_size = (200, 200)
                image.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                
                label = tk.Label(self.preview_window, image=photo, bd=2, relief="solid")
                label.image = photo
                label.pack()
                
                x = self.winfo_rootx() + widget.winfo_width() + 10
                y = self.winfo_rooty() + bbox[1]
                self.preview_window.geometry(f"+{x}+{y}")
                self.preview_window.attributes('-alpha', 0.95)
                self.preview_window.deiconify()
                
                self._current_preview_path = file_path
                
        except Exception as e:
            if self.preview_window:
                self.preview_window.destroy()
                self.preview_window = None
                self._current_preview_path = None
    
    def hide_preview(self, event=None):
        if self.preview_window:
            self.preview_window.destroy()
            self.preview_window = None