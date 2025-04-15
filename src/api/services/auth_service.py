from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from src.api.services.db_service import *
import uuid
import jwt
import datetime

SECRET_KEY = "PROD_command_2025"
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


    def generate_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }

        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


    def decode_token(self, token):
        return jwt.decode(token, SECRET_KEY, algorithms="HS256")


    def check_client_token(self, token):
        try:
            if token:
                token_data = self.decode_token(token)
                exp = token_data['exp']
                user_id = token_data['user_id']

                if int(datetime.datetime.utcnow().timestamp()) < exp:
                    if self.db.query(Client).filter(Client.client_id == user_id).first():
                        return user_id
            raise HTTPException(status_code=401, detail="Некорректный токен")
        except Exception:
            raise HTTPException(status_code=401, detail="Некорректный токен")


    def check_partner_token(self, token):
        try:
            if token:
                token_data = self.decode_token(token)
                exp = token_data['exp']
                user_id = token_data['user_id']

                if int(datetime.datetime.utcnow().timestamp()) < exp:
                    if self.db.query(Partner).filter(Partner.partner_id == user_id).first():
                        return user_id
            raise HTTPException(status_code=401, detail="Некорректный токен")
        except Exception:
            raise HTTPException(status_code=401, detail="Некорректный токен")


    def registration_user(self, data):
        existing_user = self.db.query(Client).filter(Client.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail='Эта почта уже зарегистрирована')
        client = Client()
        client.client_id = uuid.uuid4()
        client.name = data.name
        client.email = data.email
        client.password_hash = self.hash_password(data.password)
        client.gender = data.gender
        client.date_birthday = data.date_birthday
        self.db.add(client)
        self.db.commit()

        token = self.generate_token(str(client.client_id))
        for i in ["06efe0b2-394e-4a7e-afad-f5499f9542f3", "8eb923a2-44b3-4439-a6a4-c89d9781dd87", "1ce1c37a-7c74-4ce1-ab37-1230cd874d12", "18c44de5-f201-49c3-8dc2-ba005978b0ac", "448d7244-3257-4b55-b957-f78f6d81fae4", "d352d436-0951-4439-9d4f-87495dd01c79"]:
            self.db.add(ClientAchievementsUsage(achievements_id=i, client_id=client.client_id, n_count=0))

        return {"token": token}


    def authorization_user(self, email, password):
        existing_user = self.db.query(Client).filter(Client.email == email).first()
        if existing_user:
            if self.verify_password(password, str(existing_user.password_hash)):
                token = self.generate_token(str(existing_user.client_id))
                return {"token": token}
            else:
                raise HTTPException(status_code=401, detail='Неверный email или пароль')
        else:
            raise HTTPException(status_code=401, detail='Неверный email или пароль')


    def registration_partner(self, data):
        existing_user = self.db.query(Partner).filter(Partner.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail='Эта почта уже зарегистрирована')
        partner = Partner()
        partner.partner_id = uuid.uuid4()
        partner.name = data.name
        partner.email = data.email
        partner.password_hash = self.hash_password(data.password)
        self.db.add(partner)
        self.db.commit()

        token = self.generate_token(str(partner.partner_id))

        return {"token": token}


    def authorization_partner(self, email, password):
        existing_partner = self.db.query(Partner).filter(Partner.email == email).first()
        if existing_partner:
            if self.verify_password(password, str(existing_partner.password_hash)):
                token = self.generate_token(str(existing_partner.partner_id))
                return {"token": token}
            else:
                raise HTTPException(status_code=401, detail='Некорректная почта или пароль')
        else:
            raise HTTPException(status_code=401, detail='Некорректная почта или пароль')

    def get_role(self, token):
        try:
            user_id = self.check_client_token(token)
            return {"role": "CLIENT", "user_id": user_id}
        except HTTPException:
            try:
                user_id = self.check_partner_token(token)
                return {"role": "PARTNER", "user_id": user_id}
            except HTTPException:
                raise HTTPException(status_code=401, detail='Некорректный токен')