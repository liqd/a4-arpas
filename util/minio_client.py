# utils/minio_utils.py
import logging
from datetime import timedelta

from django.conf import settings
from minio import Minio

logger = logging.getLogger(__name__)

_minio_client = None


def get_minio_client():
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.MINIO_DATA["endpoint"],
            access_key=settings.MINIO_DATA["accessKey"],
            secret_key=settings.MINIO_DATA["secretKey"],
            secure=True,
        )
    return _minio_client


def get_presigned_url(mesh_id, expires=timedelta(hours=1)):
    if not mesh_id:
        return None

    try:
        client = get_minio_client()
        bucket_name = settings.MINIO_DATA["bucket"]
        parts = object_name = mesh_id.split("/", 1)
        object_name = parts[1]
        return client.presigned_get_object(bucket_name, object_name, expires=expires)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for {mesh_id}: {str(e)}")
        return None
