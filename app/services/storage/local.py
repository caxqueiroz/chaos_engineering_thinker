import os
import shutil
from typing import BinaryIO, Optional, Dict, Any
from .base import BaseStorage
import magic

class LocalStorage(BaseStorage):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> str:
        """Get the full path for a file"""
        full_path = os.path.join(self.base_path, file_path)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path
    
    def save_file(self, file_data: BinaryIO, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a file to local storage"""
        full_path = self._get_full_path(file_path)
        
        # Save the file
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)
        
        # Save metadata if provided
        if metadata:
            metadata_path = f"{full_path}.metadata"
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f)
        
        return file_path
    
    def get_file(self, file_path: str) -> BinaryIO:
        """Get a file from local storage"""
        full_path = self._get_full_path(file_path)
        return open(full_path, 'rb')
    
    def delete_file(self, file_path: str) -> None:
        """Delete a file from local storage"""
        full_path = self._get_full_path(file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            # Remove metadata file if it exists
            metadata_path = f"{full_path}.metadata"
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a local file path (note: not a proper URL)"""
        return self._get_full_path(file_path)
