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
                              QTableWidgetItem, QGroupBox)
from PySide6.QtCore import Qt
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
        
        # Portfolio performance summary
        summary_group = QGroupBox("Portfolio Performance Summary")
        summary_layout = QFormLayout(summary_group)
        
        self.total_value_label = QLabel("N/A")
        self.total_gain_loss_label = QLabel("N/A")
        self.total_gain_loss_percent_label = QLabel("N/A")
        self.annual_return_label = QLabel("N/A")
        self.volatility_label = QLabel("N/A")
        
        summary_layout.addRow("Total Value:", self.total_value_label)
        summary_layout.addRow("Gain/Loss:", self.total_gain_loss_label)
        summary_layout.addRow("Gain/Loss %:", self.total_gain_loss_percent_label)
        summary_layout.addRow("Annual Return:", self.annual_return_label)
        summary_layout.addRow("Volatility:", self.volatility_label)
        
        layout.addWidget(summary_group)
        
        # Top performing assets
        top_assets_group = QGroupBox("Top Performing Assets")
        top_layout = QVBoxLayout(top_assets_group)
        
        self.top_assets_table = QTableWidget(0, 3)
        self.top_assets_table.setHorizontalHeaderLabels(["Ticker", "Gain/Loss", "Gain/Loss %"])
        self.top_assets_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        top_layout.addWidget(self.top_assets_table)
        
        layout.addWidget(top_assets_group)
        
        # Date range selection
        date_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout(date_group)
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["1D", "1W", "1M", "3M", "6M", "1Y", "All Time"])
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_performance_data)
        
        date_layout.addWidget(QLabel("Select Range:"))
        date_layout.addWidget(self.date_range_combo)
        date_layout.addStretch()
        date_layout.addWidget(refresh_btn)
        
        layout.addWidget(date_group)
    
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
            
            # Update summary labels
            self.total_value_label.setText(f"${total_value:,.2f}")
            self.total_gain_loss_label.setText(f"${total_gain_loss:,.2f}")
            self.total_gain_loss_percent_label.setText(f"{total_gain_loss_percent:.2f}%")
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
                self.top_assets_table.setItem(i, 2, QTableWidgetItem(f"{asset['gain_loss_percent']:.2f}%"))
                
        except Exception as e:
            print(f"Error loading top assets: {e}")