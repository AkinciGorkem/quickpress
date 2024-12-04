import os
from typing import List, Tuple

class FileHandler:
    VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        return (
            os.path.isfile(file_path) and 
            file_path.lower().endswith(FileHandler.VALID_EXTENSIONS)
        )
    
    @staticmethod
    def get_files_from_folder(folder_path: str) -> List[str]:
        valid_files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.lower().endswith(FileHandler.VALID_EXTENSIONS):
                    full_path = os.path.join(root, filename)
                    valid_files.append(full_path)
        return valid_files
    
    @staticmethod
    def parse_dropped_files(data: str) -> Tuple[List[str], List[str]]:
        valid_files = []
        invalid_files = []
        
        for file_path in data.split('{') if isinstance(data, str) else data:
            file_path = file_path.strip('{}')
            if os.path.isfile(file_path):
                if FileHandler.validate_file(file_path):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)
            elif os.path.isdir(file_path):
                folder_files = FileHandler.get_files_from_folder(file_path)
                valid_files.extend(folder_files)
                
        return valid_files, invalid_files