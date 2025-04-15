from enum import Enum
from typing import List

from pydantic import BaseModel, EmailStr
from datetime import date

from src.api.schemas.partner_schemas import LoyaltyForClient

class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'

class ClientDataRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str
    date_birthday: date
    gender: Gender

    class Config:
        use_enum_values = True

class ClientDataAuthorization(BaseModel):
    email: EmailStr
    password: str


class ClientDataUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None

# class ClientDataQR(BaseModel):
#     client_id: UUID

class ClientDataProfile(BaseModel):
    name: str
    email: EmailStr
    date_birthday: date
    gender: Gender

class ClientDataEditProfile(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    date_birthday: date | None = None
    gender: Gender | None = None

class OneClientLoyalty(BaseModel):
    name: str
    partner_id: str
    loyalties: List[LoyaltyForClient]

class ReturnAchievement(BaseModel):
    title: str
    target_usages: int
    n_count: int
