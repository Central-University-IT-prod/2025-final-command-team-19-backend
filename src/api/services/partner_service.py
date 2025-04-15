from http.client import HTTPException

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.api.repos.partner_repository import PartnerRepository


class PartnerService:
    def __init__(self, db: Session):
        self.partner_repo = PartnerRepository(db)

    def get_partner_profile(self, partner_id):
        try:
            res = self.partner_repo.get_by_id(partner_id)
            res = res.__dict__
            del res['password_hash']
            del res['partner_id']
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="Профиль партнёра не найден. Повторите позже")

    def update_partner_profile(self, data, partner_id):
        try:
            res = self.partner_repo.update_partner(partner_id, data)
            res = res.__dict__
            del res['password_hash']
            del res['partner_id']
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="Не удалось создать программу лояльности. Повторите позже")


    def create_loyalty(self, data, partner_id):
        try:
            added_loyalty = self.partner_repo.add_loyalty(partner_id, data)
            added_loyalty = added_loyalty
            return added_loyalty
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="Не удалось создать программу лояльности. Повторите позже")

    def get_loyalty(self, partner_id, limit, offset):
        try:
            res = self.partner_repo.get_loyalty_with_pagination(partner_id, limit, offset)
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="При получении данных произошла ошибка. Попробуйте позже")


    def scan_loyalty(self, partner_id, client_id):
        try:
            res = self.partner_repo.scan_loyalty(partner_id, client_id)
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="При получении данных произошла ошибка. Попробуйте позже")

    def scan_loyalty_plus_one(self, partner_id, client_id, loyalty_id):
        try:
            res = self.partner_repo.scan_loyalty_plus_one(partner_id, client_id, loyalty_id)
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="При получении данных произошла ошибка. Попробуйте позже")


    def scan_loyalty_give(self, partner_id, client_id, loyalty_id):
        try:
            res = self.partner_repo.scan_loyalty_give(partner_id, client_id, loyalty_id)
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400,
                                detail="При получении данных произошла ошибка. Попробуйте позже")
