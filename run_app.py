#!/usr/bin/env python3
"""
Portfolio Manager - Main Application Entry Point
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from portfolio_manager.gui.main_window import MainWindow
from portfolio_manager.services.portfolio_service import PortfolioService
from portfolio_manager.services.personal_finance_service import PersonalFinanceService
from portfolio_manager.database.database import init_database

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
    
    # Create and show main window
    main_window = MainWindow(portfolio_service, personal_finance_service)
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()