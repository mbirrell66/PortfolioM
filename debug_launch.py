#!/usr/bin/env python3
"""
Debug script to launch the portfolio manager app
"""
import sys
import os

print("Starting debug script...")
print("Current working directory:", os.getcwd())
print("Python path:", sys.path[:3])

# Add the project root to Python path
project_root = "D:/Projects/PortfolioM"
sys.path.insert(0, project_root)
print("Added project root to path:", project_root)

try:
    print("Attempting to import QApplication...")
    from PySide6.QtWidgets import QApplication
    print("QApplication imported successfully")
    
    print("Attempting to import MainWindow...")
    from portfolio_manager.gui.main_window import MainWindow
    print("MainWindow imported successfully")
    
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("QApplication created successfully")
    
    print("Creating MainWindow...")
    main_window = MainWindow()
    print("MainWindow created successfully")
    
    print("Showing main window...")
    main_window.show()
    print("Main window shown successfully")
    
    print("Starting application event loop...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()