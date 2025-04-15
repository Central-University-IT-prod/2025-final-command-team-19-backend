from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.api.repos.client_repository import ClientRepository


class ClientService:
    def __init__(self, db: Session):
        self.client_repo = ClientRepository(db)

    def get_client_profile(self, client_id):
        try:
            res = self.client_repo.get_by_id(client_id)
            res = res.__dict__
            del res['password_hash']
            del res['client_id']
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=404, detail="При получениии профиля произошла ошибка. Попробуйте позже")

    def update_client_profile(self, data, client_id):
        try:
            res = self.client_repo.update_client(client_id, data)
            res =  res.__dict__
            del res['password_hash']
            del res['client_id']
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=404, detail="При обновлении профиля произошла ошибка. Попробуйте позже")

    def get_client_loyalty(self, client_id):
        res = self.client_repo.get_loyalty(client_id)
        return res

    def get_client_achievements(self, client_id):
        res = self.client_repo.get_achievements(client_id)
        return res
