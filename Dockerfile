FROM python:3.11-slim

ENV DATABASE_URL="postgresql+psycopg://tbank:admin-19344-1023982@postgres:5432/PROD"
ENV MINIO_ENDPOINT="http://minio:9000"
ENV MINIO_ACCESS_KEY="minioadmin"
ENV MINIO_SECRET_KEY="minioadmin"
ENV BUCKET_NAME="campaign-images"
ENV REGION_NAME="us-east-1"

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --only main
COPY . /app

EXPOSE 80
CMD ["uvicorn", "src.main:app", "--port", "80", "--host=0.0.0.0", "--root-path", "/api"]