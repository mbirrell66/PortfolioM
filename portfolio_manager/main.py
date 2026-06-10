#!/usr/bin/env python3
"""
Portfolio Manager - Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from services.portfolio_service import PortfolioService
from services.personal_finance_service import PersonalFinanceService
from services.tax_service import TaxService
from database.database import init_database

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Portfolio Manager")
    app.setApplicationVersion("1.0.0")
    
    # Initialize database
    init_database()
    
    # Create services
    portfolio_service = PortfolioService()
    personal_finance_service = PersonalFinanceService()
    tax_service = TaxService()
    
    # Create and show main window
    main_window = MainWindow(portfolio_service, personal_finance_service, tax_service)
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()