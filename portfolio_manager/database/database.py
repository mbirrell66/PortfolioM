"""
Database initialization and connection for Portfolio Manager
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Get the data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "portfolio.db"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database by creating tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_database()