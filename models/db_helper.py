# from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime
# from dotenv import load_dotenv
# import os

# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()

# class Grant(Base):
#     __tablename__ = "grants"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(String, unique=True, nullable=False)   # root domain
#     landing_page = Column(String, nullable=True)        # discovered grants page
#     status = Column(String, nullable=False)
#     categories = Column(JSON, nullable=True)            # JSON array
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     last_updated = Column(DateTime, default=datetime.utcnow)

# # === CRUD Functions ===

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def add_or_update_grant(url, status, landing_page=None, categories=None):
#     db = SessionLocal()
#     now = datetime.utcnow()
#     grant = db.query(Grant).filter(Grant.url == url).first()
#     if grant:
#         grant.status = status
#         grant.landing_page = landing_page or grant.landing_page
#         grant.categories = categories or grant.categories
#         grant.last_updated = now
#     else:
#         grant = Grant(
#             url=url,
#             landing_page=landing_page,
#             status=status,
#             categories=categories,
#             last_updated=now
#         )
#         db.add(grant)
#     db.commit()
#     db.close()

# def get_grants():
#     db = SessionLocal()
#     grants = db.query(Grant).order_by(Grant.id.asc()).all()
#     db.close()
#     return grants

# def delete_grant_by_id(grant_id):
#     db = SessionLocal()
#     grant = db.query(Grant).filter(Grant.id == grant_id).first()
#     if grant:
#         db.delete(grant)
#         db.commit()
#     db.close()

# def url_exists(url: str):
#     db = SessionLocal()
#     exists = db.query(Grant).filter(Grant.url == url).first() is not None
#     db.close()
#     return exists




# from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime
# from dotenv import load_dotenv
# import os

# # === Load environment variables ===
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

# # === Database setup ===
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()


# # === New Grant Model (separate table) ===
# class GrantSite(Base):
#     __tablename__ = "grant_sites"   # new table name

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(String, unique=True, nullable=False)   # root domain
#     landing_page = Column(String, nullable=True)        # discovered grants page
#     status = Column(String, nullable=False)             # open / closed / error
#     categories = Column(JSON, nullable=True)            # JSON array
#     timestamp = Column(DateTime, default=datetime.utcnow)  # created at
#     last_updated = Column(DateTime, default=datetime.utcnow)  # updated at


# # === CRUD Functions ===

# def get_db():
#     """Yield a database session (FastAPI dependency style)."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def add_or_update_grant_site(url, status, landing_page=None, categories=None):
#     """Insert or update a grant site record."""
#     now = datetime.utcnow()
#     with SessionLocal() as db:
#         grant = db.query(GrantSite).filter(GrantSite.url == url).first()
#         if grant:
#             # Update existing record
#             grant.status = status
#             grant.landing_page = landing_page or grant.landing_page
#             grant.categories = categories or grant.categories
#             grant.last_updated = now
#         else:
#             # Create new record
#             grant = GrantSite(
#                 url=url,
#                 landing_page=landing_page,
#                 status=status,
#                 categories=categories,
#                 timestamp=now,
#                 last_updated=now
#             )
#             db.add(grant)

#         db.commit()
#         db.refresh(grant)  # refresh with DB values
#         return grant


# def get_grant_sites():
#     """Get all grant site records ordered by ID."""
#     with SessionLocal() as db:
#         return db.query(GrantSite).order_by(GrantSite.id.asc()).all()


# def delete_grant_site_by_id(grant_id):
#     """Delete a grant site record by its ID."""
#     with SessionLocal() as db:
#         grant = db.query(GrantSite).filter(GrantSite.id == grant_id).first()
#         if grant:
#             db.delete(grant)
#             db.commit()
#             return True
#         return False


# def url_exists_in_grant_sites(url: str) -> bool:
#     """Check if a grant site URL already exists in DB."""
#     with SessionLocal() as db:
#         return db.query(GrantSite).filter(GrantSite.url == url).first() is not None














# from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine, Text
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime
# from dotenv import load_dotenv
# import os

# # === Load environment variables ===
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grants.db")  # fallback to sqlite

# # === Database setup ===
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()


# # === Grant Model ===
# class GrantSite(Base):
#     __tablename__ = "grant_sites"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(String, unique=True, nullable=False)   # base/root domain
#     landing_page = Column(String, nullable=True)        # discovered grants page
#     status = Column(String, nullable=False)             # open / closed / error
#     categories = Column(JSON, nullable=True)            # JSON array of categories
#     country = Column(String, nullable=True)             # optional, for filters
#     notes = Column(Text, nullable=True)                 # optional
#     timestamp = Column(DateTime, default=datetime.utcnow)   # created at
#     last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# # === CRUD Functions ===
# def get_db():
#     """Yield a database session (FastAPI dependency style)."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def add_or_update_grant_site(url, status, landing_page=None, categories=None, country=None, notes=None):
#     """Insert or update a grant site record."""
#     now = datetime.utcnow()
#     with SessionLocal() as db:
#         grant = db.query(GrantSite).filter(GrantSite.url == url).first()
#         if grant:
#             # Update existing record
#             grant.status = status
#             grant.landing_page = landing_page or grant.landing_page
#             grant.categories = categories or grant.categories
#             grant.country = country or grant.country
#             grant.notes = notes or grant.notes
#             grant.last_updated = now
#         else:
#             # Create new record
#             grant = GrantSite(
#                 url=url,
#                 landing_page=landing_page,
#                 status=status,
#                 categories=categories or [],
#                 country=country,
#                 notes=notes,
#                 timestamp=now,
#                 last_updated=now
#             )
#             db.add(grant)

#         db.commit()
#         db.refresh(grant)
#         return grant


# def get_grant_sites():
#     """Get all grant site records ordered by ID."""
#     with SessionLocal() as db:
#         return db.query(GrantSite).order_by(GrantSite.id.asc()).all()


# def delete_grant_site_by_id(grant_id):
#     """Delete a grant site record by its ID."""
#     with SessionLocal() as db:
#         grant = db.query(GrantSite).filter(GrantSite.id == grant_id).first()
#         if grant:
#             db.delete(grant)
#             db.commit()
#             return True
#         return False


# def url_exists_in_grant_sites(url: str) -> bool:
#     """Check if a grant site URL already exists in DB."""
#     with SessionLocal() as db:
#         return db.query(GrantSite).filter(GrantSite.url == url).first() is not None









from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# === Load environment variables ===
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grants.db")

# === Database setup ===
# Handle both PostgreSQL (NeonDB) and SQLite
if "postgresql" in DATABASE_URL or "neon" in DATABASE_URL.lower():
    # PostgreSQL/NeonDB connection
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
    from sqlalchemy.dialects.postgresql import JSONB
    JSON_TYPE = JSONB
else:
    # SQLite fallback
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False})
    JSON_TYPE = JSON

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# === Grant Model ===
class GrantSite(Base):
    __tablename__ = "grant_sites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    landing_page = Column(String)
    status = Column(String)
    categories = Column(JSON_TYPE, nullable=True)
    country = Column(String)
    notes = Column(Text)
    applicable_to_pakistan = Column(Integer, default=0)
    regions = Column(JSON_TYPE, nullable=True)
    thematic_areas = Column(JSON_TYPE, nullable=True)
    open_date = Column(DateTime, nullable=True)
    close_date = Column(DateTime, nullable=True)
    eligibility = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_count = Column(Integer, default=0)
    is_user_added = Column(Boolean, default=False)  # ✅ Flag to preserve user-added URLs

# === DB Session ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_or_update_grant_site(url, status, landing_page=None, categories=None, 
                            country=None, notes=None, applicable_to_pakistan=False,
                            regions=None, thematic_areas=None, open_date=None, 
                            close_date=None, eligibility=None, is_user_added=False, 
                            preserve_user_flag=True):
    """
    Insert or update a grant site record with all fields.
    
    Args:
        preserve_user_flag: If True, don't overwrite is_user_added flag for existing records
    """
    now = datetime.utcnow()
    
    # ✅ Cast boolean to integer here
    applicable_to_pakistan = int(applicable_to_pakistan)

    with SessionLocal() as db:
        grant = db.query(GrantSite).filter(GrantSite.url == url).first()
        
        if grant:
            # ✅ Preserve user-added flag if it was set by user
            if preserve_user_flag and grant.is_user_added:
                # Don't overwrite user-added grants, only update status and dates
                grant.status = status
                grant.last_updated = now
                if open_date:
                    grant.open_date = open_date
                if close_date:
                    grant.close_date = close_date
                if landing_page:
                    grant.landing_page = landing_page
                if status == "error":
                    grant.error_count += 1
                else:
                    grant.error_count = 0
            else:
                # Update all fields for auto-scraped grants
                grant.status = status
                grant.landing_page = landing_page or grant.landing_page
                grant.categories = categories or grant.categories
                grant.country = country or grant.country
                grant.notes = notes or grant.notes
                grant.applicable_to_pakistan = applicable_to_pakistan
                grant.regions = regions or grant.regions
                grant.thematic_areas = thematic_areas or grant.thematic_areas
                grant.open_date = open_date or grant.open_date
                grant.close_date = close_date or grant.close_date
                grant.eligibility = eligibility or grant.eligibility
                grant.last_updated = now
                grant.is_user_added = is_user_added  # Only set if explicitly provided
                
                if status == "error":
                    grant.error_count += 1
                else:
                    grant.error_count = 0
        else:
            grant = GrantSite(
                url=url,
                landing_page=landing_page,
                status=status,
                categories=categories or [],
                country=country,
                notes=notes,
                applicable_to_pakistan=applicable_to_pakistan,
                regions=regions or [],
                thematic_areas=thematic_areas or [],
                open_date=open_date,
                close_date=close_date,
                eligibility=eligibility,
                timestamp=now,
                last_updated=now,
                is_user_added=is_user_added
            )
            db.add(grant)

        db.commit()
        db.refresh(grant)
        return grant

def get_grant_sites():
    with SessionLocal() as db:
        return db.query(GrantSite).order_by(GrantSite.last_updated.desc()).all()

def get_grant_by_id(grant_id):
    with SessionLocal() as db:
        return db.query(GrantSite).filter(GrantSite.id == grant_id).first()

def get_grants_by_status(status):
    with SessionLocal() as db:
        return db.query(GrantSite).filter(GrantSite.status == status).all()

def get_grants_for_pakistan():
    with SessionLocal() as db:
        return db.query(GrantSite).filter(GrantSite.applicable_to_pakistan == 1).all()

def delete_grant_site_by_id(grant_id: int, db: Session):
    grant = db.query(GrantSite).filter(GrantSite.id == grant_id).first()
    if grant:
        db.delete(grant)
        db.commit()
        return True
    return False


def url_exists_in_grant_sites(url: str) -> bool:
    with SessionLocal() as db:
        return db.query(GrantSite).filter(GrantSite.url == url).first() is not None

def get_high_error_grants(threshold=3):
    with SessionLocal() as db:
        return db.query(GrantSite).filter(GrantSite.error_count >= threshold).all()