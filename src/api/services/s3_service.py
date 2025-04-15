from fastapi import UploadFile, HTTPException
from src.api.repos.s3_utils import upload_file, get_file_url, download_file, delete_file, create_bucket
import os
from aiobotocore.session import get_session
from io import BytesIO
from PIL import Image

BUCKET_NAME = os.getenv("BUCKET_NAME")
TARGET_SIZE = (200, 200)


class S3Service:
    async def initialize_s3(self):
        """Инициализирует бакет при запуске приложения."""
        session = get_session()
        await create_bucket(session, BUCKET_NAME)

    def resize_image(self, image_bytes) -> bytes:
        """Изменяет размер изображения до TARGET_SIZE."""
        try:
            img = Image.open(BytesIO(image_bytes))
            img = img.convert("RGB")  # Ensure image is in RGB format
            img = img.resize(TARGET_SIZE)  # Resize using LANCZOS resampling
            img_io = BytesIO()
            img.save(img_io, "JPEG", quality=90)  # Save as JPEG with quality 90
            img_io.seek(0)  # Reset file pointer to the beginning
            return img_io.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image processing error: {e}")

    async def upload_image_service(self, file: UploadFile, campaign_id: str):
        object_name = f"{campaign_id}.png"

        image_bytes = file.read()
        resized_image_bytes = self.resize_image(image_bytes)  # Resize the image

        message = await upload_file(resized_image_bytes, object_name)

        image_url = await get_file_url(object_name)
        return {"message": "Изображение загружено"}

    async def get_image_service(self, image_name: str) -> bytes:
        """Получает изображение из S3."""
        image_data = await download_file(image_name)
        return image_data

    async def delete_image_service(self, image_name: str) -> dict:
        """Удаляет изображение из S3."""
        message = await delete_file(image_name)
        return {"message": message}
