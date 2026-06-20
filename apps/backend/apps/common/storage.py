from __future__ import annotations

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
        return file_field.url
    except Exception:
        return None


def file_key(file_field) -> str | None:
    if not file_field:
        return None
    return file_field.name or None

