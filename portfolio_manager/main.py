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

# Global stylesheet applied app-wide.
# Sets default text colour on all widgets so unstyled QLabel / QGroupBox /
# form-row labels don't fall back to the OS black.  Widgets with their own
# explicit colour rules override this automatically via QSS specificity.
_APP_STYLE = (
    # Default text colour for every widget
    "QWidget { color: #DDE8FF; }"
    # Scrollbars
    "QScrollBar:vertical { background: #0B0D16; width: 8px; margin: 0; }"
    "QScrollBar::handle:vertical { background: #2E3662; min-height: 24px; border-radius: 4px; }"
    "QScrollBar::handle:vertical:hover { background: #5295FF; }"
    "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    "QScrollBar:horizontal { background: #0B0D16; height: 8px; margin: 0; }"
    "QScrollBar::handle:horizontal { background: #2E3662; min-width: 24px; border-radius: 4px; }"
    "QScrollBar::handle:horizontal:hover { background: #5295FF; }"
    "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
    # Tooltips
    "QToolTip { background-color: #191D2E; color: #DDE8FF;"
    " border: 1px solid #2E3662; border-radius: 4px; padding: 4px 8px; font-size: 12px; }"
)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyleSheet(_APP_STYLE)

    app.setApplicationName("Portfolio Manager")
    app.setApplicationVersion("1.0.0")

    init_database()

    portfolio_service = PortfolioService()
    personal_finance_service = PersonalFinanceService()
    tax_service = TaxService()

    main_window = MainWindow(portfolio_service, personal_finance_service, tax_service)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
