from __future__ import annotations

import boto3
from botocore.config import Config
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = settings.AWS_MEDIA_LOCATION
    file_overwrite = False
    default_acl = None
    querystring_auth = True
    querystring_expire = settings.AWS_PRESIGNED_URL_EXPIRE_SECONDS
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN or None


def file_url(file_field) -> str | None:
    if not file_field:
        return None
    try:
        key = f"{settings.AWS_MEDIA_LOCATION}/{file_field.name}".strip("/")
        client_kwargs = {
            "region_name": settings.AWS_S3_REGION_NAME,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "config": Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        }
        if settings.AWS_SESSION_TOKEN:
            client_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
        if settings.AWS_S3_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
        client = boto3.client("s3", **client_kwargs)
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
            ExpiresIn=settings.AWS_PRESIGNED_URL_EXPIRE_SECONDS,
        )
    except Exception:
        return None


def file_key(file_field) -> str | None:
    if not file_field:
        return None
    return file_field.name or None
