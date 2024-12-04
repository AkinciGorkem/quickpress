from PIL import Image
import io
import os
from typing import Dict, List, Optional

class ImageCompressor:
    @staticmethod
    def compress_image(
        file_path: str,
        output_folder: str,
        quality: int,
        output_format: str,
        target_size: Optional[float] = None
    ) -> Dict:
        try:
            with Image.open(file_path) as img:
                original_size = os.path.getsize(file_path)
                
                if output_format == "same":
                    output_format = img.format or "JPEG"
                    
                extension = ".jpg" if output_format == "JPEG" else ".png"
                output_path = os.path.join(
                    output_folder or os.path.dirname(file_path),
                    f"{os.path.splitext(os.path.basename(file_path))[0]}_compressed{extension}"
                )
                
                if output_format == "JPEG" and img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                if target_size:
                    quality = ImageCompressor.find_optimal_quality(img, target_size)
                    
                if output_format == "PNG":
                    img.save(output_path, format=output_format, optimize=True)
                else:
                    img.save(output_path, format=output_format, quality=quality, optimize=True)
                    
                new_size = os.path.getsize(output_path)
                
                return {
                    'file': file_path,
                    'original_size': original_size,
                    'compressed_size': new_size,
                    'format': output_format,
                    'output_path': output_path
                }
        except Exception as e:
            raise Exception(f"Error compressing image {file_path}: {str(e)}")
    
    @staticmethod
    def find_optimal_quality(img: Image.Image, target_size_bytes: float) -> int:
        min_quality = 1
        max_quality = 95
        best_quality = max_quality
        best_size = float('inf')
        
        while min_quality <= max_quality:
            current_quality = (min_quality + max_quality) // 2
            
            temp_output = io.BytesIO()
            img.save(temp_output, format=img.format or 'JPEG', 
                    quality=current_quality, optimize=True)
            current_size = temp_output.tell()
            
            if abs(current_size - target_size_bytes) < abs(best_size - target_size_bytes):
                best_quality = current_quality
                best_size = current_size
            
            if current_size > target_size_bytes:
                max_quality = current_quality - 1
            else:
                min_quality = current_quality + 1
        
        return best_quality