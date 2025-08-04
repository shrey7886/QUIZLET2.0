#!/usr/bin/env python3
"""
Database initialization script for Quizlet AI
"""

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import *  # Import all models

def init_db():
    """Initialize the database by creating all tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("📊 Tables created:")
        
        # List all tables
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            for table in tables:
                print(f"   - {table[0]}")
                
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db() 