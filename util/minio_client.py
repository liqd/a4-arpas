import logging
from datetime import timedelta

from django.conf import settings
from django.utils.functional import cached_property
from minio import Minio

logger = logging.getLogger(__name__)


class MinIOClient:
    @cached_property
    def client(self):
        if all(
            attr in settings.MINIO_DATA
            for attr in ["endpoint", "accessKey", "secretKey", "allowed_buckets"]
        ):
            return Minio(
                settings.MINIO_DATA.get("endpoint"),
                access_key=settings.MINIO_DATA.get("accessKey"),
                secret_key=settings.MINIO_DATA.get("secretKey"),
                secure=True,
            )
        else:
            logger.error(
                "Failed to generate MinIO client, check environment variables."
            )
            return None

    def get_presigned_url(self, mesh_id, expires=timedelta(hours=1)):
        try:
            parts = mesh_id.split("/", 1)
            bucket_name = parts[0]
            allowed_buckets = settings.MINIO_DATA.get("allowed_buckets")
            if bucket_name in allowed_buckets:
                object_name = parts[1]
                return self.client.presigned_get_object(
                    bucket_name, object_name, expires=expires
                )
            else:
                logger.error(f"Access to bucket {bucket_name} is not allowed.")
                return None
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {mesh_id}: {str(e)}")
            return None


minio_client = MinIOClient()
