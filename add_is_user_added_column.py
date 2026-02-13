#!/usr/bin/env python3
"""
Add the missing is_user_added column to the grant_sites table in NeonDB.
This script will safely add the column if it doesn't exist.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Load environment variables
load_dotenv()

def add_is_user_added_column():
    """Add is_user_added column to grant_sites table if it doesn't exist."""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables!")
        print("   Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print("=" * 60)
    print("Adding is_user_added column to grant_sites table")
    print("=" * 60)
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    try:
        # Check if column already exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('grant_sites')]
        
        if 'is_user_added' in columns:
            print("✅ Column 'is_user_added' already exists!")
            print("   No migration needed.")
            return
        
        print("⚠️  Column 'is_user_added' not found. Adding it now...")
        print()
        
        # Add the column
        with engine.connect() as conn:
            # For PostgreSQL/NeonDB
            if "postgresql" in DATABASE_URL or "neon" in DATABASE_URL.lower():
                # Add column with default value
                conn.execute(text("""
                    ALTER TABLE grant_sites 
                    ADD COLUMN IF NOT EXISTS is_user_added BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ Column 'is_user_added' added successfully!")
                
                # Update existing records to have is_user_added = FALSE
                conn.execute(text("""
                    UPDATE grant_sites 
                    SET is_user_added = FALSE 
                    WHERE is_user_added IS NULL
                """))
                conn.commit()
                print("✅ Updated existing records (set is_user_added = FALSE)")
                
            else:
                # For SQLite
                print("⚠️  SQLite detected. Migration for SQLite is more complex.")
                print("   Consider recreating the table or using Alembic for migrations.")
        
        # Verify the column was added
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('grant_sites')]
        
        if 'is_user_added' in columns:
            print()
            print("✅ Verification: Column 'is_user_added' now exists!")
            print()
            print("Current columns in grant_sites table:")
            for col in inspector.get_columns('grant_sites'):
                print(f"   - {col['name']} ({col['type']})")
        else:
            print("❌ Error: Column was not added successfully")
            sys.exit(1)
            
    except ProgrammingError as e:
        print(f"❌ Database error: {str(e)}")
        print()
        print("Trying alternative approach...")
        
        # Try with IF NOT EXISTS removed (some PostgreSQL versions don't support it)
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE grant_sites 
                    ADD COLUMN is_user_added BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ Column added using alternative method!")
        except Exception as e2:
            if "already exists" in str(e2).lower() or "duplicate" in str(e2).lower():
                print("✅ Column already exists (detected by error message)")
            else:
                print(f"❌ Failed: {str(e2)}")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print()
    print("You can now run:")
    print("  python3 export_json_to_db.py")

if __name__ == "__main__":
    try:
        add_is_user_added_column()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)

