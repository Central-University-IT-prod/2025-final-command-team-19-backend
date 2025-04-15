import os

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from src.api.routes.clients import router as client_router
from src.api.routes.partners import router as partner_router
from src.api.schemas.default_schemas import *
from src.api.services.auth_service import AuthService
from src.api.services.db_service import get_session, create_table
from src.api.services.s3_service import S3Service

app = FastAPI(
    title="LoyalT",
    description="Сервис для упрощения управления программами лояльности для бизнесов",
    version="1.0.0",
)

app.include_router(client_router)
app.include_router(partner_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_table()

@app.on_event("startup")
async def startup_event():
    """Инициализирует S3 при запуске приложения."""
    await S3Service().initialize_s3()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Loyalty",
        version="1.0.0",
        description="Сервис программ лояльностей",
        routes=app.routes,

    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {  # Match the name you'll use in the endpoint's security property
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter the token with the `Bearer ` prefix, e.g., 'Bearer YOUR_TEST_TOKEN'."
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    raise HTTPException(status_code=400, detail="Ошибка в данных запроса.")

@app.get("/ping",
         summary="Пинг",
         description="Проверка работоспособности сервера",
         response_model=Ping,
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": {
                             "status": "PROOOOOOOOOOOOOOOOOD"
                         }
                     }
                 },
             },
         }
         )
async def ping():
    return {"status": "PROOOOOOOOOOOOOOOOOD"}

@app.get("/get/role",
         summary="Получение роли",
         description="Получение роли пользователя по jwt",
         response_model=Role,
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": {
                             "role": "CLIENT",
                             "user_id": "4a0804e2-1a60-48be-bd56-4915982bc0b9",
                         }
                     }
                 },
             },
             401: {
                 "description": "Not Authorized",
                 "content": {
                     "application/json": {
                         "example": {
                             "detail": "Invalid token",
                         }
                     }
                 }
             }
         }
         )
async def get_role(token: str = Depends(oauth2_scheme)):
    return AuthService(db=get_session()).get_role(token)


if __name__ == "__main__":
    server_address = os.getenv("SERVER_ADDRESS", "REDACTED")
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))
