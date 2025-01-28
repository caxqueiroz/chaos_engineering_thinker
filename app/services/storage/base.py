from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any
from enum import Enum
import os

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"

class BaseStorage(ABC):
    """Base class for storage implementations"""
    
    @abstractmethod
    def save_file(self, file_data: BinaryIO, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a file to storage and return its path/url"""
        pass
    
    @abstractmethod
    def get_file(self, file_path: str) -> BinaryIO:
        """Get a file from storage"""
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """Delete a file from storage"""
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a URL for the file (may be temporary for cloud storage)"""
        pass
