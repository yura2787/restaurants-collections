import uuid as uuid_lib
import aioboto3
from fastapi import UploadFile, HTTPException, status

from settings import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE_MB = 5


class S3Storage:
    def __init__(self):
        self.bucket_name = settings.BUCKET_NAME

    async def get_s3_session(self):
        session = aioboto3.Session()
        async with session.client(
                's3',
                endpoint_url=settings.ENDPOINT,
                aws_access_key_id=settings.ACCESS_KEY,
                aws_secret_access_key=settings.SECRET_KEY,
                region_name='auto'
        ) as s3:
            yield s3

    async def upload_product_image(self, file: UploadFile, restaurant_uuid: str) -> str:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"
            )
        await file.seek(0)

        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "jpg"
        safe_filename = f"{uuid_lib.uuid4()}.{ext}"
        path = f'restaurant/{restaurant_uuid}/{safe_filename}'

        async for s3_client in self.get_s3_session():
            await s3_client.upload_fileobj(file, self.bucket_name, path)
            url = f"{settings.PUBLIC_URL}/{path}"

        return url


s3_storage = S3Storage()