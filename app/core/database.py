"""
Database Configuration
Supports both SQLite (development) and Neon PostgreSQL (production/multitenant)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Check if we're using Neon (multitenant) or SQLite (development)
USE_NEON = os.getenv("NEON_DATABASE_URL") is not None

if USE_NEON:
    # Use Neon PostgreSQL for multitenant setup
    DATABASE_URL = os.getenv("NEON_DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("NEON_DATABASE_URL environment variable not set")
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
else:
    # Use SQLite for development
    DATABASE_URL = "sqlite:///./quizlet.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 