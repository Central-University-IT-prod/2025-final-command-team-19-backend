from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from src.api.schemas.client_schemas import *
from src.api.services.client_service import ClientService
from src.api.services.auth_service import AuthService
from src.api.schemas.default_schemas import *
from src.api.services.db_service import get_session

router = APIRouter(prefix="/client", tags=["client"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/auth/sign-up",
             summary="Регистрация клиента",
             description="Регистрация пользователя",
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
             }
             )
async def create_user(data: ClientDataRegistration):
    return AuthService(db=get_session()).registration_user(data)


@router.post("/auth/sign-in",
             summary="Авторизаци клиента",
             description="Авторизация пользователя в системе. При успешном вызове возвращает JWT токен.",
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
             }
             )
async def authorization_user(data: ClientDataAuthorization):
    return AuthService(db=get_session()).authorization_user(data.email, data.password)


@router.get("/qr",
            summary="Создание qr-кода для использования акций",
            description="Возвращает данные, необходимые для создания qr-кода покупателя",
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "a6a9b22a-92ed-461e-a576-8cc87cccd4ca"
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
            }
            )
async def generate_qr(token: str = Depends(oauth2_scheme)):
    return AuthService(db=get_session()).check_client_token(token)


@router.get("/profile",
            summary="Профиль клиента",
            description="Получение данных профиля клиента",
            response_model=ClientDataProfile,
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "name": "Евгений Шмат",
                                "email": "proood@tbank.ru",
                                "date_birthday": "20.01.2021",
                                "gender": "MALE"

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
            }
            )
async def get_client_profile(token: str = Depends(oauth2_scheme)):
    client_id = AuthService(db=get_session()).check_client_token(token)
    return ClientService(db=get_session()).get_client_profile(client_id)


@router.patch("/profile",
              summary="Редактирование профиля клиента",
              description="Изменение данных, хранящихся в профиле клиента",
              response_model=ClientDataEditProfile,
              responses={
                  200: {
                      "description": "Successful Response",
                      "content": {
                          "application/json": {
                              "example": {
                                  "name": "Евгений Шмат",
                                  "email": "proood@tbank.ru",
                                  "date_birthday": "20.01.2021",
                                  "gender": "MALE"

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
              }
              )
async def update_client_profile(data: ClientDataUpdate, token: str = Depends(oauth2_scheme)):
    client_id = AuthService(db=get_session()).check_client_token(token)
    return ClientService(db=get_session()).update_client_profile(data, client_id)


@router.get("/loyalty",
            summary="Получение акций в которых участвует клиент",
            description="Получение акций в которых участвует клиент",
            response_model=List[OneClientLoyalty],
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": [{
                                "name": "TBank",
                                "partner_id": "a6a9b22a-92ed-461e-a576-8cc87cccd4ca",
                                "loyalties": [
                                    {
                                        "loyalti_id": "a6a9b22a-92ed-461e-a576-8cc87cccd4ca",
                                        "title": "При получении двух кредитных карт, кофе-брейк в подарок",
                                        "target_usages": 5,
                                        "n_count": 3
                                    }

                                ]

                            }]
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
                    "description": "Loyalty not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Вы не участвуете, не в одной программе лояльности"}
                        }
                    },
                },
            }
            )
async def get_client_loyalty(token: str = Depends(oauth2_scheme)):
    client_id = AuthService(db=get_session()).check_client_token(token)
    return ClientService(db=get_session()).get_client_loyalty(client_id)

@router.get("/achievements",
         summary="Получение достижений клиентов",
         description="Изменение данных, хранящихся в профиле клиента",
         response_model=List[ReturnAchievement],
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "title": "Активируйте программы лояльности у 3 разных компаний",
                                 "target_usages": 3,
                                 "n_count": 1
                             }
                         ]
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
                 "description": "Loyalty not found",
                 "content": {
                     "application/json": {
                     }
                 },
             },
         }
         )
async def get_client_achievements(token: str = Depends(oauth2_scheme)):
    client_id = AuthService(db=get_session()).check_client_token(token)
    return ClientService(db=get_session()).get_client_achievements(client_id)