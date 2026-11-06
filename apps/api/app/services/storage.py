"""Object storage adapter — local filesystem by default, S3-compatible when configured."""

from __future__ import annotations

import hashlib
from pathlib import Path

import boto3
from botocore.client import Config

from app.core.config import get_settings


class ObjectStorage:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.local_root = Path(self.settings.local_storage_dir)
        self.local_root.mkdir(parents=True, exist_ok=True)

    @property
    def use_s3(self) -> bool:
        return bool(self.settings.s3_access_key and self.settings.storage_backend == "s3")

    def put_bytes(self, *, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        if self.use_s3:
            client = boto3.client(
                "s3",
                endpoint_url=self.settings.s3_endpoint_url or None,
                aws_access_key_id=self.settings.s3_access_key,
                aws_secret_access_key=self.settings.s3_secret_key,
                region_name=self.settings.s3_region,
                config=Config(signature_version="s3v4"),
            )
            client.put_object(
                Bucket=self.settings.s3_bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            return key

        path = self.local_root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def get_bytes(self, key: str) -> bytes:
        if self.use_s3:
            client = boto3.client(
                "s3",
                endpoint_url=self.settings.s3_endpoint_url or None,
                aws_access_key_id=self.settings.s3_access_key,
                aws_secret_access_key=self.settings.s3_secret_key,
                region_name=self.settings.s3_region,
                config=Config(signature_version="s3v4"),
            )
            obj = client.get_object(Bucket=self.settings.s3_bucket, Key=key)
            return obj["Body"].read()
        return (self.local_root / key).read_bytes()

    def delete(self, key: str) -> None:
        if self.use_s3:
            client = boto3.client(
                "s3",
                endpoint_url=self.settings.s3_endpoint_url or None,
                aws_access_key_id=self.settings.s3_access_key,
                aws_secret_access_key=self.settings.s3_secret_key,
                region_name=self.settings.s3_region,
                config=Config(signature_version="s3v4"),
            )
            client.delete_object(Bucket=self.settings.s3_bucket, Key=key)
            return
        path = self.local_root / key
        if path.exists():
            path.unlink()

    @staticmethod
    def checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


object_storage = ObjectStorage()
