import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from src.gui.app import ImageCompressor
from tkinterdnd2 import TkinterDnD
from tkinter import messagebox

def main():
    try:
        root = TkinterDnD.Tk()
        app = ImageCompressor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()