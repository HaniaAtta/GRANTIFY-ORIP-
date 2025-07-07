from models.db_helper import SessionLocal
from sqlalchemy import text

def reset_grants_only():
    db = SessionLocal()

    try:
        db.execute(text("TRUNCATE TABLE grants RESTART IDENTITY CASCADE;"))
        print("[✅] grants table truncated and ID reset to 1.")
    except Exception as e:
        print("[⚠️] Failed to truncate grants table:", e)

    db.commit()
    db.close()

if __name__ == "__main__":
    reset_grants_only()
