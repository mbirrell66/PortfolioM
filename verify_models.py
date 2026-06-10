import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing the models
try:
    from database.models import DividendEvent, StockSplit
    print("✅ DividendEvent and StockSplit models imported successfully")
    
    # Test creating database tables
    from database.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Tables in database: {table_names}")
    
    if 'dividend_events' in table_names and 'stock_splits' in table_names:
        print("✅ DividendEvent and StockSplit tables created successfully")
    else:
        print("❌ Missing tables")
        
except Exception as e:
    print(f"❌ Error: {e}")