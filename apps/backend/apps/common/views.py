from __future__ import annotations

import boto3
from botocore.config import Config
from django.conf import settings
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()
        return Response({"status": "ok", "database": "ok"})


class DeepHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks = {"database": "ok", "s3": "unknown"}
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()

        client_kwargs = {
            "service_name": "s3",
            "region_name": settings.AWS_S3_REGION_NAME,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID or None,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY or None,
            "aws_session_token": settings.AWS_SESSION_TOKEN or None,
            "config": Config(signature_version="s3v4"),
        }
        if settings.AWS_S3_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
        client = boto3.client(**client_kwargs)
        client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        checks["s3"] = "ok"
        return Response({"status": "ok", "checks": checks})

