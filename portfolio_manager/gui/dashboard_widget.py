"""
Dashboard widget for Portfolio Manager
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QFrame, QTableWidget, QTableWidgetItem,
                              QHeaderView, QSplitter)
from PySide6.QtCore import Qt
from services.portfolio_service import PortfolioService
import pyqtgraph as pg

class DashboardWidget(QWidget):
    """Dashboard widget with portfolio analytics and charts."""
    
    def __init__(self, parent=None):
        """Initialize dashboard widget."""
        super().__init__(parent)
        self.portfolio_service = PortfolioService()
        
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Create a splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Top panel with summary
        summary_widget = QFrame()
        summary_layout = QGridLayout(summary_widget)
        summary_layout.setSpacing(10)
        
        # Summary labels
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_gain_label = QLabel("Total Gain/Loss: $0.00")
        self.total_gain_percent_label = QLabel("Total Gain/Loss %: 0.00%")
        self.position_count_label = QLabel("Positions: 0")
        
        # Format labels
        self.total_value_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.total_gain_label.setStyleSheet("font-size: 14px; color: green;")
        self.total_gain_percent_label.setStyleSheet("font-size: 14px; color: green;")
        self.position_count_label.setStyleSheet("font-size: 14px;")
        
        # Add to grid
        summary_layout.addWidget(QLabel("Portfolio Summary:"), 0, 0, 1, 2)
        summary_layout.addWidget(self.total_value_label, 1, 0)
        summary_layout.addWidget(self.total_gain_label, 2, 0)
        summary_layout.addWidget(self.total_gain_percent_label, 3, 0)
        summary_layout.addWidget(self.position_count_label, 4, 0)
        
        # Chart area
        self.chart_widget = pg.PlotWidget()
        self.chart_widget.setTitle("Portfolio Distribution")
        self.chart_widget.setLabel('left', 'Value ($)')
        self.chart_widget.setLabel('bottom', 'Asset')
        
        # Performance table
        self.performance_table = QTableWidget(0, 5)
        self.performance_table.setHorizontalHeaderLabels([
            "Ticker", "Company", "Shares", "Value", "Gain/Loss %"
        ])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add widgets to splitter
        splitter.addWidget(summary_widget)
        splitter.addWidget(self.chart_widget)
        splitter.addWidget(self.performance_table)
        
        # Set splitter sizes
        splitter.setSizes([100, 200, 200])
        
        layout.addWidget(splitter)
        
        # Set layout properties
        layout.setContentsMargins(10, 10, 10, 10)
        
    def load_data(self):
        """Load and display dashboard data."""
        try:
            # Get all positions
            positions = self.portfolio_service.get_positions()
            
            # Calculate portfolio summary
            total_value = 0
            total_cost = 0
            position_count = len(positions)
            
            for position in positions:
                current_price = self.portfolio_service.get_current_price(position.ticker)
                market_value = current_price * position.shares
                cost_basis = position.purchase_price * position.shares
                total_value += market_value
                total_cost += cost_basis
            
            # Calculate total gain/loss
            total_gain_loss = total_value - total_cost
            total_gain_percent = (total_gain_loss / total_cost) * 100 if total_cost != 0 else 0
            
            # Update summary labels
            self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
            self.total_gain_label.setText(f"Total Gain/Loss: ${total_gain_loss:,.2f}")
            self.total_gain_percent_label.setText(f"Total Gain/Loss %: {total_gain_percent:+.2f}%")
            self.position_count_label.setText(f"Positions: {position_count}")
            
            # Update chart
            self.update_chart(positions)
            
            # Update performance table
            self.update_performance_table(positions)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def update_chart(self, positions):
        """Update the portfolio distribution chart."""
        try:
            # Clear existing plots
            self.chart_widget.clear()
            
            if positions:
                # Prepare data for chart
                labels = []
                values = []
                
                for position in positions:
                    current_price = self.portfolio_service.get_current_price(position.ticker)
                    market_value = current_price * position.shares
                    labels.append(position.ticker)
                    values.append(market_value)
                
                # Create bar chart
                bar_chart = pg.BarGraphItem(
                    x=range(len(labels)),
                    height=values,
                    width=0.6,
                    brush='g'
                )
                
                # Add to plot
                self.chart_widget.addItem(bar_chart)
                
                # Set labels
                self.chart_widget.getPlotItem().getAxis('bottom').setTicks([list(enumerate(labels))])
                self.chart_widget.getPlotItem().getAxis('bottom').setLabel('Assets')
                
        except Exception as e:
            print(f"Error updating chart: {e}")
    
    def update_performance_table(self, positions):
        """Update the performance table."""
        try:
            # Clear existing rows
            self.performance_table.setRowCount(0)
            
            # Add rows
            for i, position in enumerate(positions):
                self.performance_table.insertRow(i)
                
                # Get current data
                current_price = self.portfolio_service.get_current_price(position.ticker)
                market_value = current_price * position.shares
                cost_basis = position.purchase_price * position.shares
                gain_loss = market_value - cost_basis
                gain_percent = (gain_loss / cost_basis) * 100 if cost_basis != 0 else 0
                
                # Set item data
                self.performance_table.setItem(i, 0, QTableWidgetItem(position.ticker))
                self.performance_table.setItem(i, 1, QTableWidgetItem(position.company_name))
                self.performance_table.setItem(i, 2, QTableWidgetItem(str(position.shares)))
                self.performance_table.setItem(i, 3, QTableWidgetItem(f"${market_value:,.2f}"))
                gain_percent_str = f"{gain_percent:+.2f}%"
                self.performance_table.setItem(i, 4, QTableWidgetItem(gain_percent_str))
                
        except Exception as e:
            print(f"Error updating performance table: {e}")