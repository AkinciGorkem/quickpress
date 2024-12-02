import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import threading

class ImageCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickPress")
        self.root.geometry("500x600")
        self.selected_files = []
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg="#f0f0f0")
        
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.create_labels()
        self.create_buttons()
        self.create_progressbar()
        self.setup_drag_drop()
        
    def create_labels(self):
        label_styles = {'bg': "#f0f0f0", 'wraplength': 400}
        
        tk.Label(
            self.main_frame, 
            text="QuickPress",
            font=("Helvetica", 24, "bold"),
            fg="#333333",
            **label_styles
        ).pack(pady=(0, 20))
        
        tk.Label(
            self.main_frame,
            text="Compress your images without quality loss",
            font=("Helvetica", 12),
            fg="#666666",
            **label_styles
        ).pack(pady=(0, 30))
        
        self.status_label = tk.Label(
            self.main_frame,
            text="No file selected",
            font=("Helvetica", 10),
            fg="#666666",
            **label_styles
        )
        self.status_label.pack(pady=(0, 20))
        
        self.files_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.files_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.files_listbox = tk.Listbox(
            self.files_frame,
            width=50,
            height=8,
            selectmode=tk.MULTIPLE,
            font=("Helvetica", 10),
            bg="white"
        )
        self.files_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(self.files_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)

    def create_buttons(self):
        button_styles = {
            'fg': "white",
            'relief': tk.FLAT,
            'cursor': "hand2"
        }
        
        self.button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.button_frame.pack(pady=(0, 10))
        
        self.select_btn = tk.Button(
            self.button_frame,
            text="Select Images",
            command=self.select_files,
            bg="#4CAF50",
            padx=20,
            pady=10,
            font=("Helvetica", 12),
            **button_styles
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_folder_btn = tk.Button(
            self.button_frame,
            text="Select Folder",
            command=self.select_folder,
            bg="#FF9800",
            padx=20,
            pady=10,
            font=("Helvetica", 12),
            **button_styles
        )
        self.select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.list_actions_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.list_actions_frame.pack(pady=(0, 10))
        
        self.remove_btn = tk.Button(
            self.list_actions_frame,
            text="Remove Selected",
            command=self.remove_selected,
            bg="#FF5722",
            padx=10,
            pady=5,
            font=("Helvetica", 10),
            **button_styles
        )
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            self.list_actions_frame,
            text="Clear All",
            command=self.clear_list,
            bg="#9E9E9E",
            padx=10,
            pady=5,
            font=("Helvetica", 10),
            **button_styles
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.compress_btn = tk.Button(
            self.main_frame,
            text="Compress Image",
            command=self.start_compression,
            bg="#2196F3",
            padx=30,
            pady=15,
            font=("Helvetica", 12, "bold"),
            **button_styles
        )
        self.compress_btn.pack(pady=10)
        
        for button in [self.select_btn, self.compress_btn, self.remove_btn, self.clear_btn]:
            button.bind("<Enter>", self.on_enter)
            button.bind("<Leave>", self.on_leave)

    def create_progressbar(self):
        self.progress = ttk.Progressbar(self.main_frame, orient='horizontal', mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 20))
        self.progress.pack_forget()

    def on_enter(self, event):
        button_colors = {
            self.select_btn: "#45a049",
            self.compress_btn: "#1976D2",
            self.remove_btn: "#D84315",
            self.clear_btn: "#757575"
        }
        event.widget.configure(bg=button_colors[event.widget])
    
    def on_leave(self, event):
        button_colors = {
            self.select_btn: "#4CAF50",
            self.compress_btn: "#2196F3",
            self.remove_btn: "#FF5722",
            self.clear_btn: "#9E9E9E"
        }
        event.widget.configure(bg=button_colors[event.widget])
    
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
            total_original_size = 0
            total_new_size = 0
            
            for index, file_path in enumerate(self.selected_files):
                with Image.open(file_path) as img:
                    original_size = os.path.getsize(file_path)
                    total_original_size += original_size
                    
                    output_path = f"{os.path.splitext(file_path)[0]}_compressed{os.path.splitext(file_path)[1]}"
                    img.save(output_path, optimize=True, quality=100)
                    
                    new_size = os.path.getsize(output_path)
                    total_new_size += new_size
                    
                    self.root.after(0, self.update_progress, index + 1)
            
            compression_percent = ((total_original_size - total_new_size) / total_original_size) * 100
            self.root.after(0, self.compression_complete, total_original_size, total_new_size, compression_percent)
                
        except Exception as e:
            self.root.after(0, self.compression_error, str(e))

    def update_progress(self, value):
        self.progress['value'] = value
        self.status_label.config(text=f"Compressing... ({value}/{len(self.selected_files)})")

    def compression_complete(self, total_original_size, total_new_size, compression_percent):
        self.progress.pack_forget()
        messagebox.showinfo("Success", "All images compressed successfully!")
        self.status_label.config(
            text=f"Compression completed!\nTotal Original: {total_original_size/1024/1024:.2f} MB\n"
                 f"Total New: {total_new_size/1024/1024:.2f} MB\n"
                 f"Total Reduced by: {compression_percent:.2f}%",
            fg="#4CAF50"
        )
        self.enable_buttons()

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
        self.main_frame.drop_target_register(DND_FILES)
        self.main_frame.dnd_bind('<<Drop>>', self.handle_drop)
        self.main_frame.dnd_bind('<<DragEnter>>', self.drag_enter)
        self.main_frame.dnd_bind('<<DragLeave>>', self.drag_leave)
        
        self.files_listbox.drop_target_register(DND_FILES)
        self.files_listbox.dnd_bind('<<Drop>>', self.handle_drop)
        self.files_listbox.dnd_bind('<<DragEnter>>', self.drag_enter)
        self.files_listbox.dnd_bind('<<DragLeave>>', self.drag_leave)

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
        self.drag_leave(event)

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

def main():
    try:
        root = TkinterDnD.Tk()
        app = ImageCompressor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()