from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi import HTTPException
from src.api.services.db_service import Loyalty, ClientLoyaltyUsage, Partner, Achievements, ClientAchievementsUsage, Client


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id):
        return self.db.query(Client).filter(Client.client_id == str(client_id)).first()

    def update_client(self, client_id, data):
        existing_client = self.get_by_id(client_id)
        if existing_client:
            stmt = update(Client).where(Client.client_id == str(client_id)).values(**data.dict())
            self.db.execute(stmt)
            self.db.commit()
            self.db.refresh(existing_client)
        else:
            raise HTTPException(status_code=404,
                                detail={"message": "Такого клиента не существует"})
        return existing_client

    def get_loyalty(self, client_id):
        data = self.db.query(
            Partner.name,
            Loyalty.title,
            Loyalty.target_usages,
            ClientLoyaltyUsage.n_count,
            ClientLoyaltyUsage.loyalty_id,
            Partner.partner_id
        ).join(Loyalty, Loyalty.partner_id == Partner.partner_id) \
            .join(ClientLoyaltyUsage, ClientLoyaltyUsage.loyalty_id == Loyalty.loyalty_id) \
            .filter(ClientLoyaltyUsage.client_id == client_id).all()
        result = []
        if data:
            for name, title, target_usages, n_count, loyalty_id, partner_id in data:
                partner_entry = next((item for item in result if item["name"] == name), None)
                if partner_entry:
                    partner_entry["loyalties"].append({
                        "loyalty_id": str(loyalty_id),
                        "title": title,
                        "target_usages": target_usages,
                        "n_count": n_count
                    })
                else:
                    result.append({
                        "name": name,
                        "partner_id": str(partner_id),
                        "loyalties": [{
                            "loyalty_id": str(loyalty_id),
                            "title": title,
                            "target_usages": target_usages,
                            "n_count": n_count
                        }]
                    })
            return result
        else:
            raise HTTPException(status_code=404,
                                detail="Программа лояльности не найдена")

    def get_achievements(self, client_id):
        data = self.db.query(
            Achievements.title,
            Achievements.target_usages,
            ClientAchievementsUsage.n_count
        ).select_from(Achievements) \
            .join(ClientAchievementsUsage, ClientAchievementsUsage.achievements_id == Achievements.achievements_id) \
            .filter(ClientAchievementsUsage.client_id == client_id).all()
        result = []
        if data:
            for title, target_usages, n_count in data:
                result.append({"title": title, "target_usages": target_usages, "n_count": n_count})
            return result
        else:
            raise HTTPException(status_code=404,
                                detail="Достижения не найдены")