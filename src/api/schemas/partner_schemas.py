from typing import List, Optional

from pydantic import BaseModel, EmailStr

class PartnerDataRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str

class PartnerDataAuthorization(BaseModel):
    email: EmailStr
    password: str

class CreateLoyalty(BaseModel):
    title: str
    target_usages: int

class PartnerDataUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class GetProfile(BaseModel):
    name: str
    email: EmailStr

class PatchProfile(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

class LoyaltyForClient(BaseModel):
    loyalty_id: str
    title: str
    target_usages: int
    n_count: int

class UploadFileValid(BaseModel):
    file: str