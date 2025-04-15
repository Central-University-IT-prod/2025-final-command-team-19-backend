from aiobotocore.session import get_session
import os
from fastapi import HTTPException

# Загрузка конфигурации из переменных окружения (или установите значения по умолчанию)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

async def create_bucket(session, bucket_name):
    async with session.create_client("s3", endpoint_url=MINIO_ENDPOINT,
                                      aws_access_key_id=MINIO_ACCESS_KEY,
                                      aws_secret_access_key=MINIO_SECRET_KEY,
                                      region_name=REGION_NAME) as client:
        try:
            await client.create_bucket(Bucket=bucket_name)
        except Exception as e:
            print(f"Bucket creation error: {e}")  # Handle appropriately - bucket might already exist


async def upload_file(file_bytes, object_name: str, bucket_name: str = BUCKET_NAME):
    """Загружает файл в MinIO."""
    session = get_session()
    async with session.create_client("s3", endpoint_url=MINIO_ENDPOINT,
                                      aws_access_key_id=MINIO_ACCESS_KEY,
                                      aws_secret_access_key=MINIO_SECRET_KEY,
                                      region_name=REGION_NAME) as client:
        try:
            await client.put_object(Bucket=bucket_name, Key=object_name, Body=file_bytes)
            return object_name
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


async def get_file_url(object_name: str, bucket_name: str = BUCKET_NAME):
    """Возвращает URL для доступа к файлу в MinIO."""
    return f"{MINIO_ENDPOINT}/{bucket_name}/{object_name}"


async def download_file(object_name: str, bucket_name: str = BUCKET_NAME):
    """Скачивает файл из MinIO и возвращает его содержимое."""
    session = get_session()
    async with session.create_client("s3", endpoint_url=MINIO_ENDPOINT,
                                      aws_access_key_id=MINIO_ACCESS_KEY,
                                      aws_secret_access_key=MINIO_SECRET_KEY,
                                      region_name=REGION_NAME) as client:
        try:
            response = await client.get_object(Bucket=bucket_name, Key=object_name)
            return response['Body']  # Return the content directly

        except Exception as e:
            raise HTTPException(status_code=404, detail="Изображение не найдено")


async def delete_file(object_name: str, bucket_name: str = BUCKET_NAME):
    """Удаляет файл из MinIO."""
    session = get_session()
    async with session.create_client("s3", endpoint_url=MINIO_ENDPOINT,
                                      aws_access_key_id=MINIO_ACCESS_KEY,
                                      aws_secret_access_key=MINIO_SECRET_KEY,
                                      region_name=REGION_NAME) as client:
        try:
            await client.delete_object(Bucket=bucket_name, Key=object_name)
            return f"File deleted"
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))