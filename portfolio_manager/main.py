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

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QTimer
from gui.main_window import MainWindow
from services.portfolio_service import PortfolioService
from services.personal_finance_service import PersonalFinanceService
from services.tax_service import TaxService
from database.database import init_database

# Global stylesheet applied app-wide.
_APP_STYLE = (
    "QWidget { color: #DDE8FF; }"
    "QScrollBar:vertical { background: #0B0D16; width: 8px; margin: 0; }"
    "QScrollBar::handle:vertical { background: #4B6599; min-height: 24px; border-radius: 4px; }"
    "QScrollBar::handle:vertical:hover { background: #5295FF; }"
    "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    "QScrollBar:horizontal { background: #0B0D16; height: 8px; margin: 0; }"
    "QScrollBar::handle:horizontal { background: #4B6599; min-width: 24px; border-radius: 4px; }"
    "QScrollBar::handle:horizontal:hover { background: #5295FF; }"
    "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
    "QToolTip { background-color: #191D2E; color: #DDE8FF;"
    " border: 1px solid #4B6599; border-radius: 4px; padding: 4px 8px; font-size: 12px; }"
    # -- Calendar popup (QDateEdit setCalendarPopup) -----------------------
    "QCalendarWidget QWidget { alternate-background-color: #191D2E; color: #DDE8FF; }"
    "QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #191D2E; }"
    "QCalendarWidget QToolButton {"
    " color: #DDE8FF; background-color: #191D2E; border: none;"
    " border-radius: 4px; padding: 4px 10px; margin: 2px; font-size: 13px; }"
    "QCalendarWidget QToolButton:hover { background-color: #222844; color: #5295FF; }"
    "QCalendarWidget QToolButton::menu-indicator { image: none; }"
    "QCalendarWidget QSpinBox {"
    " background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;"
    " border-radius: 4px; padding: 2px 4px; }"
    "QCalendarWidget QMenu {"
    " background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844; }"
    "QCalendarWidget QMenu::item:selected { background-color: #5295FF; color: #0F1117; }"
    "QCalendarWidget QAbstractItemView:enabled {"
    " background-color: #0F1117; color: #DDE8FF; gridline-color: #222844;"
    " selection-background-color: #5295FF; selection-color: #0F1117; outline: none; }"
    "QCalendarWidget QAbstractItemView:disabled { color: #4B6599; }"
)


def _icon_path() -> Path:
    """Return the absolute path to PortM.png -- works frozen and non-frozen."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "PortM.png"
    return Path(__file__).parent / "PortM.png"


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyleSheet(_APP_STYLE)

    app.setApplicationName("Portfolio Manager")
    app.setApplicationVersion("1.0.0")

    png = _icon_path()

    # -- Application icon (taskbar + window chrome) ------------------------
    if png.exists():
        app.setWindowIcon(QIcon(str(png)))

    # -- Splash screen (3 seconds) -----------------------------------------
    splash = None
    if png.exists():
        pixmap = QPixmap(str(png))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
            splash.show()
            app.processEvents()

    # -- Initialise backend while splash is visible ------------------------
    init_database()

    portfolio_service = PortfolioService()
    personal_finance_service = PersonalFinanceService()
    tax_service = TaxService()

    main_window = MainWindow(portfolio_service, personal_finance_service, tax_service)

    def _launch():
        if splash:
            splash.finish(main_window)
        main_window.show()
        # Centre the window on the primary screen at startup.
        frame = main_window.frameGeometry()
        frame.moveCenter(app.primaryScreen().availableGeometry().center())
        main_window.move(frame.topLeft())

    QTimer.singleShot(3000, _launch)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
