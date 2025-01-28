import pytest
from fastapi import UploadFile
import io
import os
from PIL import Image
import networkx as nx
from app.services.document_processor import DocumentProcessor
from app.services.storage.base import StorageType

class MockUploadFile:
    """Mock UploadFile for testing"""
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self._content = content
        
    async def read(self):
        return self._content

@pytest.mark.asyncio
async def test_document_processor_save_regular_document(document_processor_local):
    """Test saving a regular document"""
    # Create test document
    content = b"Test document content"
    file = MockUploadFile("test.txt", content)
    
    # Save document
    file_path, metadata = await document_processor_local.save_document(
        file=file,
        session_id="test_session",
        doc_type="text"
    )
    
    # Verify file path and metadata
    assert "test_session" in file_path
    assert "text" in file_path
    assert metadata["original_filename"] == "test.txt"
    assert metadata["session_id"] == "test_session"
    assert metadata["doc_type"] == "text"
    
    # Verify content
    saved_content = document_processor_local.get_document(file_path).read()
    assert saved_content == content

@pytest.mark.asyncio
async def test_document_processor_save_network_topology(document_processor_local, sample_image):
    """Test saving and processing a network topology image"""
    # Create test image with network topology
    file = MockUploadFile("network.png", sample_image.getvalue())
    
    # Save document
    file_path, metadata = await document_processor_local.save_document(
        file=file,
        session_id="test_session",
        doc_type="network_topology"
    )
    
    # Verify file path and metadata
    assert "test_session" in file_path
    assert "network_topology" in file_path
    assert metadata["original_filename"] == "network.png"
    assert "graph_data" in metadata
    
    # Verify graph data structure
    graph_data = metadata["graph_data"]
    assert isinstance(graph_data["nodes"], list)
    assert isinstance(graph_data["edges"], list)
    assert isinstance(graph_data["dot_data"], str)
    
    # Verify some expected content from our test image
    nodes = graph_data["nodes"]
    assert any("Server" in str(node) for node in nodes), "Expected to find 'Server' in node labels"

@pytest.mark.asyncio
async def test_document_processor_with_s3(document_processor_s3):
    """Test document processor with S3 storage"""
    # Create test document
    content = b"Test S3 document"
    file = MockUploadFile("test_s3.txt", content)
    
    # Save document
    file_path, metadata = await document_processor_s3.save_document(
        file=file,
        session_id="test_session",
        doc_type="text"
    )
    
    # Verify file path and metadata
    assert "test_session" in file_path
    assert metadata["original_filename"] == "test_s3.txt"
    
    # Get document URL
    url = document_processor_s3.get_document_url(file_path)
    assert url is not None
    assert "test-bucket" in url
    
    # Verify content
    saved_content = document_processor_s3.get_document(file_path).read()
    assert saved_content == content

@pytest.mark.asyncio
async def test_document_processor_metadata(document_processor_local):
    """Test document processor metadata handling"""
    content = b"Test metadata"
    file = MockUploadFile("metadata_test.txt", content)
    custom_metadata = {
        "owner": "test_user",
        "priority": "high",
        "tags": ["test", "metadata"]
    }
    
    # Save document with custom metadata
    file_path, metadata = await document_processor_local.save_document(
        file=file,
        session_id="test_session",
        doc_type="text",
        metadata=custom_metadata
    )
    
    # Verify custom metadata was preserved
    assert metadata["owner"] == "test_user"
    assert metadata["priority"] == "high"
    assert metadata["tags"] == ["test", "metadata"]

def test_document_processor_delete(document_processor_local):
    """Test deleting a document"""
    # Create and save a test document
    content = b"Delete me"
    file_obj = io.BytesIO(content)
    file_path = "test_session/text/delete_me.txt"
    
    document_processor_local.storage.save_file(file_obj, file_path)
    
    # Verify file exists
    assert document_processor_local.get_document(file_path) is not None
    
    # Delete document
    document_processor_local.delete_document(file_path)
    
    # Verify file no longer exists
    with pytest.raises(FileNotFoundError):
        document_processor_local.get_document(file_path)
