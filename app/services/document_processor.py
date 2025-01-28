import os
from datetime import datetime
from typing import BinaryIO, Dict, Any, Optional, Tuple
from fastapi import UploadFile
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract
import pydot
from .storage.base import BaseStorage, StorageType
from .storage.local import LocalStorage
from .storage.s3 import S3Storage

class DocumentProcessor:
    def __init__(
        self,
        storage_type: StorageType = StorageType.LOCAL,
        storage_config: Optional[Dict[str, Any]] = None
    ):
        self.storage_config = storage_config or {}
        
        # Initialize storage backend
        if storage_type == StorageType.LOCAL:
            base_path = storage_config.get('base_path', './data/uploads')
            self.storage = LocalStorage(base_path)
        else:  # S3
            self.storage = S3Storage(
                bucket_name=storage_config['bucket_name'],
                aws_access_key_id=storage_config.get('aws_access_key_id'),
                aws_secret_access_key=storage_config.get('aws_secret_access_key'),
                endpoint_url=storage_config.get('endpoint_url'),
                region_name=storage_config.get('region_name')
            )
    
    def _generate_file_path(self, original_filename: str, session_id: str, doc_type: str) -> str:
        """Generate a unique file path for storage"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"
        return os.path.join(session_id, doc_type, filename)
    
    async def save_document(
        self,
        file: UploadFile,
        session_id: str,
        doc_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Save a document and return its path and metadata"""
        file_path = self._generate_file_path(file.filename, session_id, doc_type)
        
        # Read file content
        content = await file.read()
        file_obj = BinaryIO(content)
        
        # Add basic metadata
        metadata = metadata or {}
        metadata.update({
            'original_filename': file.filename,
            'session_id': session_id,
            'doc_type': doc_type,
            'upload_time': datetime.now().isoformat()
        })
        
        # Process specific document types
        if doc_type == "network_topology":
            graph_data = self._process_network_topology(file_obj)
            metadata['graph_data'] = graph_data
        
        # Save file
        stored_path = self.storage.save_file(file_obj, file_path, metadata)
        
        return stored_path, metadata
    
    def _process_network_topology(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Process network topology image and extract graph data"""
        # Create a temporary file for image processing
        img = Image.open(file_obj)
        
        # Extract text from image using OCR
        text = pytesseract.image_to_string(img)
        
        # Create graph from image
        graph = nx.Graph()
        
        # Parse the text to identify nodes and edges
        # This is a simple example - you might need more sophisticated parsing
        lines = text.split('\n')
        for line in lines:
            if '->' in line:
                source, target = line.split('->')
                graph.add_edge(source.strip(), target.strip())
            elif node := line.strip():
                graph.add_node(node)
        
        # Convert graph to dot format
        dot_data = nx.drawing.nx_pydot.to_pydot(graph)
        
        return {
            'nodes': list(graph.nodes()),
            'edges': list(graph.edges()),
            'dot_data': dot_data.to_string()
        }
    
    def get_document_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get URL for accessing the document"""
        return self.storage.get_file_url(file_path, expires_in)
    
    def get_document(self, file_path: str) -> BinaryIO:
        """Get document content"""
        return self.storage.get_file(file_path)
    
    def delete_document(self, file_path: str) -> None:
        """Delete a document"""
        self.storage.delete_file(file_path)
