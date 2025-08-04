"""
Neon Database Configuration
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Neon Database Configuration
NEON_DATABASE_URL = os.getenv(
    "NEON_DATABASE_URL",
    "postgresql://your-username:your-password@your-host/your-database"
)

# Create engine
engine = create_engine(
    NEON_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 