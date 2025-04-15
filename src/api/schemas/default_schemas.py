from pydantic import BaseModel
from enum import Enum

class Ping(BaseModel):
    status: str

class Auth(BaseModel):
    token: str

class RoleEnum(Enum):
    NONE = None
    CLIENT = 'CLIENT'
    PARTNER = 'PARTNER'

class Role(BaseModel):
    role: RoleEnum
    user_id: str | None = None

    class Config:
        use_enum_values = True

class Status(BaseModel):
    status: str
