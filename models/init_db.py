# models/init_db.py
from models.db_helper import Base, engine
from sqlalchemy import inspect, text

def create_tables():
    """Create all tables and add missing columns if needed."""
    Base.metadata.create_all(bind=engine)
    print("[INFO] Tables created/verified in Neon DB.")
    
    # Check and add is_user_added column if it doesn't exist
    inspector = inspect(engine)
    if 'grant_sites' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('grant_sites')]
        if 'is_user_added' not in columns:
            print("[INFO] Adding missing column: is_user_added")
            try:
                with engine.connect() as conn:
                    conn.execute(text("""
                        ALTER TABLE grant_sites 
                        ADD COLUMN IF NOT EXISTS is_user_added BOOLEAN DEFAULT FALSE
                    """))
                    conn.commit()
                    print("[INFO] Column 'is_user_added' added successfully!")
            except Exception as e:
                # Try without IF NOT EXISTS for older PostgreSQL
                try:
                    with engine.connect() as conn:
                        conn.execute(text("""
                            ALTER TABLE grant_sites 
                            ADD COLUMN is_user_added BOOLEAN DEFAULT FALSE
                        """))
                        conn.commit()
                        print("[INFO] Column 'is_user_added' added successfully!")
                except Exception as e2:
                    if "already exists" not in str(e2).lower():
                        print(f"[WARNING] Could not add column: {e2}")
        else:
            print("[INFO] Column 'is_user_added' already exists.")

if __name__ == "__main__":
    create_tables()
