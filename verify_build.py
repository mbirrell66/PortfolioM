# Portfolio Manager - Build Script

# This script prepares the application for distribution as a standalone executable

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports to verify everything works
try:
    from gui.main_window import MainWindow
    from services.portfolio_service import PortfolioService
    from services.personal_finance_service import PersonalFinanceService
    from services.tax_service import TaxService
    from database.database import init_database
    print("All imports successful!")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

print("Build script verification complete.")