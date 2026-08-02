"""Storage abstraction supporting local disk and S3-compatible backends.

The concrete backend is selected by ``settings.storage_backend`` so the
platform can migrate from local storage to AWS S3 without changing callers.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ValidationError


class StorageBackend(ABC):
    """Interface implemented by concrete storage providers."""

    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Persist bytes under ``key`` and return the storage key."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read bytes stored under ``key``."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove the object stored under ``key``."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether ``key`` exists."""


class LocalStorageBackend(StorageBackend):
    """Stores files on the local filesystem under a configurable root."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        # Prevent path traversal: keys must be relative and within the root.
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValidationError("Invalid storage key")
        return path

    def save(self, key: str, data: bytes) -> str:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def read(self, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()


class S3StorageBackend(StorageBackend):
    """S3-backed storage. Requires boto3; lazily imported."""

    def __init__(self) -> None:
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ValidationError("boto3 is required for S3 storage") from exc
        if not settings.s3_bucket:
            raise ValidationError("S3_BUCKET is not configured")
        self.client = boto3.client(
            "s3",
            region_name=settings.s3_region or None,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
        self.bucket = settings.s3_bucket

    def save(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return key

    def read(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


def get_storage() -> StorageBackend:
    """Build the storage backend selected by configuration."""
    if settings.storage_backend == "s3":
        return S3StorageBackend()
    return LocalStorageBackend(settings.storage_local_path)


def build_storage_key(*, user_id: int, filename: str, content: bytes) -> str:
    """Build a collision-safe, path-safe storage key."""
    digest = hashlib.sha256(content).hexdigest()[:16]
    safe_name = Path(filename).name
    return f"resumes/{user_id}/{digest}_{safe_name}"
