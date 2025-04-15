from io import BytesIO
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from src.api.schemas.partner_schemas import *
from src.api.services.partner_service import PartnerService
from src.api.services.auth_service import AuthService
from src.api.services.s3_service import S3Service
from src.api.services.db_service import get_session
from src.api.schemas.default_schemas import *
import base64

router = APIRouter(prefix="/partner", tags=["partner"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/auth/sign-up",
             summary="Регистрация партнёра",
             description="Регистрация партнёра",
             response_model=Auth,
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {
                                 "token": "REDACTED.eyJ1c2VyX2lkIjoiYzU5N2JkODgtMDZmZC00YmVhLTg3OGMtNzQ0YTE2Zjg5NDEzIiwiZXhwIjoxNzQwODgyMjIwfQ.AN1hhfR5qdINChtA4CqVTVMFl85hSf6NtVQaL5180FY"
                             }
                         }
                     },
                 },
                 400: {
                     "description": "Error in validation",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Ошибка в данных запроса"}
                         }
                     },
                 },
                 401: {
                     "description": "Invalid token",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Невалидный токен"}
                         }
                     },
                 },
                 409: {
                     "description": "Same email",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Такая почта уже зарегистрирована"}
                         }
                     },
                 },
             })
async def create_partner(data: PartnerDataRegistration):
    return AuthService(db=get_session()).registration_partner(data)


@router.post("/auth/sign-in",
             summary="Авторизация партнёра",
             description="Авторизация партнёра в системе. При успешном вызове возвращает JWT токен.",
             response_model=Auth,
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {
                                 "token": "REDACTED.eyJ1c2VyX2lkIjoiYzU5N2JkODgtMDZmZC00YmVhLTg3OGMtNzQ0YTE2Zjg5NDEzIiwiZXhwIjoxNzQwODgyMjIwfQ.AN1hhfR5qdINChtA4CqVTVMFl85hSf6NtVQaL5180FY"
                             }
                         }
                     },
                 },
                 401: {
                     "description": "Incorrect email or password",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Неверный email или пароль"}
                         }
                     },
                 },
             })
async def authorization_partner(data: PartnerDataAuthorization):
    return AuthService(db=get_session()).authorization_partner(data.email, data.password)


@router.get("/profile",
            summary="Профиль партнёра",
            description="Получение данных профиля партнёра",
            response_model=GetProfile,
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "name": "Евгений Шмат",
                                "email": "proood@tbank.ru"

                            }
                        }
                    },
                },
                401: {
                    "description": "Invalid token",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Невалидный токен"}
                        }
                    },
                },
                404: {
                    "description": "Profile not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "При получениии профиля произошла ошибка. Попробуйте позже"}
                        }
                    },
                },
            })
async def get_partner_profile(token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).get_partner_profile(partner_id)


@router.patch("/profile",
              summary="Изменение профиля партнёра",
              description=" Изменение данных профиля партнёра",
              response_model=PatchProfile,
              responses={
                  200: {
                      "description": "Successful Response",
                      "content": {
                          "application/json": {
                              "example": {
                                  "name": "Роман Калмыков",
                                  "email": "proood@tbank.ru",
                              }
                          }
                      }
                  },

                  401: {
                      "description": "Invalid token",
                      "content": {
                          "application/json": {
                              "example": {"detail": "Невалидный токен"}
                          }
                      },
                  },
                  404: {
                      "description": "Profile not found",
                      "content": {
                          "application/json": {
                              "example": {"detail": "При изменении данных профиля произошла ошибка. Попробуйте позже"}
                          }
                      },
                  },
              }
              )
async def update_partner_profile(data: PartnerDataUpdate, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).update_partner_profile(data, partner_id)


@router.post("/create-loyalty",
             summary="Создание программы лояльности",
             description="Создание программы лояльности",
             response_model=CreateLoyalty,
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {
                                 "title": "Роман Калмыков",
                                 "target_usages": 0,
                             }
                         }
                     }
                 },

                 401: {
                     "description": "Invalid token",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Невалидный токен"}
                         }
                     },
                 },
                 400: {
                     "description": "Bad request",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Не удалось создать программу лояльности. Повторите позже"}
                         }
                     },
                 },
             }
             )
async def create_loyalty(data: CreateLoyalty, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).create_loyalty(data.dict(), partner_id)


@router.get("/loyalty",
            summary="Получение акций с пагинацией",
            description="Получение акций рекламных ",
            response_model=List[CreateLoyalty],
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "title": "Выиграй PROD и погуляй с гитом",
                                    "target_usages": 11

                                }
                            ]
                        }
                    }
                },

                404: {
                    "description": "Invalid token",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Программа лояльности не найдена"}
                        }
                    },
                },

                400: {
                    "description": "Bad request",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Не удалось создать программу лояльности. Повторите позже"}
                        }
                    },
                },
            }

            )
async def get_loyalty(limit: int = 5, offset: int = 0, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).get_loyalty(partner_id, limit, offset)


@router.get("/scan/{client_id}",
            summary="Список актуальных акций",
            description="Возвращает список актуальных акций для данного партнёра",
            response_model=List[LoyaltyForClient],
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "items": [
                                {
                                    "loyalty_id": "9637f13d-f800-4d1b-8564-70fec766cef7",
                                    "title": "Выиграй PROD и погуляй с гитом",
                                    "target_usages": 11,
                                    "n_count": 0
                                }
                            ]
                            }
                        }
                    }
                },

                404: {
                    "description": "Partner or client not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Данного партнёра или клиента не существует"}
                        }
                    },
                },

            }
            )
async def scan_loyalty(client_id: UUID, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).scan_loyalty(partner_id, client_id)


@router.post("/scan/{client_id}/{loyalty_id}/plus-one",
             summary="Количество приобретений",
             description="Ведёт статистику приобретения товара",
             response_model=Status,
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {"status": "ok"}
                         }
                     }
                 },
                 403: {
                     "description": "Havent permissions",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Недостаточно прав для совершения данного действия"}
                         }
                     }
                 },

                 404: {
                     "description": "Partner or client not found",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Данного партнёра или клиента не существует"}
                         }
                     }
                 }})
async def scan_loyalty_plus_one(client_id: UUID, loyalty_id: UUID, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).scan_loyalty_plus_one(partner_id, client_id, loyalty_id)


@router.post("/scan/{client_id}/{loyalty_id}/give",
             summary="Количество бесплатных подарков",
             description="Ведёт статистику получения бесплатного товара",
             response_model=Status,
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {"status": "ok"}
                         }
                     }
                 },
                 403: {
                     "description": "Havent permissions",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Недостаточно прав для совершения данного действия"}
                         }
                     }
                 },

                 404: {
                     "description": "Partner or client not found",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Данного партнёра или клиента не существует"}
                         }
                     }
                 }})
async def scan_loyalty_give(client_id: UUID, loyalty_id: UUID, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    return PartnerService(db=get_session()).scan_loyalty_give(partner_id, client_id, loyalty_id)


@router.post("/image", status_code=201,
             summary="Загрузка изображений",
             description="Добавляет функционал загрузки изображений профиля для партнёров",
             responses={
                 201: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {"message": "Изображение загружено"}
                         }
                     }
                 },
                 400: {
                     "description": "Invalid image format",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Неверный формат изображения. Возможен только PNG"}
                         }
                     }
                 }, }
             )
async def upload_image(file: UploadFileValid, token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    """Загружает изображение в S3."""
    file = base64.b64decode(file.file.split(",")[1])
    file = BytesIO(file)
    try:
        result = await S3Service().upload_image_service(file, str(partner_id))
        return {"message": "Изображение загружено."}  # Возвращаем результат из s3_service
    except HTTPException as e:
        raise e


@router.get("/image",
            summary="Получение изображений",
            description="Добавляет функционал получения изображений профиля для партнёров",
            responses={
                200: {
                    "description": "Successful Response",
                },
                404: {
                    "description": "Image not found",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Изображение не найдено"}
                        }
                    }
                }, }
            )
async def get_image(partner_id: str):
    """Получает изображение из S3."""
    try:
        image_data = await S3Service().get_image_service(str(partner_id) + '.png')
        return StreamingResponse(content=image_data, media_type="image/png")  # Укажите правильный media_type
    except HTTPException as e:
        raise e


@router.delete("/image", status_code=204,
               summary="Удаление изображений",
               description="Удаляет изображение профиля партнёра и возвращает сообщение об этом",
               responses={
                   204: {
                       "description": "Successful Response",
                   },
                   404: {
                       "description": "Image not found",
                       "content": {
                           "application/json": {
                               "example": {
                                   "detail": "Изображение не найдено"}
                           }
                       }
                   },
                   422: {
                       "description": "Can not delete image",
                       "content": {
                           "application/json": {
                               "example": {
                                   "detail": "Не удвалось удалить изображение. Попробуйте позже"}
                           }
                       }
                   },
               }
               )
async def delete_image(token: str = Depends(oauth2_scheme)):
    partner_id = AuthService(db=get_session()).check_partner_token(token)
    """Удаляет изображение из S3."""
    try:
        result = await S3Service().delete_image_service(str(partner_id) + '.png')
        return # Возвращаем результат из s3_service
    except HTTPException as e:
        raise e
