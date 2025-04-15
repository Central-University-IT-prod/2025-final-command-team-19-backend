from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import update, and_
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from src.api.services.db_service import Partner, Loyalty, Client, ClientLoyaltyUsage, PartnerStatGeneral, PartnerStat, ClientAchievementsUsage, Achievements
import uuid

from src.api.schemas.partner_schemas import PartnerDataUpdate


class PartnerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, partner_id):
        partner = self.db.query(Partner).filter(Partner.partner_id == str(partner_id)).first()
        if partner:
            return partner
        else:
            raise HTTPException(status_code=404, detail="Партнёр не найден")

    def update_partner(self, partner_id, data: PartnerDataUpdate):
        existing_partner = self.get_by_id(partner_id)
        if existing_partner:
            stmt = update(Partner).where(Partner.partner_id == str(partner_id)).values(**data.dict())
            self.db.execute(stmt)
            self.db.commit()
            return self.db.refresh(existing_partner).__dict__
        else:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра не существует"})



    def add_loyalty(self, partner_id, data):
        existing_partner = self.get_by_id(partner_id)
        if existing_partner:
            loyalty = Loyalty(
                loyalty_id=uuid.uuid4(),
                partner_id=partner_id,
                title=data["title"],
                target_usages=data["target_usages"])
            self.db.add(loyalty)
            self.db.commit()
            self.db.refresh(loyalty)
            loyalty = loyalty.__dict__
            del loyalty["loyalty_id"]
            del loyalty["partner_id"]
            return loyalty

        else:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра не существует"})




    def get_loyalty_with_pagination(self, partner_id, limit, offset):
        existing_partner = self.get_by_id(partner_id)
        if existing_partner:
            data = self.db.query(Loyalty).filter(Loyalty.partner_id == str(partner_id))
            total_count = data.count()
            try:
                result = [{"loyalty_id": str(i.loyalty_id), "title": i.title, "target_usages": i.target_usages} for i in
                          data.limit(limit).offset(offset).all()]
            except:
                raise HTTPException(status_code=404,
                                detail={"message": "Программа лояльности не найдена"})
        else:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра не существует"})
        return JSONResponse(content=result, headers={'x-total-count': str(total_count)})

    def get_client_by_id(self, client_id):
        return self.db.query(Client).filter(Client.client_id == str(client_id)).first()

    def get_client_loyalty(self, partner_id):
        return self.db.query(Loyalty).filter(Loyalty.partner_id == str(partner_id)).all()

    def get_client_loyalty_by_loyalty(self, loyalty_id):
        return self.db.query(Loyalty).filter(Loyalty.loyalty_id == str(loyalty_id)).first()

    def get_client_loyalty_usage(self, loyalty, client_id):
        return self.db.query(ClientLoyaltyUsage).filter(and_(ClientLoyaltyUsage.loyalty_id == loyalty.loyalty_id,
                                                             ClientLoyaltyUsage.client_id == client_id)).first()

    def scan_loyalty(self, partner_id, client_id):
        existing_partner = self.get_by_id(partner_id)
        existing_client = self.get_client_by_id(client_id)
        if not existing_partner or not existing_client:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра или клиента не существует"})
        else:
            loyalty = self.get_client_loyalty(partner_id)
            res = []
            for i in loyalty:
                client_loyalty = self.get_client_loyalty_usage(i, client_id)
                if client_loyalty:
                    res.append({"loyalty_id": str(i.loyalty_id), "title": i.title, "target_usages": i.target_usages, "n_count": client_loyalty.n_count})
                else:
                    res.append({"loyalty_id": str(i.loyalty_id), "title": i.title, "target_usages": i.target_usages, "n_count": 0})
            return res

    def scan_loyalty_plus_one(self, partner_id, client_id, loyalty_id):
        existing_partner = self.get_by_id(partner_id)
        existing_client = self.get_client_by_id(client_id)
        loyalty = self.get_client_loyalty_by_loyalty(loyalty_id
                                                     )
        if not existing_partner or not existing_client:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра или клиента не существует"})
        if not loyalty:
            raise HTTPException(status_code=404,
                                detail={"message": "Программа лояльности не найдена"})
        existing_client_loyalty_usage = self.db.query(ClientLoyaltyUsage).filter(
            and_(ClientLoyaltyUsage.loyalty_id == loyalty_id, ClientLoyaltyUsage.client_id == client_id)).first()
        if not existing_client_loyalty_usage:
            client_loyalty_usage = ClientLoyaltyUsage(loyalty_id=loyalty_id, client_id=client_id, n_count=1)
            self.db.add(client_loyalty_usage)
            partner_stat_general = PartnerStatGeneral(partner_id=partner_id, client_id=client_id, loyalty_id=loyalty_id,
                                                      start_loyalty=1, finish_loyalty=0, return_loyalty=0)
            self.db.add(partner_stat_general)
            self.db.commit()
        elif existing_client_loyalty_usage.n_count == loyalty.target_usages:
             raise HTTPException(status_code=422,
                                detail={"Недостаточно прав для совершения данного действия"})
        elif existing_client_loyalty_usage.n_count == 0:
            existing_partner_stat_general = self.db.query(PartnerStatGeneral).filter(
                and_(PartnerStatGeneral.partner_id == partner_id, PartnerStatGeneral.loyalty_id == loyalty_id,
                     PartnerStatGeneral.client_id == client_id)).first()
            existing_partner_stat_general.return_loyalty = 1
            existing_client_loyalty_usage.n_count += 1
            partner_stat = PartnerStat(partner_id=partner_id, loyalty_id=loyalty_id, date_time=datetime.now(),
                                       plus_one=1,
                                       give=0)
            self.db.add(partner_stat)
            self.db.commit()
        else:
            existing_client_loyalty_usage.n_count += 1
            partner_stat = PartnerStat(partner_id=partner_id, loyalty_id=loyalty_id, date_time=datetime.now(),
                                       plus_one=1, give=0)
            self.db.add(partner_stat)
            self.db.commit()
        for i in ["06efe0b2-394e-4a7e-afad-f5499f9542f3", "8eb923a2-44b3-4439-a6a4-c89d9781dd87", "1ce1c37a-7c74-4ce1-ab37-1230cd874d12"]:
            achiv = self.db.query(ClientAchievementsUsage).filter(and_(ClientAchievementsUsage.achievements_id == i, ClientAchievementsUsage.client_id == client_id)).first()
            if not achiv:
                self.db.add(ClientAchievementsUsage(achievements_id=i, client_id=client_id, n_count=1))
            else:
                if achiv.n_count != self.db.query(Achievements).filter(Achievements.achievements_id == i).first().target_usages:
                    achiv.n_count += 1
        self.db.commit()
        return {"status": "ok"}

    def scan_loyalty_give(self, partner_id, client_id, loyalty_id):
        existing_partner = self.get_by_id(partner_id)
        existing_client = self.get_client_by_id(client_id)
        existing_loyalty = self.get_client_loyalty_by_loyalty(loyalty_id)
        if not existing_partner or not existing_client:
            raise HTTPException(status_code=404,
                                detail={"message": "Данного партнёра или клиента не существует"})
        if not existing_loyalty:
            raise HTTPException(status_code=404,
                                detail={"message": "Программа лояльности не найдена"})
        existing_client_loyalty_usage = self.db.query(ClientLoyaltyUsage).filter(
            and_(ClientLoyaltyUsage.loyalty_id == loyalty_id, ClientLoyaltyUsage.client_id == client_id)).first()
        if existing_client_loyalty_usage.n_count == existing_loyalty.target_usages:
            existing_client_loyalty_usage.n_count = 0
            existing_partner_stat_general = self.db.query(PartnerStatGeneral).filter(
                and_(PartnerStatGeneral.partner_id == partner_id, PartnerStatGeneral.loyalty_id == loyalty_id,
                     PartnerStatGeneral.client_id == client_id)).first()
            existing_partner_stat_general.finish_loyalty = 1
            partner_stat = PartnerStat(partner_id=partner_id, loyalty_id=loyalty_id, date_time=datetime.now(),
                                       plus_one=0, give=1)
            self.db.add(partner_stat)
            for i in ["18c44de5-f201-49c3-8dc2-ba005978b0ac", "448d7244-3257-4b55-b957-f78f6d81fae4",
                      "d352d436-0951-4439-9d4f-87495dd01c79"]:
                achiv = self.db.query(ClientAchievementsUsage).filter(and_(ClientAchievementsUsage.achievements_id == i,
                                                                           ClientAchievementsUsage.client_id == client_id)).first()
                if not achiv:
                    self.db.add(ClientAchievementsUsage(achievements_id=i, client_id=client_id, n_count=1))
                else:
                    if achiv.n_count != self.db.query(Achievements).filter(
                            Achievements.achievements_id == i).first().target_usages:
                        achiv.n_count += 1
            self.db.commit()
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=422,
                                detail={"message": "Недостаточно покупок для совершения данного действия"})





