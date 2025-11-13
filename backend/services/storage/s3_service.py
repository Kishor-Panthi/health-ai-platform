"""
AWS S3 Storage Service
HIPAA-compliant file storage for documents, images, and medical records
"""
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional, BinaryIO
import os
import structlog
from datetime import datetime, timedelta
import mimetypes
import uuid

logger = structlog.get_logger()


class S3StorageService:
    """
    S3 storage service with HIPAA compliance features
    """

    def __init__(self):
        # AWS Configuration
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )

        self.bucket_name = os.environ.get('S3_BUCKET_NAME')

        if not self.bucket_name:
            logger.warning("S3_BUCKET_NAME not set - storage will fail")

        # Verify bucket exists and has encryption
        self._verify_bucket_configuration()

    def _verify_bucket_configuration(self):
        """Verify S3 bucket exists and has proper HIPAA compliance settings"""
        if not self.bucket_name:
            return

        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)

            # Verify encryption is enabled
            try:
                encryption = self.s3_client.get_bucket_encryption(Bucket=self.bucket_name)
                logger.info(
                    "s3_bucket_verified",
                    bucket=self.bucket_name,
                    encryption=encryption['ServerSideEncryptionConfiguration']
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    logger.error(
                        "s3_bucket_not_encrypted",
                        bucket=self.bucket_name,
                        message="Bucket does not have encryption enabled - HIPAA violation!"
                    )

        except ClientError as e:
            logger.error("s3_bucket_verification_failed", bucket=self.bucket_name, error=str(e))

    def _generate_key(
        self,
        practice_id: str,
        category: str,
        filename: str
    ) -> str:
        """
        Generate S3 key with proper organization
        Format: practice_id/category/YYYY/MM/DD/uuid_filename
        """
        now = datetime.utcnow()
        unique_id = str(uuid.uuid4())[:8]

        key = f"{practice_id}/{category}/{now.year}/{now.month:02d}/{now.day:02d}/{unique_id}_{filename}"

        return key

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        practice_id: str,
        category: str = 'documents',
        patient_id: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Upload file to S3 with HIPAA-compliant settings

        Args:
            file_content: File content as bytes
            filename: Original filename
            practice_id: Practice ID for organization
            category: File category (documents, images, labs, etc)
            patient_id: Optional patient ID for metadata
            content_type: MIME type (auto-detected if not provided)
            metadata: Additional metadata to store with file

        Returns:
            Dict with success status, key, and URL
        """
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            # Generate S3 key
            key = self._generate_key(practice_id, category, filename)

            # Determine content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Build metadata
            s3_metadata = {
                'practice-id': practice_id,
                'category': category,
                'original-filename': filename,
                'uploaded-at': datetime.utcnow().isoformat()
            }

            if patient_id:
                s3_metadata['patient-id'] = patient_id

            if metadata:
                # Add custom metadata (S3 only allows lowercase keys)
                s3_metadata.update({k.lower(): str(v) for k, v in metadata.items()})

            # Upload to S3 with encryption
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256',  # HIPAA requirement
                Metadata=s3_metadata,
                # Add tags for compliance
                Tagging=f"practice={practice_id}&category={category}&phi=true"
            )

            logger.info(
                "file_uploaded_to_s3",
                bucket=self.bucket_name,
                key=key,
                size=len(file_content),
                practice_id=practice_id
            )

            return {
                'success': True,
                'key': key,
                'bucket': self.bucket_name,
                'size': len(file_content),
                'content_type': content_type,
                'url': f"s3://{self.bucket_name}/{key}"
            }

        except ClientError as e:
            logger.error(
                "s3_upload_failed",
                filename=filename,
                error=str(e),
                exc_info=True
            )
            return {'success': False, 'error': str(e)}

    async def download_file(self, key: str) -> Dict:
        """
        Download file from S3

        Returns:
            Dict with success status, content, and metadata
        """
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )

            content = response['Body'].read()

            logger.info(
                "file_downloaded_from_s3",
                bucket=self.bucket_name,
                key=key,
                size=len(content)
            )

            return {
                'success': True,
                'content': content,
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {}),
                'last_modified': response.get('LastModified'),
                'size': response.get('ContentLength')
            }

        except ClientError as e:
            logger.error("s3_download_failed", key=key, error=str(e))
            return {'success': False, 'error': str(e)}

    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        download_filename: Optional[str] = None
    ) -> Dict:
        """
        Generate temporary download URL (for secure file access)

        Args:
            key: S3 object key
            expiration: URL expiration in seconds (default 1 hour)
            download_filename: Force download with specific filename

        Returns:
            Dict with success status and URL
        """
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }

            # Force download with custom filename
            if download_filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{download_filename}"'

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )

            logger.info(
                "presigned_url_generated",
                key=key,
                expiration=expiration
            )

            return {
                'success': True,
                'url': url,
                'expires_in': expiration,
                'expires_at': (datetime.utcnow() + timedelta(seconds=expiration)).isoformat()
            }

        except ClientError as e:
            logger.error("presigned_url_failed", key=key, error=str(e))
            return {'success': False, 'error': str(e)}

    async def delete_file(self, key: str) -> Dict:
        """
        Delete file from S3

        Note: For HIPAA compliance, consider using versioning instead of
        permanent deletion
        """
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            logger.info("file_deleted_from_s3", bucket=self.bucket_name, key=key)

            return {'success': True, 'deleted_key': key}

        except ClientError as e:
            logger.error("s3_delete_failed", key=key, error=str(e))
            return {'success': False, 'error': str(e)}

    async def list_files(
        self,
        practice_id: str,
        category: Optional[str] = None,
        patient_id: Optional[str] = None,
        max_keys: int = 100
    ) -> Dict:
        """
        List files for a practice/patient

        Args:
            practice_id: Practice ID
            category: Optional category filter
            patient_id: Optional patient ID filter
            max_keys: Maximum number of keys to return

        Returns:
            Dict with success status and list of files
        """
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            # Build prefix
            if category:
                prefix = f"{practice_id}/{category}/"
            else:
                prefix = f"{practice_id}/"

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Get metadata to filter by patient if needed
                    if patient_id:
                        metadata_response = self.s3_client.head_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        file_patient_id = metadata_response.get('Metadata', {}).get('patient-id')

                        if file_patient_id != patient_id:
                            continue

                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag']
                    })

            logger.info(
                "files_listed_from_s3",
                bucket=self.bucket_name,
                prefix=prefix,
                count=len(files)
            )

            return {
                'success': True,
                'files': files,
                'count': len(files),
                'truncated': response.get('IsTruncated', False)
            }

        except ClientError as e:
            logger.error("s3_list_failed", practice_id=practice_id, error=str(e))
            return {'success': False, 'error': str(e)}

    async def copy_file(
        self,
        source_key: str,
        destination_key: str
    ) -> Dict:
        """Copy file within S3"""
        if not self.bucket_name:
            return {'success': False, 'error': 'S3 not configured'}

        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }

            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key,
                ServerSideEncryption='AES256'
            )

            logger.info(
                "file_copied_in_s3",
                source=source_key,
                destination=destination_key
            )

            return {
                'success': True,
                'source_key': source_key,
                'destination_key': destination_key
            }

        except ClientError as e:
            logger.error("s3_copy_failed", source=source_key, error=str(e))
            return {'success': False, 'error': str(e)}


# Global instance
s3_storage = S3StorageService()
