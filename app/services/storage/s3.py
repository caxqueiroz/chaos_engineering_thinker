import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional, Dict, Any
from .base import BaseStorage
import io

class S3Storage(BaseStorage):
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: Optional[str] = None
    ):
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            region_name=region_name
        )
        
        # Ensure bucket exists
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                raise
    
    def save_file(self, file_data: BinaryIO, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a file to S3"""
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = {
                k: str(v) for k, v in metadata.items()
            }
        
        self.s3.upload_fileobj(
            file_data,
            self.bucket_name,
            file_path,
            ExtraArgs=extra_args
        )
        
        return file_path
    
    def get_file(self, file_path: str) -> BinaryIO:
        """Get a file from S3"""
        file_obj = io.BytesIO()
        self.s3.download_fileobj(
            self.bucket_name,
            file_path,
            file_obj
        )
        file_obj.seek(0)
        return file_obj
    
    def delete_file(self, file_path: str) -> None:
        """Delete a file from S3"""
        self.s3.delete_object(
            Bucket=self.bucket_name,
            Key=file_path
        )
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a presigned URL for the file"""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError:
            return ""
