"""
Main window for Portfolio Manager GUI
"""

from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTableView,
                              QSplitter, QVBoxLayout, QWidget, QPushButton,
                              QHBoxLayout, QMenuBar, QMenu, QStatusBar,
                              QMessageBox, QFileDialog, QLabel)
from PySide6.QtGui import QAction
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.edit_position_dialog import EditPositionDialog
from gui.dashboard_widget import DashboardWidget
from gui.performance_tab import PerformanceTab
from gui.settings_tab import SettingsTab
from gui.dividend_dialog import DividendEntryDialog
from gui.stock_split_dialog import StockSplitDialog
from gui.benchmark_comparison_tab import BenchmarkComparisonTab
from gui.report_tab import ReportTab
from gui.news_tab import NewsTab
from gui.portfolio_optimization_tab import PortfolioOptimizationTab
from gui.personal_finance_tab import PersonalFinanceTab
from gui.tax_management_tab import TaxManagementTab
from services.tax_service import TaxService

from PySide6.QtCore import Qt
from gui.portfolio_table import PortfolioTableModel, PortfolioTableView
from gui.add_position_dialog import AddPositionDialog
from database.database import init_database
from services.portfolio_service import PortfolioService
from services.personal_finance_service import PersonalFinanceService

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, portfolio_service: PortfolioService, personal_finance_service: PersonalFinanceService, tax_service: TaxService):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Portfolio Manager")
        self.setGeometry(100, 100, 1200, 800)
        # Maximize the window
        self.showMaximized()
        
        # Initialize services
        self.portfolio_service = portfolio_service
        self.personal_finance_service = personal_finance_service
        self.tax_service = tax_service
        
        # Create UI elements
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        self.create_central_widget()
        self.create_connections()
        
        # Load initial data
        self.load_data()
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Add position action
        add_position_action = QAction("&Add Position", self)
        add_position_action.setShortcut("Ctrl+N")
        add_position_action.setStatusTip("Add new position")
        edit_menu.addAction(add_position_action)
        
        # Add dividend action
        add_dividend_action = QAction("&Add Dividend", self)
        add_dividend_action.setShortcut("Ctrl+D")
        add_dividend_action.setStatusTip("Add dividend payment")
        edit_menu.addAction(add_dividend_action)
        
        # Add stock split action
        add_stock_split_action = QAction("&Add Stock Split", self)
        add_stock_split_action.setStatusTip("Add stock split")
        edit_menu.addAction(add_stock_split_action)
        
        # Edit position action
        edit_position_action = QAction("&Edit Position", self)
        edit_position_action.setShortcut("Ctrl+E")
        edit_position_action.setStatusTip("Edit selected position")
        edit_menu.addAction(edit_position_action)
        
        # Delete position action
        delete_position_action = QAction("&Delete Position", self)
        delete_position_action.setShortcut("Del")
        delete_position_action.setStatusTip("Delete selected position")
        edit_menu.addAction(delete_position_action)
        
        # Reset action
        reset_action = QAction("&Reset Application", self)
        reset_action.setStatusTip("Reset application to initial state")
        edit_menu.addAction(reset_action)
        
        # Connect actions
        exit_action.triggered.connect(self.close)
        add_position_action.triggered.connect(self.show_add_position_dialog)
        add_dividend_action.triggered.connect(self.show_dividend_dialog)
        add_stock_split_action.triggered.connect(self.show_stock_split_dialog)
        edit_position_action.triggered.connect(self.edit_position)
        delete_position_action.triggered.connect(self.delete_position)
        reset_action.triggered.connect(self.reset_application)
    
    def create_toolbar(self):
        """Create toolbar."""
        toolbar = self.addToolBar("Main")
        
        # Add position button
        add_position_btn = QPushButton("Add Position")
        add_position_btn.clicked.connect(self.show_add_position_dialog)
        toolbar.addWidget(add_position_btn)
        
        # Add dividend button
        add_dividend_btn = QPushButton("Add Dividend")
        add_dividend_btn.clicked.connect(self.show_dividend_dialog)
        toolbar.addWidget(add_dividend_btn)
        
        # Add stock split button
        add_stock_split_btn = QPushButton("Add Stock Split")
        add_stock_split_btn.clicked.connect(self.show_stock_split_dialog)
        toolbar.addWidget(add_stock_split_btn)
        
        # Edit position button
        edit_position_btn = QPushButton("Edit Position")
        edit_position_btn.clicked.connect(self.edit_position)
        toolbar.addWidget(edit_position_btn)
        
        # Delete position button
        delete_position_btn = QPushButton("Delete Position")
        delete_position_btn.clicked.connect(self.delete_position)
        toolbar.addWidget(delete_position_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Prices")
        refresh_btn.clicked.connect(self.refresh_prices)
        toolbar.addWidget(refresh_btn)
    
    def create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")
    
    def create_central_widget(self):
        """Create central widget with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create portfolio table tab
        portfolio_tab = self.create_portfolio_tab()
        tab_widget.addTab(portfolio_tab, "Portfolio")
        
        # Create dashboard tab
        dashboard_tab = DashboardWidget()
        tab_widget.addTab(dashboard_tab, "Dashboard")
        
        # Create performance tab
        performance_tab = PerformanceTab()
        tab_widget.addTab(performance_tab, "Performance")
        
        # Create benchmark comparison tab
        try:
            benchmark_tab = BenchmarkComparisonTab()
            tab_widget.addTab(benchmark_tab, "Benchmark Comparison")
        except Exception as e:
            print(f"Error creating benchmark tab: {e}")
            # Create a simple placeholder tab if the benchmark tab fails
            placeholder_tab = QWidget()
            layout = QVBoxLayout(placeholder_tab)
            layout.addWidget(QLabel("Benchmark Comparison tab failed to initialize"))
            tab_widget.addTab(placeholder_tab, "Benchmark Comparison")
        
        # Create report tab
        report_tab = ReportTab(self.portfolio_service)
        tab_widget.addTab(report_tab, "Reports")
        
        # Create news tab
        news_tab = NewsTab()
        tab_widget.addTab(news_tab, "News")
        
        # Create personal finance tab
        self.personal_finance_tab = PersonalFinanceTab(self.personal_finance_service)
        tab_widget.addTab(self.personal_finance_tab, "Personal Finance")
        
        # Create tax management tab
        self.tax_management_tab = TaxManagementTab(self.tax_service)
        tab_widget.addTab(self.tax_management_tab, "Tax Management")
        
        
        
        # Create settings tab
        settings_tab = SettingsTab()
        tab_widget.addTab(settings_tab, "Settings")
        
        layout.addWidget(tab_widget)
    
    def create_portfolio_tab(self):
        """Create portfolio table tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create table view
        self.portfolio_table = PortfolioTableView()
        layout.addWidget(self.portfolio_table)
        
        # Create button layout
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Position")
        edit_btn = QPushButton("Edit Position")
        delete_btn = QPushButton("Delete Position")
        
        add_btn.clicked.connect(self.show_add_position_dialog)
        edit_btn.clicked.connect(self.edit_position)
        delete_btn.clicked.connect(self.delete_position)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return tab
    
    def create_dashboard_tab(self):
        """Create dashboard tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Dashboard content would go here"))
        return tab
    
    def create_performance_tab(self):
        """Create performance tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Performance charts would go here"))
        return tab
    
    def create_settings_tab(self):
        """Create settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Settings would go here"))
        return tab
    
    def create_connections(self):
        """Create signal connections."""
        pass
    
    def load_data(self):
        """Load initial data."""
        self.portfolio_table.load_data()
    
    def show_add_position_dialog(self):
        """Show dialog to add a new position."""
        dialog = AddPositionDialog(self)
        if dialog.exec():
            # Refresh the table after adding
            self.load_data()
    
    def edit_position(self):
        """Edit selected position."""
        position_id = self.portfolio_table.get_selected_position_id()
        if position_id:
            # Open edit dialog
            dialog = EditPositionDialog(position_id, self)
            if dialog.exec():
                # Refresh the table after editing
                self.load_data()
        else:
            QMessageBox.warning(self, "Edit Position", 
                              "Please select a position to edit.")
    
    def delete_position(self):
        """Delete selected position."""
        # Get the selected position ID from the table view
        selection = self.portfolio_table.selectionModel().selectedRows()
        if selection:
            # Get the row from the selection model
            row = selection[0].row()
            # Get the position ID directly from the model
            model = self.portfolio_table.model()
            if isinstance(model, PortfolioTableModel):
                position_id = model.positions[row].id
                reply = QMessageBox.question(
                    self, 
                    "Delete Position", 
                    "Are you sure you want to delete this position?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        success = self.portfolio_service.delete_position(position_id)
                        if success:
                            self.load_data()
                            self.statusBar().showMessage("Position deleted successfully")
                        else:
                            QMessageBox.warning(self, "Delete Position", 
                                              "Failed to delete position.")
                    except Exception as e:
                        QMessageBox.critical(self, "Delete Position", 
                                           f"Error deleting position: {str(e)}")
        else:
            QMessageBox.warning(self, "Delete Position", 
                              "Please select a position to delete.")
    
    def refresh_prices(self):
        """Refresh all stock prices."""
        try:
            # Get all positions
            positions = self.portfolio_service.get_positions()
            if not positions:
                QMessageBox.information(self, "Refresh Prices", "No positions to refresh.")
                return
                
            # Refresh the table data (which will fetch current prices)
            self.portfolio_table.load_data()
            QMessageBox.information(self, "Refresh Prices", 
                                  "Prices refreshed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Refresh Prices", 
                               f"Error refreshing prices: {str(e)}")
    
    def show_dividend_dialog(self):
        """Show dialog to add a new dividend payment."""
        dialog = DividendEntryDialog(self)
        if dialog.exec():
            # Optionally refresh data after adding dividend
            self.load_data()
    
    def show_stock_split_dialog(self):
        """Show dialog to add a new stock split."""
        # Check if a position is selected
        selected_ticker = None
        selection = self.portfolio_table.selectionModel().selectedRows()
        if selection:
            row = selection[0].row()
            model = self.portfolio_table.model()
            if isinstance(model, PortfolioTableModel):
                selected_ticker = model.positions[row].ticker
        
        dialog = StockSplitDialog(self, selected_ticker)
        if dialog.exec():
            # Refresh data after adding stock split
            self.load_data()
    
    def reset_application(self):
        """Reset application to initial state."""
        reply = QMessageBox.question(
            self, 
            "Reset Application", 
            "Delete all portfolio data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # For now, just show a message - will implement reset logic
            # in later milestone
            QMessageBox.information(self, "Reset Application", 
                                  "Reset functionality will be implemented in later milestone.")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()