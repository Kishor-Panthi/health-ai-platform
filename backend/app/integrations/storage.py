from __future__ import annotations

import pathlib
from typing import BinaryIO

import structlog

from app.core.config import settings

logger = structlog.get_logger('storage')


class StorageProvider:
    async def upload(self, *, key: str, file_obj: BinaryIO) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: pathlib.Path | None = None):
        self.base_path = base_path or pathlib.Path('storage')
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(self, *, key: str, file_obj: BinaryIO) -> str:
        destination = self.base_path / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('wb') as handle:
            handle.write(file_obj.read())
        logger.info('storage.upload', key=key)
        return str(destination)


def get_storage_provider() -> StorageProvider:
    if settings.aws_s3_bucket:
        logger.info('storage.stub', bucket=settings.aws_s3_bucket)
    return LocalStorageProvider()