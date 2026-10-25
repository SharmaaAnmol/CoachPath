"""
Unit & Integration Tests for Staging Deployment Readiness.
Validates:
1. Dynamic PORT binding (Render support)
2. Database URL scheme normalization (Neon / Supabase / Render asyncpg compatibility)
3. Cookie policies (cross-origin vs same-origin proxy compatibility)
4. Storage service driver instantiation and abstraction contracts
5. Health checks & diagnostic safety (zero secret leakage)
"""

from __future__ import annotations

import os
import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.services.storage import (
    FileStorageException,
    FileStorageService,
    LocalFileStorageService,
    S3FileStorageService,
    create_storage_service,
)


def test_database_url_normalization():
    """Validates that postgres:// and postgresql:// are automatically normalized to asyncpg."""
    # 1. Standard postgresql:// scheme
    s1 = Settings(DATABASE_URL="postgresql://user:pass@ep-neon.tech:5432/db")
    assert s1.DATABASE_URL == "postgresql+asyncpg://user:pass@ep-neon.tech:5432/db"

    # 2. Legacy postgres:// scheme (Render / Heroku)
    s2 = Settings(DATABASE_URL="postgres://user:pass@ep-neon.tech:5432/db")
    assert s2.DATABASE_URL == "postgresql+asyncpg://user:pass@ep-neon.tech:5432/db"

    # 3. Already asyncpg scheme
    s3 = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db")
    assert s3.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/db"

    # 4. SQLite scheme preserved for tests
    s4 = Settings(DATABASE_URL="sqlite+aiosqlite:///:memory:")
    assert s4.DATABASE_URL == "sqlite+aiosqlite:///:memory:"

    # 5. Neon connection string with sslmode=require normalized to ssl=require
    s5 = Settings(DATABASE_URL="postgresql://user:pass@ep-neon.tech:5432/neondb?sslmode=require")
    assert s5.DATABASE_URL == "postgresql+asyncpg://user:pass@ep-neon.tech:5432/neondb?ssl=require"


def test_dynamic_port_injection():
    """Validates that PORT environment variable overrides API_PORT for PaaS runtimes."""
    s = Settings(PORT=10000)
    assert s.API_PORT == 10000


def test_cookie_samesite_and_secure_policies():
    """Validates that cookie secure policies adapt to environment and samesite settings."""
    # Staging default with lax
    s_staging = Settings(ENVIRONMENT="staging", COOKIE_SAMESITE="lax")
    assert s_staging.COOKIE_SECURE is True

    # SameSite=None requires Secure=True even if unspecified
    s_none = Settings(ENVIRONMENT="development", COOKIE_SAMESITE="none")
    assert s_none.COOKIE_SECURE is True


def test_storage_factory_local_driver():
    """Validates default storage provider creates LocalFileStorageService."""
    service = create_storage_service()
    assert isinstance(service, LocalFileStorageService)


def test_storage_factory_s3_driver():
    """Validates STORAGE_PROVIDER='r2' initializes S3FileStorageService."""
    with patch("app.core.config.settings.STORAGE_PROVIDER", "r2"), \
         patch("app.core.config.settings.S3_BUCKET_NAME", "test-bucket"), \
         patch("app.core.config.settings.S3_ACCESS_KEY_ID", "key123"), \
         patch("app.core.config.settings.S3_SECRET_ACCESS_KEY", "secret123"):
        service = create_storage_service()
        assert isinstance(service, S3FileStorageService)
        assert service._bucket == "test-bucket"


@pytest.mark.asyncio
async def test_s3_storage_mocked_lifecycle():
    """Validates save, read, delete, exists workflow on S3FileStorageService using mock boto3 client."""
    s3_service = S3FileStorageService(
        bucket_name="mock-bucket",
        endpoint_url="https://r2.mock.cloudflarestorage.com",
        access_key_id="mock_key",
        secret_access_key="mock_secret",
    )

    mock_boto_client = MagicMock()
    mock_boto_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"%PDF-1.4 mock content")
    }
    mock_boto_client.head_object.return_value = {"ContentLength": 19}
    s3_service._client = mock_boto_client

    test_user_id = uuid.uuid4()
    pdf_bytes = b"%PDF-1.4 test resume"

    # 1. Save file
    storage_path = await s3_service.save_file(test_user_id, pdf_bytes, "pdf")
    assert storage_path.startswith(str(test_user_id))
    assert storage_path.endswith(".pdf")
    mock_boto_client.put_object.assert_called_once()

    # 2. File exists
    exists = await s3_service.file_exists(storage_path)
    assert exists is True

    # 3. Read file
    content = await s3_service.read_file(storage_path)
    assert content == b"%PDF-1.4 mock content"

    # 4. Delete file
    deleted = await s3_service.delete_file(storage_path)
    assert deleted is True
    mock_boto_client.delete_object.assert_called_once()

    # 5. Unsupported extension rejected
    with pytest.raises(FileStorageException):
        await s3_service.save_file(test_user_id, b"malicious", "exe")


@pytest.mark.asyncio
async def test_health_and_root_endpoints_safety(client: AsyncClient):
    """Validates that public health endpoints do not leak internal secrets or connection strings."""
    # Root endpoint
    r_root = await client.get("/")
    assert r_root.status_code == 200
    data_root = r_root.json()
    assert "password" not in str(data_root).lower()
    assert "secret" not in str(data_root).lower()
    assert "postgres" not in str(data_root).lower()

    # Health liveness
    r_health = await client.get("/api/v1/health")
    assert r_health.status_code == 200
    data_health = r_health.json()
    assert data_health["status"] == "healthy"
    assert "password" not in str(data_health).lower()
    assert "api_key" not in str(data_health).lower()

    # Readiness probe
    r_ready = await client.get("/api/v1/ready")
    assert r_ready.status_code in (200, 503)
    data_ready = r_ready.json()
    assert "password" not in str(data_ready).lower()
    assert "coachpath_password" not in str(data_ready).lower()
