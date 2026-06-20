from __future__ import annotations

import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


REQUIRED_SETTINGS = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_S3_REGION_NAME",
    "AWS_MEDIA_LOCATION",
    "AWS_SEED_ASSET_LOCATION",
]


class Command(BaseCommand):
    help = "Validate required S3 configuration and optionally run a real S3 write smoke test."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Fail if any required value is missing or S3 is unreachable.")
        parser.add_argument("--skip-write", action="store_true", help="Only run head_bucket, not put/delete object.")

    def handle(self, *args, **options):
        missing = [name for name in REQUIRED_SETTINGS if not getattr(settings, name, "")]
        if missing:
            message = f"Missing required S3 settings: {', '.join(missing)}"
            if options["strict"]:
                raise CommandError(message)
            self.stdout.write(self.style.WARNING(message))
            return

        client_kwargs = {
            "service_name": "s3",
            "region_name": settings.AWS_S3_REGION_NAME,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "aws_session_token": settings.AWS_SESSION_TOKEN or None,
            "config": Config(signature_version="s3v4"),
        }
        if settings.AWS_S3_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
        client = boto3.client(**client_kwargs)

        try:
            client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            if not options["skip_write"]:
                key = f"{settings.AWS_SEED_ASSET_LOCATION}/health/{uuid.uuid4()}.txt"
                client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, Body=b"ok", ContentType="text/plain")
                client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        except Exception as exc:
            if options["strict"]:
                raise CommandError(f"S3 validation failed: {exc}") from exc
            self.stdout.write(self.style.WARNING(f"S3 validation failed: {exc}"))
            return

        self.stdout.write(self.style.SUCCESS("S3 configuration validated."))

