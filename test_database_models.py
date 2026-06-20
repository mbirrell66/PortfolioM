#!/usr/bin/env python
"""
Test script to verify database initialization with new models
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import Base, DividendEvent, StockSplit
from database.database import engine

def test_database_setup():
    """Test that database can be initialized with new models"""
    print("Testing database initialization...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully with all tables including DividendEvent and StockSplit")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Tables in database: {table_names}")
    
    if 'dividend_events' in table_names and 'stock_splits' in table_names:
        print("✅ DividendEvent and StockSplit tables created successfully")
        return True
    else:
        print("❌ Missing tables")
        return False

if __name__ == "__main__":
    test_database_setup()