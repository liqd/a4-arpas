import boto3
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class GenerateMinioPresignedUrlView(APIView):
    def post(self, request):
        mesh_id = request.data.get("mesh_id")
        action = request.data.get("action", "get_object")
        expiration = request.data.get("expiration", 3600)

        if not mesh_id:
            return Response(
                {"error": "mesh_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Split Mesh_id in bucket_name & object_name
        parts = mesh_id.split("/", 1)
        if len(parts) < 2:
            return Response(
                {"error": "Invalid mesh_id format. Expected 'bucket/object_path'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bucket_name = parts[0]
        object_name = parts[1]

        if not bucket_name or not object_name:
            return Response(
                {"error": "bucket_name and object_name are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.MINIO_DATA["endpoint"],
                aws_access_key_id=settings.MINIO_DATA["accessKey"],
                aws_secret_access_key=settings.MINIO_DATA["secretKey"],
                config=boto3.session.Config(signature_version="s3v4"),
                use_ssl=settings.MINIO_DATA["secure"],
                region_name=settings.MINIO_DATA["region"],
            )

            if action == "get_object":
                presigned_url = s3_client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": bucket_name, "Key": object_name},
                    ExpiresIn=expiration,
                )
            else:
                return Response(
                    {"error": "Invalid action. Must be 'get_object' or 'put_object'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({"presigned_url": presigned_url})

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
