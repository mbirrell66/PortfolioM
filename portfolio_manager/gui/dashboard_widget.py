"""
Dashboard widget for Portfolio Manager
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                QLabel, QFrame, QTableWidget, QTableWidgetItem,
                                QHeaderView, QSplitter, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.portfolio_service import PortfolioService
from datetime import datetime
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a scroll area for the dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0F1117;
                border: none;
            }
        """)
        
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        dashboard_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top panel with summary
        summary_widget = QFrame()
        summary_widget.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        summary_layout = QGridLayout(summary_widget)
        summary_layout.setSpacing(12)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        
        # Summary labels with modern styling
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_gain_label = QLabel("Total Gain/Loss: $0.00")
        self.total_gain_percent_label = QLabel("Total Gain/Loss %: 0.00%")
        self.position_count_label = QLabel("Positions: 0")
        
        # Header label
        summary_header = QLabel("Portfolio Summary")
        summary_header.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #DDE8FF;
            padding-bottom: 8px;
            border-bottom: 2px solid #5295FF;
        """)
        
        # Format labels
        for label in [self.total_value_label, self.total_gain_label, 
                      self.total_gain_percent_label, self.position_count_label]:
            label.setStyleSheet("""
                font-size: 15px;
                color: #7488B8;
            """)
        
        self.total_value_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #DDE8FF;
        """)
        
        # Add to grid
        summary_layout.addWidget(summary_header, 0, 0, 1, 2)
        summary_layout.addWidget(QLabel("Total Value"), 1, 0)
        summary_layout.addWidget(self.total_value_label, 1, 1)
        summary_layout.addWidget(QLabel("Gain / Loss"), 2, 0)
        summary_layout.addWidget(self.total_gain_label, 2, 1)
        summary_layout.addWidget(QLabel("Gain / Loss %"), 3, 0)
        summary_layout.addWidget(self.total_gain_percent_label, 3, 1)
        summary_layout.addWidget(QLabel("Positions"), 4, 0)
        summary_layout.addWidget(self.position_count_label, 4, 1)
        
        # Chart area
        chart_widget = QFrame()
        chart_widget.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(16, 16, 16, 16)
        
        self.chart_widget = pg.PlotWidget()
        self.chart_widget.setTitle("Portfolio Distribution", color="#DDE8FF", size="16px")
        self.chart_widget.setLabel('left', 'Value ($)', color="#7488B8")
        self.chart_widget.setLabel('bottom', 'Asset', color="#7488B8")
        self.chart_widget.setStyleSheet("""
            PlotWidget {
                background-color: #0F1117;
                border-radius: 8px;
            }
        """)
        chart_layout.addWidget(self.chart_widget)
        
        # Performance table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #191D2E;
                border-radius: 12px;
                border: 1px solid #222844;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(16, 16, 16, 16)
        
        table_header = QLabel("Performance Overview")
        table_header.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #DDE8FF;
            padding-bottom: 12px;
            border-bottom: 2px solid #5295FF;
        """)
        table_layout.addWidget(table_header)
        
        self.performance_table = QTableWidget(0, 6)
        self.performance_table.setHorizontalHeaderLabels([
            "Ticker", "Company", "Shares", "Value", "Gain/Loss %", "CAGR"
        ])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.performance_table.setStyleSheet("""
            QTableWidget {
                background-color: #0F1117;
                color: #DDE8FF;
                gridline-color: #222844;
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
                background-color: #222844;
                color: #DDE8FF;
                padding: 10px;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-radius: 4px;
            }
            QTableWidget::corner {
                background-color: #222844;
                border: none;
            }
        """)
        table_layout.addWidget(self.performance_table)
        
        # Add widgets to dashboard
        dashboard_layout.addWidget(summary_widget)
        dashboard_layout.addWidget(chart_widget)
        dashboard_layout.addWidget(table_frame)
        
        scroll_area.setWidget(dashboard_widget)
        layout.addWidget(scroll_area)
        
        # Set layout properties
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1117;
            }
        """)
        
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
            
            # Update summary labels with color coding
            self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
            
            gain_loss_color = "#24CDB0" if total_gain_loss >= 0 else "#FF3558"
            gain_loss_text = f"${total_gain_loss:,.2f}"
            self.total_gain_label.setText(f"{gain_loss_text}")
            self.total_gain_label.setStyleSheet(f"font-size: 15px; color: {gain_loss_color}; font-weight: 600;")
            
            gain_loss_pct_color = "#24CDB0" if total_gain_percent >= 0 else "#FF3558"
            self.total_gain_percent_label.setText(f"{total_gain_percent:+.2f}%")
            self.total_gain_percent_label.setStyleSheet(f"font-size: 15px; color: {gain_loss_pct_color}; font-weight: 600;")
            
            self.position_count_label.setText(f"{position_count}")
            self.position_count_label.setStyleSheet("font-size: 15px; color: #5295FF; font-weight: 600;")
            
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
                    if current_price is None:
                        current_price = position.purchase_price
                    market_value = current_price * position.shares
                    cost_basis = position.purchase_price * position.shares
                    gain_loss = market_value - cost_basis
                    
                    labels.append(position.ticker)
                    values.append(market_value)
                
                # Create bar chart with colors - need to create separate bars for each color
                for i, (label, value) in enumerate(zip(labels, values)):
                    current_price = self.portfolio_service.get_current_price(positions[i].ticker)
                    if current_price is None:
                        current_price = positions[i].purchase_price
                    market_value = current_price * positions[i].shares
                    cost_basis = positions[i].purchase_price * positions[i].shares
                    gain_loss = market_value - cost_basis
                    
                    bar_color = "#24CDB0" if gain_loss > 0 else "#FF3558"
                    
                    bar_chart = pg.BarGraphItem(
                        x=[i],
                        height=[value],
                        width=0.6,
                        brush=bar_color
                    )
                    self.chart_widget.addItem(bar_chart)
                
                # Set labels
                self.chart_widget.getPlotItem().getAxis('bottom').setTicks([list(enumerate(labels))])
                self.chart_widget.getPlotItem().getAxis('bottom').setLabel('Assets', color="#7488B8")
                
        except Exception as e:
            import traceback
            print(f"Error updating chart: {e}")
            traceback.print_exc()
    
    def calculate_cagr(self, start_value, end_value, years):
        """Calculate CAGR from start and end values and time period."""
        if years <= 0 or start_value <= 0:
            return 0
        return (end_value / start_value) ** (1 / years) - 1
    
    def update_performance_table(self, positions):
        """Update the performance table."""
        try:
            # Clear existing rows
            self.performance_table.setRowCount(0)
            
            # Get current date for CAGR calculation
            current_date = datetime.now()
            
            # Add rows
            for i, position in enumerate(positions):
                self.performance_table.insertRow(i)
                
                # Get current data
                current_price = self.portfolio_service.get_current_price(position.ticker)
                if current_price is None:
                    current_price = position.purchase_price
                
                market_value = current_price * position.shares
                cost_basis = position.purchase_price * position.shares
                gain_loss = market_value - cost_basis
                gain_percent = (gain_loss / cost_basis) * 100 if cost_basis != 0 else 0
                
                # Calculate CAGR
                purchase_date = position.purchase_date
                if purchase_date:
                    # Convert date to datetime for subtraction
                    purchase_datetime = datetime.combine(purchase_date, datetime.min.time())
                    days_held = (current_date - purchase_datetime).days
                    years_held = days_held / 365.25
                    cagr = self.calculate_cagr(cost_basis, market_value, years_held)
                else:
                    cagr = 0
                
                # Set item data
                ticker_item = QTableWidgetItem(position.ticker)
                company_item = QTableWidgetItem(position.company_name)
                shares_item = QTableWidgetItem(str(position.shares))
                value_item = QTableWidgetItem(f"${market_value:,.2f}")
                gain_percent_str = f"{gain_percent:+.2f}%"
                gain_item = QTableWidgetItem(gain_percent_str)
                cagr_str = f"{cagr:+.2%}"
                cagr_item = QTableWidgetItem(cagr_str)
                
                self.performance_table.setItem(i, 0, ticker_item)
                self.performance_table.setItem(i, 1, company_item)
                self.performance_table.setItem(i, 2, shares_item)
                self.performance_table.setItem(i, 3, value_item)
                self.performance_table.setItem(i, 4, gain_item)
                self.performance_table.setItem(i, 5, cagr_item)
                
                # Color code based on gain/loss
                gain_loss_color = "#24CDB0" if gain_loss > 0 else "#FF3558"
                
                gain_item.setForeground(QColor(gain_loss_color))
                cagr_item.setForeground(QColor(gain_loss_color))
                
                # Set font weight for key columns
                gain_item.setFont(self.performance_table.font())
                gain_item.setFont(self.performance_table.font())
                
        except Exception as e:
            import traceback
            print(f"Error updating performance table: {e}")
            traceback.print_exc()