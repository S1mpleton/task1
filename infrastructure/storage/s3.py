import boto3
from botocore.client import BaseClient

from botocore.config import Config
from botocore.exceptions import ClientError

from infrastructure.storage.config import settings, EXPIRES_IN


# YouTube code
class S3Storage:
    def __init__(self):
        self.bucket = settings.s3_bucket
        self._client = self._create_client()

    @staticmethod
    def _create_client() -> BaseClient:
        session = boto3.session.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.s3_region,
        )

        return session.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def get_object_info(self, object_key: str) -> dict:
        return self._client.head_object(
            Bucket=self.bucket,
            Key=object_key,
        )

    def object_exists(self, object_key: str) -> bool:
        try:
            self.get_object_info(object_key)
            return True

        except ClientError as exc:
            code = exc.response["Error"]["Code"]

            if code in {"404", "NoSuchKey", "NotFound"}:
                return False

            raise

    def generate_upload_url(self, object_key: str, content_type: str) -> str:
        return self._client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=EXPIRES_IN,
            HttpMethod="PUT",
        )

    def initiate_multipart(self, object_key: str, content_type: str) -> str:
        response = self._client.create_multipart_upload(
            Bucket=self.bucket,
            Key=object_key,
            ContentType=content_type,
        )
        return response["UploadId"]

    def generate_part_upload_url(
            self,
            object_key: str,
            upload_id: str,
            part_number: int,
    ) -> str:
        return self._client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=EXPIRES_IN,
            HttpMethod="PUT",
        )

    def abort_multipart(self, object_key: str, upload_id: str) -> None:
        self._client.abort_multipart_upload(
            Bucket=self.bucket,
            Key=object_key,
            UploadId=upload_id,
        )

    def list_uploaded_parts(
            self,
            object_key: str,
            upload_id: str,
    ) -> list[dict]:
        parts = []
        paginator = self._client.get_paginator("list_parts")

        pages = paginator.paginate(
            Bucket=self.bucket,
            Key=object_key,
            UploadId=upload_id,
        )

        for page in pages:
            for part in page.get("Parts", []):
                parts.append({
                    "PartNumber": part["PartNumber"],
                    "ETag": part["ETag"],
                })

        return sorted(
            parts,
            key=lambda item: item["PartNumber"],
        )

    def complete_multipart(
            self,
            object_key: str,
            upload_id: str,
            parts: list[dict],
    ) -> None:

        if not parts:
            raise ValueError("No uploaded parts")

        self._client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=object_key,
            UploadId=upload_id,
            MultipartUpload={
                "Parts": parts,
            },
        )

    def generate_download_url(self,object_key: str) -> str:
        return self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
            },
            ExpiresIn=EXPIRES_IN,
            HttpMethod="GET",
        )

    def delete_object(self, object_key: str) -> None:
        self._client.delete_object(
            Bucket=self.bucket,
            Key=object_key,
        )

    def close(self) -> None:
        self._client.close()