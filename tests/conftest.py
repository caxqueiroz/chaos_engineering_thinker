import os
import pytest
import tempfile
import shutil
from moto import mock_aws
import boto3
from app.services.storage.local import LocalStorage
from app.services.storage.s3 import S3Storage
from app.services.document_processor import DocumentProcessor
from app.services.storage.base import StorageType

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def local_storage(temp_dir):
    """Create a LocalStorage instance for testing"""
    return LocalStorage(temp_dir)

@pytest.fixture
def mock_s3_client():
    """Create a mocked S3 client"""
    with mock_aws():
        s3 = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        # Create test bucket
        s3.create_bucket(
            Bucket='test-bucket'
        )
        yield s3

@pytest.fixture
def s3_storage(mock_s3_client):
    """Create an S3Storage instance with mocked S3"""
    storage = S3Storage(
        bucket_name='test-bucket',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    return storage

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    from PIL import Image, ImageDraw
    import io
    
    # Create a test image with some network-like content
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some nodes and connections
    draw.text((50, 50), "Server A", fill='black')
    draw.text((150, 150), "Server B", fill='black')
    draw.line([(60, 60), (160, 160)], fill='black', width=2)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

@pytest.fixture
def document_processor_local(temp_dir):
    """Create a DocumentProcessor instance with local storage"""
    return DocumentProcessor(
        storage_type=StorageType.LOCAL,
        storage_config={'base_path': temp_dir}
    )

@pytest.fixture
def document_processor_s3(mock_s3_client):
    """Create a DocumentProcessor instance with S3 storage"""
    return DocumentProcessor(
        storage_type=StorageType.S3,
        storage_config={
            'bucket_name': 'test-bucket',
            'aws_access_key_id': 'test',
            'aws_secret_access_key': 'test',
            'region_name': 'us-east-1'
        }
    )
