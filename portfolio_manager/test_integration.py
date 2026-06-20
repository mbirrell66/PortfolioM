"""
Simple test script to verify portfolio manager functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test import
try:
    from main import main
    print("Main module imports successfully")
    
    # Test database initialization
    from database.database import init_db
    init_db()
    print("Database initialized successfully")
    
    # Test portfolio service
    from services.portfolio_service import PortfolioService
    service = PortfolioService()
    print("Portfolio service created successfully")
    
    # Test analytics
    from services.portfolio_analytics import PortfolioAnalytics
    analytics = PortfolioAnalytics(service)
    print("Portfolio analytics created successfully")
    
    print("\nAll core components are working correctly!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()