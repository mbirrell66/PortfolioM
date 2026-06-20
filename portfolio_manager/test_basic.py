"""
Test script to verify basic functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from database.models import Position, PortfolioSnapshot
        from database.database import init_database
        from services.market_data import MarketDataService
        from services.portfolio_service import PortfolioService
        from gui.main_window import MainWindow
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_database():
    """Test database initialization."""
    try:
        from database.database import init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running basic functionality tests...")
    
    success = True
    success &= test_imports()
    success &= test_database()
    
    if success:
        print("\n🎉 All tests passed! Application structure is correct.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)