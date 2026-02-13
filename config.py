import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

#db config
DATABASE_URL = os.getenv("DATABASE_URL", 'postgresql://neondb_owner:npg_BeAk9D6rJsSu@ep-shy-block-a86ln8fv-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require')  # Default fallback to SQLite

# Handle both PostgreSQL and SQLite
if "postgresql" in DATABASE_URL or "neon" in DATABASE_URL.lower():
    # PostgreSQL/NeonDB connection
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
else:
    # SQLite fallback
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# celery config
BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery("grantly", broker=BROKER_URL, backend=RESULT_BACKEND)
# Add this line here:
celery_app.autodiscover_tasks(['tasks'])

# Main Celery Config
celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)

# celery beat
celery_app.conf.beat_schedule = {
    'scrape-every-6-hours': {
        'task': 'tasks.run_scrapers.run_all_scrapers',
        'schedule': crontab(hour='*/6'),
    },
}

