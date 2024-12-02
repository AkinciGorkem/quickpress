import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import threading

class ImageCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickPress")
        self.root.geometry("500x400")
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg="#f0f0f0")
        
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.create_labels()
        self.create_buttons()
        self.create_progressbar()
        
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

    def create_buttons(self):
        button_styles = {
            'fg': "white",
            'relief': tk.FLAT,
            'cursor': "hand2"
        }
        
        self.select_btn = tk.Button(
            self.main_frame,
            text="Select Image",
            command=self.select_file,
            bg="#4CAF50",
            padx=20,
            pady=10,
            font=("Helvetica", 12),
            **button_styles
        )
        self.select_btn.pack(pady=(0, 10))
        
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
        
        for button in [self.select_btn, self.compress_btn]:
            button.bind("<Enter>", self.on_enter)
            button.bind("<Leave>", self.on_leave)

    def create_progressbar(self):
        self.progress = ttk.Progressbar(self.main_frame, orient='horizontal', mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 20))
        self.progress.pack_forget()

    def on_enter(self, event):
        button_colors = {
            self.select_btn: "#45a049",
            self.compress_btn: "#1976D2"
        }
        event.widget.configure(bg=button_colors[event.widget])
    
    def on_leave(self, event):
        button_colors = {
            self.select_btn: "#4CAF50",
            self.compress_btn: "#2196F3"
        }
        event.widget.configure(bg=button_colors[event.widget])
    
    def select_file(self):
        try:
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
            self.selected_file = filedialog.askopenfilename(filetypes=filetypes)
            if self.selected_file:
                self.status_label.config(
                    text=f"Selected: {os.path.basename(self.selected_file)}",
                    fg="#333333"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting file: {str(e)}")
    
    def start_compression(self):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            messagebox.showwarning("Warning", "Please select an image first!")
            return
        
        self.select_btn.config(state=tk.DISABLED)
        self.compress_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Compressing...", fg="#666666")
        
        self.progress.pack()
        self.progress.start()
        
        threading.Thread(target=self.compress_image, daemon=True).start()

    def compress_image(self):
        try:
            with Image.open(self.selected_file) as img:
                original_size = os.path.getsize(self.selected_file)
                original_size = os.path.getsize(self.selected_file)
                
                file_path, file_extension = os.path.splitext(self.selected_file)
                output_path = f"{file_path}_compressed{file_extension}"
                
                img.save(output_path, optimize=True, quality=100)
                
                new_size = os.path.getsize(output_path)
                
                compression_percent = ((original_size - new_size) / original_size) * 100
                
                self.root.after(0, self.compression_complete, output_path, original_size, new_size, compression_percent)
                
        except Exception as e:
            self.root.after(0, self.compression_error, str(e))

    def compression_complete(self, output_path, original_size, new_size, compression_percent):
        self.progress.stop()
        self.progress.pack_forget()
        messagebox.showinfo("Success", f"Image compressed and saved to:\n{output_path}")
        self.status_label.config(
            text=f"Compression completed!\nOriginal: {original_size/1024:.2f} KB\nNew: {new_size/1024:.2f} KB\nReduced by: {compression_percent:.2f}%",
            fg="#4CAF50"
        )
        self.enable_buttons()

    def compression_error(self, error_message):
        self.progress.stop()
        self.progress.pack_forget()
        messagebox.showerror("Error", f"Error compressing image: {error_message}")
        self.enable_buttons()

    def enable_buttons(self):
        self.select_btn.config(state=tk.NORMAL)
        self.compress_btn.config(state=tk.NORMAL)

def main():
    try:
        root = tk.Tk()
        app = ImageCompressor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()