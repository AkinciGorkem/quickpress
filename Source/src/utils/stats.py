import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Frame, Canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatsManager:
    @staticmethod
    def export_to_csv(stats: List[Dict], filepath: str) -> None:
        try:
            df = pd.DataFrame(stats)
            df.to_csv(filepath, index=False)
        except Exception as e:
            raise Exception(f"Error exporting to CSV: {str(e)}")
    
    @staticmethod
    def export_to_pdf(stats: List[Dict], filepath: str) -> None:
        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            c.drawString(30, height - 30, "Compression Statistics")
            
            y = height - 50
            for stat in stats:
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
        except Exception as e:
            raise Exception(f"Error exporting to PDF: {str(e)}")
    
    @staticmethod
    def save_compression_stats(stats: List[Dict]) -> None:
        try:
            with open("compression_history.json", "a") as f:
                json.dump(stats, f)
                f.write("\n")
        except Exception as e:
            raise Exception(f"Error saving compression stats: {str(e)}")
    
    @staticmethod
    def create_statistics_plots(stats: List[Dict], frame: Frame) -> Canvas:
        try:
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
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            
            return canvas.get_tk_widget()
        except Exception as e:
            raise Exception(f"Error creating statistics plots: {str(e)}")