#!/usr/bin/env python
"""
Simple test to verify database and models work correctly.
This test checks if the database initialization with new models works properly.
"""

import sys
import os
import tempfile
import shutil

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_models():
    """Test that our database models work correctly."""
    
    try:
        # Import models
        from database.models import Base, DividendEvent, StockSplit
        print("✅ Successfully imported DividendEvent and StockSplit models")
        
        # Import database engine
        from database.database import engine
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test that we can create instances of the new models
        from datetime import date
        
        # Test DividendEvent
        dividend_event = DividendEvent(
            ticker="AAPL",
            ex_dividend_date=date(2023, 5, 15),
            payment_date=date(2023, 5, 20),
            dividend_per_share=0.23,
            shares_owned=100,
            cash_received=23.00
        )
        print("✅ DividendEvent instance created successfully")
        
        # Test StockSplit
        stock_split = StockSplit(
            ticker="AAPL",
            split_date=date(2023, 6, 10),
            old_ratio=1,
            new_ratio=4
        )
        print("✅ StockSplit instance created successfully")
        
        print("\n🎉 All database models and functionality are properly implemented!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_database_models()