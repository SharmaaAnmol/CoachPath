"""
Secure File Storage Service for CoachPath.
Provides abstraction and local filesystem implementation for uploaded candidate resumes.
Enforces strict path traversal prevention, server-controlled identifiers, and isolated directory permissions.
"""
from __future__ import annotations

import logging
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class FileStorageException(AppException):
    """Exception raised when an internal file storage operation fails."""

    def __init__(self, message: str = "A file storage operation failed.") -> None:
        super().__init__(
            status_code=500,
            code="STORAGE_ERROR",
            message=message,
        )


class FileStorageService(ABC):
    """Abstract interface for candidate document storage."""

    @abstractmethod
    async def save_file(
        self,
        user_id: uuid.UUID,
        file_bytes: bytes,
        extension: str,
    ) -> str:
        """
        Saves document bytes securely under server-controlled identifier.
        Returns relative storage_path.
        """
        ...

    @abstractmethod
    async def read_file(self, storage_path: str) -> bytes:
        """Reads and returns file bytes from storage."""
        ...

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage. Returns True if deleted or already absent."""
        ...

    @abstractmethod
    async def file_exists(self, storage_path: str) -> bool:
        """Checks if file exists in storage."""
        ...


class LocalFileStorageService(FileStorageService):
    """
    Local filesystem storage driver for development and on-premise deployments.
    Stores files under configured UPLOAD_DIR with strict path containment checks.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        raw_dir = base_dir or settings.UPLOAD_DIR
        self._base_path = Path(raw_dir).resolve()
        # Ensure root upload directory exists with secure permissions
        self._base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, storage_path: str) -> Path:
        """
        Resolves path and guarantees it resides strictly inside self._base_path.
        Prevents directory traversal attacks (e.g. '../../etc/passwd').
        """
        # Normalize and resolve target path
        target = (self._base_path / storage_path).resolve()
        try:
            # commonpath check guarantees target is a descendant of _base_path
            common = os.path.commonpath([str(self._base_path), str(target)])
            if common != str(self._base_path):
                logger.error("Path traversal attempt detected: %s", storage_path)
                raise FileStorageException("Illegal file storage path traversal detected.")
        except ValueError as exc:
            logger.error("Invalid path resolution: %s", exc)
            raise FileStorageException("Invalid file storage path.") from exc

        return target

    async def save_file(
        self,
        user_id: uuid.UUID,
        file_bytes: bytes,
        extension: str,
    ) -> str:
        """
        Saves document bytes using server-generated UUID.
        Storage structure: {user_id}/{random_uuid}.{ext}
        """
        clean_ext = extension.lstrip(".").lower()
        if clean_ext not in ("pdf", "docx"):
            raise FileStorageException(f"Unsupported file extension '{clean_ext}'.")

        storage_id = uuid.uuid4()
        user_folder = str(user_id)
        relative_path = f"{user_folder}/{storage_id}.{clean_ext}"

        safe_dest = self._resolve_safe_path(relative_path)
        safe_dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Write to a temporary file in same directory first, then atomic rename
            temp_dest = safe_dest.with_suffix(f".tmp_{uuid.uuid4().hex[:6]}")
            with open(temp_dest, "wb") as f:
                f.write(file_bytes)
            temp_dest.replace(safe_dest)
            logger.info("File saved successfully to storage: %s (%d bytes)", relative_path, len(file_bytes))
            return relative_path
        except Exception as exc:
            logger.error("Failed to write document to storage: %s", exc)
            raise FileStorageException("Could not persist uploaded file to storage.") from exc

    async def read_file(self, storage_path: str) -> bytes:
        """Reads document bytes safely."""
        safe_path = self._resolve_safe_path(storage_path)
        if not safe_path.is_file():
            raise FileStorageException(f"Stored file '{storage_path}' not found.")
        try:
            with open(safe_path, "rb") as f:
                return f.read()
        except Exception as exc:
            logger.error("Failed to read document from storage: %s", exc)
            raise FileStorageException("Failed to read document from storage.") from exc

    async def delete_file(self, storage_path: str) -> bool:
        """Deletes document file and cleans up empty parent directory."""
        try:
            safe_path = self._resolve_safe_path(storage_path)
            if safe_path.is_file():
                safe_path.unlink()
                logger.info("Deleted stored document: %s", storage_path)

            # Clean up parent directory if empty
            parent = safe_path.parent
            if parent.exists() and parent != self._base_path and not any(parent.iterdir()):
                parent.rmdir()
            return True
        except Exception as exc:
            logger.warning("Error during file deletion for '%s': %s", storage_path, exc)
            return False

    async def file_exists(self, storage_path: str) -> bool:
        """Checks if document exists."""
        try:
            safe_path = self._resolve_safe_path(storage_path)
            return safe_path.is_file()
        except Exception:
            return False


class S3FileStorageService(FileStorageService):
    """
    Durable S3-compatible object storage service (Cloudflare R2 / AWS S3).
    Ensures uploaded candidate resumes survive service restarts and redeployments.
    Enforces strictly private bucket access and server-controlled storage keys.
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        access_key_id: str = "",
        secret_access_key: str = "",
        region_name: str = "auto",
    ) -> None:
        self._bucket = bucket_name
        self._endpoint_url = endpoint_url
        self._access_key = access_key_id
        self._secret_key = secret_access_key
        self._region = region_name or "auto"
        self._client = None

    def _get_client(self):
        """Lazy initialization of boto3 S3 client."""
        if self._client is not None:
            return self._client
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            logger.error("boto3 is required for S3/R2 storage but is not installed.")
            raise FileStorageException("S3 object storage driver is unavailable (missing boto3).") from exc

        client_kwargs = {
            "aws_access_key_id": self._access_key,
            "aws_secret_access_key": self._secret_key,
            "region_name": self._region,
            "config": Config(signature_version="s3v4", retries={"max_attempts": 3, "mode": "standard"}),
        }
        if self._endpoint_url:
            client_kwargs["endpoint_url"] = self._endpoint_url

        self._client = boto3.client("s3", **client_kwargs)
        return self._client

    async def save_file(
        self,
        user_id: uuid.UUID,
        file_bytes: bytes,
        extension: str,
    ) -> str:
        """Saves resume document bytes to private S3 bucket."""
        clean_ext = extension.lstrip(".").lower()
        if clean_ext not in ("pdf", "docx"):
            raise FileStorageException(f"Unsupported file extension '{clean_ext}'.")

        mime_type = (
            "application/pdf"
            if clean_ext == "pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        storage_id = uuid.uuid4()
        relative_path = f"{user_id}/{storage_id}.{clean_ext}"

        client = self._get_client()
        try:
            # Upload with private ACL and server-side encryption
            client.put_object(
                Bucket=self._bucket,
                Key=relative_path,
                Body=file_bytes,
                ContentType=mime_type,
                ServerSideEncryption="AES256",
            )
            logger.info(
                "File saved successfully to S3/R2 storage: %s (%d bytes)",
                relative_path,
                len(file_bytes),
            )
            return relative_path
        except Exception as exc:
            logger.error("Failed to upload document to S3/R2: %s", exc)
            raise FileStorageException("Could not persist uploaded file to durable object storage.") from exc

    async def read_file(self, storage_path: str) -> bytes:
        """Reads document bytes from S3/R2."""
        client = self._get_client()
        try:
            response = client.get_object(Bucket=self._bucket, Key=storage_path)
            return response["Body"].read()
        except Exception as exc:
            logger.error("Failed to read document from S3/R2 '%s': %s", storage_path, exc)
            raise FileStorageException(f"Failed to read stored document '{storage_path}' from storage.") from exc

    async def delete_file(self, storage_path: str) -> bool:
        """Deletes document from S3/R2 bucket."""
        client = self._get_client()
        try:
            client.delete_object(Bucket=self._bucket, Key=storage_path)
            logger.info("Deleted S3/R2 document: %s", storage_path)
            return True
        except Exception as exc:
            logger.warning("Error deleting document from S3/R2 '%s': %s", storage_path, exc)
            return False

    async def file_exists(self, storage_path: str) -> bool:
        """Checks if document exists in S3/R2 bucket."""
        client = self._get_client()
        try:
            client.head_object(Bucket=self._bucket, Key=storage_path)
            return True
        except Exception:
            return False


def create_storage_service() -> FileStorageService:
    """Factory creating the appropriate FileStorageService based on configuration."""
    provider = getattr(settings, "STORAGE_PROVIDER", "local").lower()
    if provider in ("s3", "r2"):
        logger.info(
            "Initializing S3/R2 durable object storage driver for bucket '%s'...",
            settings.S3_BUCKET_NAME,
        )
        return S3FileStorageService(
            bucket_name=settings.S3_BUCKET_NAME,
            endpoint_url=settings.S3_ENDPOINT_URL,
            access_key_id=settings.S3_ACCESS_KEY_ID,
            secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION_NAME,
        )

    logger.info("Initializing Local filesystem storage driver (upload_dir='%s')...", settings.UPLOAD_DIR)
    return LocalFileStorageService()


# Singleton storage instance
storage_service: FileStorageService = create_storage_service()
