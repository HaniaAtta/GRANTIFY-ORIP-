# models/db_helper.py
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

# === CRUD Functions ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_or_update_grant(url, status):
    db = SessionLocal()
    now = datetime.utcnow()
    grant = db.query(Grant).filter(Grant.url == url).first()
    if grant:
        grant.status = status
        grant.last_updated = now
    else:
        grant = Grant(url=url, status=status, last_updated=now)
        db.add(grant)
    db.commit()
    db.close()

def get_grants():
    db = SessionLocal()
    grants = db.query(Grant).order_by(Grant.id.asc()).all()
    db.close()
    return grants

def delete_grant_by_id(grant_id):
    db = SessionLocal()
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if grant:
        db.delete(grant)
        db.commit()
    db.close()
def url_exists(url: str):
    db = SessionLocal()
    exists = db.query(Grant).filter(Grant.url == url).first() is not None
    db.close()
    return exists
