"""
Main window for Portfolio Manager GUI
"""

from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTableView,
                               QSplitter, QVBoxLayout, QWidget, QPushButton,
                               QHBoxLayout, QMenuBar, QMenu, QStatusBar,
                               QMessageBox, QFileDialog, QLabel)
from PySide6.QtGui import QAction, QLinearGradient, QColor, QPalette
from PySide6.QtCore import Qt, QSize
from gui.icons import get_icon
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.edit_position_dialog import EditPositionDialog
from gui.watchlist_tab import WatchlistTab
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
from gui.options_tab import OptionsTab
from gui.position_size_calculator import PositionSizeCalculator
from services.tax_service import TaxService
from services.options_service import OptionsService

from gui.portfolio_table import PortfolioTableModel, PortfolioTableView, ClosedPositionsTableView
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

        # Initialize services
        self.portfolio_service = portfolio_service
        self.personal_finance_service = personal_finance_service
        self.tax_service = tax_service
        
        # Apply dark theme
        self.apply_dark_theme()
        
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
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #0F1117;
                color: #DDE8FF;
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: rgba(74, 158, 255, 0.2);
            }
            QMenuBar::item:pressed {
                background-color: rgba(74, 158, 255, 0.3);
            }
            QMenu {
                background-color: #0F1117;
                color: #DDE8FF;
                font-size: 13px;
                padding: 6px;
                border: 1px solid #222844;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(74, 158, 255, 0.2);
            }
            QMenu::item:pressed {
                background-color: rgba(74, 158, 255, 0.3);
            }
            QMenu::separator {
                height: 1px;
                background-color: #222844;
                margin: 4px 0;
            }
        """)
        
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

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        pos_sizer_action = QAction("&Position Size Calculator", self)
        pos_sizer_action.setShortcut("Ctrl+P")
        pos_sizer_action.setStatusTip("Open the position size calculator")
        tools_menu.addAction(pos_sizer_action)

        # Connect actions
        exit_action.triggered.connect(self.close)
        add_position_action.triggered.connect(self.show_add_position_dialog)
        add_dividend_action.triggered.connect(self.show_dividend_dialog)
        add_stock_split_action.triggered.connect(self.show_stock_split_dialog)
        edit_position_action.triggered.connect(self.edit_position)
        delete_position_action.triggered.connect(self.delete_position)
        reset_action.triggered.connect(self.reset_application)
        pos_sizer_action.triggered.connect(self.show_position_sizer)
    
    def create_toolbar(self):
        """Create toolbar with SVG-icon QActions."""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #191D2E;
                border: none;
                border-bottom: 1px solid #222844;
                padding: 5px 8px;
                spacing: 2px;
            }
            QToolButton {
                background-color: transparent;
                color: #BECCE8;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QToolButton:hover {
                background-color: rgba(74, 158, 255, 0.15);
                color: #5295FF;
            }
            QToolButton:pressed {
                background-color: rgba(74, 158, 255, 0.28);
            }
            QToolBar::separator {
                background-color: #222844;
                width: 1px;
                margin: 4px 6px;
            }
        """)

        add_action = QAction(get_icon("ACT_ADD"), "Add Position", self)
        add_action.setToolTip("Add new position  (Ctrl+N)")
        add_action.triggered.connect(self.show_add_position_dialog)
        toolbar.addAction(add_action)

        div_action = QAction(get_icon("ACT_DIVIDEND"), "Add Dividend", self)
        div_action.setToolTip("Record dividend payment  (Ctrl+D)")
        div_action.triggered.connect(self.show_dividend_dialog)
        toolbar.addAction(div_action)

        split_action = QAction(get_icon("ACT_SPLIT"), "Add Split", self)
        split_action.setToolTip("Record stock split")
        split_action.triggered.connect(self.show_stock_split_dialog)
        toolbar.addAction(split_action)

        toolbar.addSeparator()

        edit_action = QAction(get_icon("ACT_EDIT"), "Edit", self)
        edit_action.setToolTip("Edit selected position  (Ctrl+E)")
        edit_action.triggered.connect(self.edit_position)
        toolbar.addAction(edit_action)

        delete_action = QAction(get_icon("ACT_DELETE"), "Delete", self)
        delete_action.setToolTip("Delete selected position  (Del)")
        delete_action.triggered.connect(self.delete_position)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        refresh_action = QAction(get_icon("ACT_REFRESH"), "Refresh", self)
        refresh_action.setToolTip("Refresh all prices")
        refresh_action.triggered.connect(self.refresh_prices)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        calc_action = QAction(get_icon("ACT_CALC"), "Position Sizer", self)
        calc_action.setToolTip("Open the position size calculator  (Ctrl+P)")
        calc_action.triggered.connect(self.show_position_sizer)
        toolbar.addAction(calc_action)
    
    def create_status_bar(self):
        """Create status bar."""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0F1117;
                color: #7488B8;
                font-size: 13px;
                padding: 4px 8px;
            }
            QStatusBar::item {
                border-radius: 3px;
                padding: 2px 6px;
            }
        """)
        status_bar.showMessage("Ready")
    
    def create_central_widget(self):
        """Create central widget with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setIconSize(QSize(16, 16))
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: #0F1117;
                border: 1px solid #222844;
                border-radius: 8px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #191D2E;
                color: #7488B8;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 500;
                border: 1px solid #222844;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background-color: #0F1117;
                color: #DDE8FF;
                font-weight: 600;
                border-bottom-color: #0F1117;
            }
            QTabBar::tab:hover {
                background-color: #222844;
                color: #5295FF;
            }
            QTabBar::tab:last {
                margin-right: 0;
            }
        """)

        portfolio_tab = self.create_portfolio_tab()
        tab_widget.addTab(portfolio_tab, get_icon("PORTFOLIO"), "Portfolio")

        watchlist_tab = WatchlistTab()
        tab_widget.addTab(watchlist_tab, get_icon("WATCHLIST"), "Watchlist")

        dashboard_tab = DashboardWidget()
        tab_widget.addTab(dashboard_tab, get_icon("DASHBOARD"), "Dashboard")

        performance_tab = PerformanceTab()
        tab_widget.addTab(performance_tab, get_icon("PERFORMANCE"), "Performance")

        try:
            from services.market_data import MarketDataService
            benchmark_tab = BenchmarkComparisonTab(self.portfolio_service, MarketDataService())
            tab_widget.addTab(benchmark_tab, get_icon("BENCHMARK"), "Benchmark")
        except Exception as e:
            print(f"Error creating benchmark tab: {e}")
            placeholder_tab = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_tab)
            placeholder_layout.addWidget(QLabel("Benchmark tab failed to initialize"))
            tab_widget.addTab(placeholder_tab, get_icon("BENCHMARK"), "Benchmark")

        report_tab = ReportTab(self.portfolio_service)
        tab_widget.addTab(report_tab, get_icon("REPORTS"), "Reports")

        news_tab = NewsTab(self.portfolio_service)
        tab_widget.addTab(news_tab, get_icon("NEWS"), "News")

        self.personal_finance_tab = PersonalFinanceTab(self.personal_finance_service, self.portfolio_service)
        tab_widget.addTab(self.personal_finance_tab, get_icon("FINANCE"), "Personal Finance")

        self.tax_management_tab = TaxManagementTab(self.tax_service)
        tab_widget.addTab(self.tax_management_tab, get_icon("TAX"), "Tax Management")

        options_svc = OptionsService()
        self.options_tab = OptionsTab(options_svc, self.portfolio_service,
                                      self.personal_finance_service)
        tab_widget.addTab(self.options_tab, get_icon("FINANCE"), "Options")

        settings_tab = SettingsTab()
        tab_widget.addTab(settings_tab, get_icon("SETTINGS"), "Settings")

        main_layout.addWidget(tab_widget)
    
    def create_portfolio_tab(self):
        """Create portfolio tab with Open and Closed Positions sub-tabs."""
        from PySide6.QtWidgets import QTabWidget as _QTW
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sub-tab widget
        self._portfolio_sub_tabs = _QTW()
        self._portfolio_sub_tabs.setStyleSheet("""
            QTabWidget::pane { background-color: #0F1117; border: 1px solid #222844; border-radius: 6px; margin-top: -1px; }
            QTabBar::tab { background-color: #191D2E; color: #7488B8; padding: 8px 18px; font-size: 12px; font-weight: 500; border: 1px solid #222844; border-bottom: none; border-top-left-radius: 5px; border-top-right-radius: 5px; margin-right: 3px; }
            QTabBar::tab:selected { background-color: #0F1117; color: #DDE8FF; font-weight: 600; }
            QTabBar::tab:hover { color: #5295FF; }
        """)

        # Open positions pane
        open_pane = QWidget()
        open_layout = QVBoxLayout(open_pane)
        open_layout.setContentsMargins(4, 4, 4, 4)
        self.portfolio_table = PortfolioTableView()
        open_layout.addWidget(self.portfolio_table)

        btn_row = QHBoxLayout()
        for label, slot in [("Add Position", self.show_add_position_dialog),
                             ("Edit Position", self.edit_position),
                             ("Delete Position", self.delete_position)]:
            b = QPushButton(label)
            b.clicked.connect(slot)
            btn_row.addWidget(b)
        btn_row.addStretch()
        open_layout.addLayout(btn_row)

        # Closed positions pane
        closed_pane = QWidget()
        closed_layout = QVBoxLayout(closed_pane)
        closed_layout.setContentsMargins(4, 4, 4, 4)
        self.closed_positions_table = ClosedPositionsTableView()
        closed_layout.addWidget(self.closed_positions_table)

        closed_btn_row = QHBoxLayout()
        edit_closed_btn = QPushButton("Edit / Reopen")
        edit_closed_btn.clicked.connect(self._edit_closed_position)
        closed_btn_row.addWidget(edit_closed_btn)
        closed_btn_row.addStretch()
        closed_layout.addLayout(closed_btn_row)

        self._portfolio_sub_tabs.addTab(open_pane, "Open Positions")
        self._portfolio_sub_tabs.addTab(closed_pane, "Closed Positions")
        layout.addWidget(self._portfolio_sub_tabs)
        return tab

    def _edit_closed_position(self):
        """Edit a closed position (allows re-opening by clearing sell date)."""
        position_id = self.closed_positions_table.get_selected_position_id()
        if not position_id:
            QMessageBox.warning(self, "Edit", "Select a position to edit.")
            return
        from gui.edit_position_dialog import EditPositionDialog
        dialog = EditPositionDialog(position_id, self)
        if dialog.exec():
            self.load_data()
    
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
    
    def apply_dark_theme(self):
        """Apply dark theme to the entire application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F1117;
            }
            QPushButton {
                background-color: #5295FF; color: #0F1117; border: none;
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
                font-weight: 600; min-width: 80px;
            }
            QPushButton:hover { background-color: #4080EE; }
            QPushButton:pressed { background-color: #327AE0; }
        """)

    def create_connections(self):
        """Create signal connections."""
        pass
    
    def load_data(self):
        """Load initial data."""
        self.portfolio_table.load_data()
        if hasattr(self, 'closed_positions_table'):
            self.closed_positions_table.load_data()
    
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
    
    def show_position_sizer(self):
        """Open the position size calculator dialog."""
        dlg = PositionSizeCalculator(self.portfolio_service, parent=self)
        dlg.exec()

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
                                  "Reset functionality will be implemented in a later milestone.")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
