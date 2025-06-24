import logging
from datetime import timedelta

from django.conf import settings
from django.utils.functional import cached_property
from minio import Minio

logger = logging.getLogger(__name__)


class MinIOClient:
    @cached_property
    def client(self):
        return Minio(
            settings.MINIO_DATA["endpoint"],
            access_key=settings.MINIO_DATA["accessKey"],
            secret_key=settings.MINIO_DATA["secretKey"],
            secure=True,
        )

    def get_presigned_url(self, mesh_id, expires=timedelta(hours=1)):
        if not mesh_id:
            return None

        try:
            parts = mesh_id.split("/", 1)
            object_name = parts[1]
            return self.client.presigned_get_object(
                settings.MINIO_DATA["bucket"], object_name, expires=expires
            )
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {mesh_id}: {str(e)}")
            return None


minio_client = MinIOClient()
