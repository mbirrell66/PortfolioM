"""
Performance tab for Portfolio Manager
"""
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLabel, QComboBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QGroupBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.portfolio_service import PortfolioService


class PerformanceTab(QWidget):
    """Performance tab showing portfolio analytics."""
    
    def __init__(self):
        """Initialize performance tab."""
        super().__init__()
        self.portfolio_service = PortfolioService()
        self.init_ui()
        self.load_performance_data()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0F1117;
                border: none;
            }
        """)
        
        perf_widget = QWidget()
        perf_layout = QVBoxLayout(perf_widget)
        perf_layout.setSpacing(20)
        perf_layout.setContentsMargins(20, 20, 20, 20)
        
        # Portfolio performance summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        summary_layout = QFormLayout(summary_frame)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(12)
        
        summary_header = QLabel("Portfolio Performance Summary")
        summary_header.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #DDE8FF;
            padding-bottom: 12px;
            border-bottom: 2px solid #5295FF;
        """)
        summary_layout.addRow(summary_header)
        
        self.total_value_label = QLabel("N/A")
        self.total_value_label.setStyleSheet("font-size: 14px; color: #DDE8FF;")
        self.total_gain_loss_label = QLabel("N/A")
        self.total_gain_loss_label.setStyleSheet("font-size: 14px; color: #7488B8;")
        self.total_gain_loss_percent_label = QLabel("N/A")
        self.total_gain_loss_percent_label.setStyleSheet("font-size: 14px; color: #7488B8;")
        self.annual_return_label = QLabel("N/A")
        self.annual_return_label.setStyleSheet("font-size: 14px; color: #7488B8;")
        self.volatility_label = QLabel("N/A")
        self.volatility_label.setStyleSheet("font-size: 14px; color: #7488B8;")
        
        summary_layout.addRow("Total Value:", self.total_value_label)
        summary_layout.addRow("Gain/Loss:", self.total_gain_loss_label)
        summary_layout.addRow("Gain/Loss %:", self.total_gain_loss_percent_label)
        summary_layout.addRow("Annual Return:", self.annual_return_label)
        summary_layout.addRow("Volatility:", self.volatility_label)
        
        perf_layout.addWidget(summary_frame)
        
        # Top performing assets
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        top_layout = QVBoxLayout(top_frame)
        top_layout.setContentsMargins(16, 16, 16, 16)
        
        top_header = QLabel("Top Performing Assets")
        top_header.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #DDE8FF;
            padding-bottom: 12px;
            border-bottom: 2px solid #5295FF;
        """)
        top_layout.addWidget(top_header)
        
        self.top_assets_table = QTableWidget(0, 3)
        self.top_assets_table.setHorizontalHeaderLabels(["Ticker", "Gain/Loss", "Gain/Loss %"])
        self.top_assets_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_assets_table.setStyleSheet("""
            QTableWidget {
                background-color: #0F1117;
                color: #DDE8FF;
                gridline-color: transparent;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: rgba(74, 158, 255, 0.3);
            }
            QTableWidget::item:hover {
                background-color: rgba(74, 158, 255, 0.15);
            }
            QHeaderView::section {
                background-color: #191D2E;
                color: #7488B8;
                padding: 8px 10px;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-right: 1px solid #222844;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last { border-right: none; }
        """)
        top_layout.addWidget(self.top_assets_table)
        
        perf_layout.addWidget(top_frame)
        
        # Date range selection
        date_frame = QFrame()
        date_frame.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(16, 16, 16, 16)
        
        date_layout.addWidget(QLabel("Select Range:"))
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["1D", "1W", "1M", "3M", "6M", "1Y", "All Time"])
        self.date_range_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F1117;
                color: #DDE8FF;
                border: 1px solid #222844;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QComboBox:hover {
                border-color: #5295FF;
            }
            QComboBox::drop-down {
                background-color: #222844;
                border: none;
                padding: 4px;
            }
        """)
        date_layout.addWidget(self.date_range_combo)
        date_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_performance_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #5295FF;
                color: #0F1117;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4080EE;
            }
            QPushButton:pressed {
                background-color: #327AE0;
            }
        """)
        date_layout.addWidget(refresh_btn)
        
        perf_layout.addWidget(date_frame)
        
        scroll_area.setWidget(perf_widget)
        layout.addWidget(scroll_area)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1117;
            }
        """)
    
    def load_performance_data(self):
        """Load and display performance data."""
        try:
            # Get all positions
            positions = self.portfolio_service.get_positions()
            
            # Cache current prices for all positions
            current_prices = {}
            tickers = list(set([position.ticker for position in positions]))
            for ticker in tickers:
                current_prices[ticker] = self.portfolio_service.get_current_price(ticker)
            
            # Calculate portfolio summary
            total_value = 0
            total_cost = 0
            
            for position in positions:
                current_price = current_prices.get(position.ticker, 0)
                if current_price:
                    market_value = current_price * position.shares
                    cost_basis = position.purchase_price * position.shares
                    total_value += market_value
                    total_cost += cost_basis
            
            # Calculate totals
            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost != 0 else 0
            
            # Calculate annual return (simplified for now)
            # In a real implementation, this would use actual time periods
            annual_return = 0.05  # 5% annual return (example)
            volatility = 0.15  # 15% volatility (example)
            
            # Update summary labels with color coding
            gain_loss_color = "#24CDB0" if total_gain_loss >= 0 else "#FF3558"
            self.total_value_label.setText(f"${total_value:,.2f}")
            self.total_gain_loss_label.setText(f"${total_gain_loss:,.2f}")
            self.total_gain_loss_label.setStyleSheet(f"font-size: 14px; color: {gain_loss_color}; font-weight: 600;")
            self.total_gain_loss_percent_label.setText(f"{total_gain_loss_percent:+.2f}%")
            self.total_gain_loss_percent_label.setStyleSheet(f"font-size: 14px; color: {gain_loss_color}; font-weight: 600;")
            self.annual_return_label.setText(f"{annual_return:.2f}%")
            self.volatility_label.setText(f"{volatility:.2f}%")
            
            # Load top assets
            self.load_top_assets()
            
        except Exception as e:
            print(f"Error loading performance data: {e}")
    
    def load_top_assets(self):
        """Load top performing assets."""
        try:
            # Get positions with gain/loss data
            positions = self.portfolio_service.get_positions()
            if not positions:
                self.top_assets_table.setRowCount(0)
                return
            
            # Cache current prices for all positions
            current_prices = {}
            tickers = list(set([position.ticker for position in positions]))
            for ticker in tickers:
                current_prices[ticker] = self.portfolio_service.get_current_price(ticker)
            
            # Calculate gain/loss for each position
            top_assets = []
            for position in positions:
                current_price = current_prices.get(position.ticker, 0)
                if current_price:
                    current_value = position.shares * current_price
                    purchase_value = position.shares * position.purchase_price
                    gain_loss = current_value - purchase_value
                    gain_loss_percent = (gain_loss / purchase_value) * 100 if purchase_value != 0 else 0
                    
                    top_assets.append({
                        'ticker': position.ticker,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_percent
                    })
            
            # Sort by gain/loss percentage descending
            top_assets.sort(key=lambda x: x['gain_loss_percent'], reverse=True)
            
            # Display top 5
            self.top_assets_table.setRowCount(min(5, len(top_assets)))
            for i, asset in enumerate(top_assets[:5]):
                self.top_assets_table.setItem(i, 0, QTableWidgetItem(asset['ticker']))
                self.top_assets_table.setItem(i, 1, QTableWidgetItem(f"${asset['gain_loss']:,.2f}"))
                
                gain_loss_item = QTableWidgetItem(f"{asset['gain_loss_percent']:.2f}%")
                gain_loss_color = "#24CDB0" if asset['gain_loss_percent'] >= 0 else "#FF3558"
                gain_loss_item.setForeground(QColor(gain_loss_color))
                self.top_assets_table.setItem(i, 2, gain_loss_item)
                
        except Exception as e:
            print(f"Error loading top assets: {e}")
