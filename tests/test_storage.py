import pytest
import io
import json
from app.services.storage.base import StorageType

def test_local_storage_save_file(local_storage):
    """Test saving a file to local storage"""
    # Create test data
    test_data = b"Hello, World!"
    file_obj = io.BytesIO(test_data)
    file_path = "test/hello.txt"
    metadata = {"test_key": "test_value"}
    
    # Save file
    saved_path = local_storage.save_file(file_obj, file_path, metadata)
    assert saved_path == file_path
    
    # Verify file exists and content matches
    with local_storage.get_file(file_path) as f:
        assert f.read() == test_data
    
    # Verify metadata was saved
    with open(f"{local_storage._get_full_path(file_path)}.metadata", 'r') as f:
        saved_metadata = json.load(f)
        assert saved_metadata == metadata

def test_local_storage_delete_file(local_storage):
    """Test deleting a file from local storage"""
    # Save a file first
    test_data = b"Test data"
    file_obj = io.BytesIO(test_data)
    file_path = "test/delete_me.txt"
    
    local_storage.save_file(file_obj, file_path)
    
    # Verify file exists
    assert local_storage.get_file(file_path) is not None
    
    # Delete file
    local_storage.delete_file(file_path)
    
    # Verify file no longer exists
    with pytest.raises(FileNotFoundError):
        local_storage.get_file(file_path)

def test_s3_storage_save_file(s3_storage):
    """Test saving a file to S3 storage"""
    # Create test data
    test_data = b"Hello, S3!"
    file_obj = io.BytesIO(test_data)
    file_path = "test/hello_s3.txt"
    metadata = {"test_key": "test_value"}
    
    # Save file
    saved_path = s3_storage.save_file(file_obj, file_path, metadata)
    assert saved_path == file_path
    
    # Verify file exists and content matches
    result = s3_storage.get_file(file_path)
    assert result.read() == test_data
    
    # Verify metadata was saved
    s3_object = s3_storage.s3.get_object(
        Bucket=s3_storage.bucket_name,
        Key=file_path
    )
    assert s3_object['Metadata']['test_key'] == 'test_value'

def test_s3_storage_delete_file(s3_storage):
    """Test deleting a file from S3 storage"""
    # Save a file first
    test_data = b"Test S3 data"
    file_obj = io.BytesIO(test_data)
    file_path = "test/delete_me_s3.txt"
    
    s3_storage.save_file(file_obj, file_path)
    
    # Verify file exists
    assert s3_storage.get_file(file_path) is not None
    
    # Delete file
    s3_storage.delete_file(file_path)
    
    # Verify file no longer exists
    with pytest.raises(Exception):
        s3_storage.get_file(file_path)

def test_s3_storage_get_file_url(s3_storage):
    """Test generating presigned URLs for S3 files"""
    # Save a file first
    test_data = b"URL test data"
    file_obj = io.BytesIO(test_data)
    file_path = "test/url_test.txt"
    
    s3_storage.save_file(file_obj, file_path)
    
    # Get URL
    url = s3_storage.get_file_url(file_path, expires_in=3600)
    
    # Verify URL contains expected components
    assert 'test-bucket' in url
    assert file_path in url
    assert 'Expires=' in url
    assert 'Signature=' in url
