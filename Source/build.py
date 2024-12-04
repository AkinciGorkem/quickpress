import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    PyInstaller.__main__.run([
        'src/main.py',
        '--name=QuickPress',
        '--windowed',
        '--onefile',
        '--icon=icon.ico',
        '--add-data=src;src',
        '--additional-hooks-dir=.',
        '--hidden-import=tkinter',
        '--hidden-import=tkinterdnd2',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=reportlab'
    ])

if __name__ == "__main__":
    build_executable()