#!/usr/bin/env python3
"""
Portfolio Manager - Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Portfolio Manager")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()