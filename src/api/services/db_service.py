from sqlalchemy import create_engine, Column, Integer, String, UUID, Date, DateTime
from sqlalchemy.orm import declarative_base, Session
import os

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'

    client_id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    date_birthday = Column(Date, nullable=False)
    gender = Column(String, nullable=False)

class Partner(Base):
    __tablename__ = 'partners'
    partner_id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

class Loyalty(Base):
    __tablename__ = 'loyalty'
    loyalty_id = Column(UUID, primary_key=True)
    partner_id = Column(UUID, nullable=False)
    title = Column(String, nullable=False)
    target_usages = Column(Integer, nullable=False)

class ClientLoyaltyUsage(Base):
    __tablename__ = 'client-loyalty-usages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(UUID, nullable=False)
    loyalty_id = Column(UUID, nullable=False)
    n_count = Column(Integer, nullable=False)

class PartnerStat(Base):
    __tablename__ = 'partner-stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partner_id = Column(UUID, nullable=False)
    loyalty_id = Column(UUID, nullable=False)
    date_time = Column(DateTime, nullable=False)
    plus_one = Column(Integer, nullable=False)
    give = Column(Integer, nullable=False)

class PartnerStatGeneral(Base):
    __tablename__ = 'partner-stats-general'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partner_id = Column(UUID, nullable=False)
    client_id = Column(UUID, nullable=False)
    loyalty_id = Column(UUID, nullable=False)
    start_loyalty = Column(Integer, nullable=False)
    finish_loyalty = Column(Integer, nullable=False)
    return_loyalty = Column(Integer, nullable=False)

class Achievements(Base):
    __tablename__ = 'achievements'
    achievements_id = Column(UUID, primary_key=True)
    title = Column(String, nullable=False)
    target_usages = Column(Integer, nullable=False)

class ClientAchievementsUsage(Base):
    __tablename__ = 'client-achievements-usages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(UUID, nullable=False)
    achievements_id = Column(UUID, nullable=False)
    n_count = Column(Integer, nullable=False)

engine = create_engine(os.environ['DATABASE_URL'])

session = Session(engine)

def create_table():
    Base.metadata.create_all(engine, tables=[Client.__table__])
    Base.metadata.create_all(engine, tables=[Partner.__table__])
    Base.metadata.create_all(engine, tables=[Loyalty.__table__])
    Base.metadata.create_all(engine, tables=[ClientLoyaltyUsage.__table__])
    Base.metadata.create_all(engine, tables=[PartnerStat.__table__])
    Base.metadata.create_all(engine, tables=[PartnerStatGeneral.__table__])
    Base.metadata.create_all(engine, tables=[Achievements.__table__])
    Base.metadata.create_all(engine, tables=[ClientAchievementsUsage.__table__])

def get_session():
    return session