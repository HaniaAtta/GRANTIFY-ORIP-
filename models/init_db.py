# models/init_db.py
from models.db_helper import Base, engine

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("[INFO] Tables created in Neon DB.")

if __name__ == "__main__":
    create_tables()
