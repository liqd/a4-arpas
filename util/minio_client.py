import logging
from datetime import timedelta

import boto3
from django.conf import settings
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class MinIOClient:
    @cached_property
    def client(self):
        if all(
            attr in settings.MINIO_DATA
            for attr in ["endpoint", "accessKey", "secretKey", "allowed_buckets"]
        ):
            return boto3.client(
                "s3",
                endpoint_url=settings.MINIO_DATA.get("endpoint"),
                aws_access_key_id=settings.MINIO_DATA.get("accessKey"),
                aws_secret_access_key=settings.MINIO_DATA.get("secretKey"),
                region_name=settings.MINIO_DATA.get("region", "eu-central-1"),
                config=boto3.session.Config(signature_version="s3v4"),
            )
        else:
            logger.error(
                "Failed to generate MinIO client, check environment variables and MINIO_DATA settings."
            )
            return None

    def get_presigned_url(self, mesh_id, expires=timedelta(hours=1)):
        try:
            parts = mesh_id.split("/", 1)
            bucket_name = parts[0]
            allowed_buckets = settings.MINIO_DATA.get("allowed_buckets")
            if bucket_name in allowed_buckets:
                object_name = parts[1]
                # Use generate_presigned_url from boto3
                url = self.client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=int(expires.total_seconds()),
                )
                print(f"url: {url}")
                return url
            else:
                logger.error(f"Access to bucket {bucket_name} is not allowed.")
                return None
        except Exception as e:
            # Debug variables -> remove after
            endpoint = settings.MINIO_DATA.get("endpoint")
            parts = mesh_id.split("/", 1)
            bucket_name = parts[0]
            object_name = parts[1]
            # end debug
            logger.error(
                f"Failed to generate presigned URL for {mesh_id}: {str(e)}, endpoint: {endpoint}, bucket_name: {bucket_name}, object_name: {object_name}"
            )
            return None


minio_client = MinIOClient()
