"""
Advanced Benchmark Comparison Tab for Portfolio Manager
"""

import sys
import os

# Add project root to path to ensure proper imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QPushButton, QTableWidget,
                              QTableWidgetItem, QGroupBox, QSplitter)
from PySide6.QtCore import Qt
import pyqtgraph as pg
import logging

logger = logging.getLogger(__name__)

class BenchmarkComparisonTab(QWidget):
    """Advanced benchmark comparison tab with charts and detailed analytics."""
    
    def __init__(self):
        """Initialize benchmark comparison tab."""
        super().__init__()
        self.init_ui()
        # Don't load data immediately - wait for user to click Compare button
        # self.load_benchmark_data()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Create a splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Portfolio vs Benchmark comparison chart
        chart_group = QGroupBox("Portfolio vs Benchmark Comparison")
        chart_layout = QVBoxLayout(chart_group)
        
        # Create the chart widget
        self.chart_widget = pg.PlotWidget()
        self.chart_widget.setTitle("Portfolio Performance vs Benchmark")
        self.chart_widget.setLabel('left', 'Value ($)')
        self.chart_widget.setLabel('bottom', 'Time')
        
        chart_layout.addWidget(self.chart_widget)
        splitter.addWidget(chart_group)
        
        # Benchmark selection and controls
        controls_group = QGroupBox("Benchmark Selection")
        controls_layout = QHBoxLayout(controls_group)
        
        self.benchmark_combo = QComboBox()
        self.benchmark_combo.addItems(["S&P 500 (^GSPC)", "NASDAQ (^IXIC)", "DOW (^DJI)", "RUSSELL 2000 (^RUT)", "Custom"])
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["1Y", "3Y", "5Y", "10Y", "All Time"])
        
        self.compare_btn = QPushButton("Compare")
        self.compare_btn.clicked.connect(self.load_benchmark_data)
        
        controls_layout.addWidget(QLabel("Benchmark:"))
        controls_layout.addWidget(self.benchmark_combo)
        controls_layout.addWidget(QLabel("Time Period:"))
        controls_layout.addWidget(self.date_range_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.compare_btn)
        
        splitter.addWidget(controls_group)
        
        # Portfolio metrics summary
        summary_group = QGroupBox("Portfolio Metrics")
        summary_layout = QFormLayout(summary_group)
        
        self.portfolio_value_label = QLabel("N/A")
        self.portfolio_return_label = QLabel("N/A")
        self.portfolio_volatility_label = QLabel("N/A")
        self.sharpe_ratio_label = QLabel("N/A")
        
        summary_layout.addRow("Portfolio Value:", self.portfolio_value_label)
        summary_layout.addRow("Return:", self.portfolio_return_label)
        summary_layout.addRow("Volatility:", self.portfolio_volatility_label)
        summary_layout.addRow("Sharpe Ratio:", self.sharpe_ratio_label)
        
        splitter.addWidget(summary_group)
        
        # Benchmark metrics comparison
        benchmark_metrics_group = QGroupBox("Benchmark Comparison")
        benchmark_metrics_layout = QFormLayout(benchmark_metrics_group)
        
        self.benchmark_value_label = QLabel("N/A")
        self.benchmark_return_label = QLabel("N/A")
        self.benchmark_volatility_label = QLabel("N/A")
        self.benchmark_sharpe_label = QLabel("N/A")
        
        benchmark_metrics_layout.addRow("Benchmark Value:", self.benchmark_value_label)
        benchmark_metrics_layout.addRow("Return:", self.benchmark_return_label)
        benchmark_metrics_layout.addRow("Volatility:", self.benchmark_volatility_label)
        benchmark_metrics_layout.addRow("Sharpe Ratio:", self.benchmark_sharpe_label)
        
        splitter.addWidget(benchmark_metrics_group)
        
        # Set splitter sizes
        splitter.setSizes([300, 100, 100, 100])
        
        layout.addWidget(splitter)
        
        # Set layout properties
        layout.setContentsMargins(10, 10, 10, 10)
    
    def load_benchmark_data(self):
        """Load benchmark comparison data and update charts."""
        try:
            # Show a simple placeholder message
            self.portfolio_value_label.setText("$10,000.00")
            self.portfolio_return_label.setText("5.00%")
            self.portfolio_volatility_label.setText("15.00%")
            self.sharpe_ratio_label.setText("0.20")
            
            self.benchmark_value_label.setText("$11,000.00")
            self.benchmark_return_label.setText("7.00%")
            self.benchmark_volatility_label.setText("20.00%")
            self.benchmark_sharpe_label.setText("0.25")
            
            # Update chart
            self.update_comparison_chart()
            
        except Exception as e:
            logger.error(f"Error loading benchmark data: {e}")
            print(f"Error loading benchmark data: {e}")
            # Show error message
            self.portfolio_value_label.setText("Error")
            self.benchmark_value_label.setText("Error")
    
    def get_selected_benchmark(self):
        """Get the selected benchmark ticker."""
        selected_text = self.benchmark_combo.currentText()
        if selected_text == "S&P 500 (^GSPC)":
            return "^GSPC"
        elif selected_text == "NASDAQ (^IXIC)":
            return "^IXIC"
        elif selected_text == "DOW (^DJI)":
            return "^DJI"
        elif selected_text == "RUSSELL 2000 (^RUT)":
            return "^RUT"
        else:
            return "^GSPC"  # Default to S&P 500
    
    def update_comparison_chart(self):
        """Update the comparison chart with portfolio vs benchmark data."""
        try:
            # Clear existing plots
            self.chart_widget.clear()
            
            # Simulate data for demonstration
            import numpy as np
            x_data = np.arange(0, 12, 1)  # 12 months of data
            portfolio_data = [10000, 10500, 11200, 12100, 13500, 14900, 15800, 17200, 18500, 19200, 20100, 21500]
            benchmark_data = [10000, 10300, 10700, 11400, 12000, 12800, 13500, 14200, 14800, 15500, 16200, 17000]
            
            # Create portfolio line
            portfolio_plot = self.chart_widget.plot(x_data, portfolio_data, 
                                                   pen=pg.mkPen('g', width=2), 
                                                   name='Portfolio')
            
            # Create benchmark line
            benchmark_plot = self.chart_widget.plot(x_data, benchmark_data, 
                                                   pen=pg.mkPen('r', width=2), 
                                                   name='Benchmark')
            
            # Add legend
            self.chart_widget.addLegend()
            
        except Exception as e:
            logger.error(f"Error updating chart: {e}")
            print(f"Error updating chart: {e}")