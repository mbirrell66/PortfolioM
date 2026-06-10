"""
Portfolio Optimization Tab for Portfolio Manager
"""
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                              QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, 
                              QTabWidget, QScrollArea)
from PySide6.QtCore import Qt
from services.portfolio_optimizer import PortfolioOptimizer
from services.portfolio_service import PortfolioService
import pandas as pd
import numpy as np

class PortfolioOptimizationTab(QWidget):
    """Portfolio optimization tab showing various optimization algorithms."""
    
    def __init__(self, portfolio_service: PortfolioService):
        """Initialize portfolio optimization tab."""
        super().__init__()
        self.portfolio_service = portfolio_service
        self.optimizer = PortfolioOptimizer(portfolio_service)
        self.init_ui()
        self.load_portfolio_data()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Main layout with tabs for different optimization methods
        self.tabs = QTabWidget()
        
        # Mean-Variance Optimization tab
        self.mv_tab = self.create_mean_variance_tab()
        self.tabs.addTab(self.mv_tab, "Mean-Variance")
        
        # Risk Parity Optimization tab
        self.rp_tab = self.create_risk_parity_tab()
        self.tabs.addTab(self.rp_tab, "Risk Parity")
        
        # Efficient Frontier tab
        self.ef_tab = self.create_efficient_frontier_tab()
        self.tabs.addTab(self.ef_tab, "Efficient Frontier")
        
        layout.addWidget(self.tabs)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_portfolio_data)
        layout.addWidget(refresh_btn)
    
    def create_mean_variance_tab(self):
        """Create Mean-Variance optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Optimization Parameters")
        input_layout = QFormLayout(input_group)
        
        self.risk_free_rate_spin = QDoubleSpinBox()
        self.risk_free_rate_spin.setRange(0, 1)
        self.risk_free_rate_spin.setDecimals(4)
        self.risk_free_rate_spin.setValue(0.02)
        input_layout.addRow("Risk-Free Rate:", self.risk_free_rate_spin)
        
        # Optimization results
        results_group = QGroupBox("Optimization Results")
        results_layout = QFormLayout(results_group)
        
        self.mv_return_label = QLabel("N/A")
        self.mv_risk_label = QLabel("N/A")
        self.mv_sharpe_label = QLabel("N/A")
        
        results_layout.addRow("Expected Return:", self.mv_return_label)
        results_layout.addRow("Portfolio Risk:", self.mv_risk_label)
        results_layout.addRow("Sharpe Ratio:", self.mv_sharpe_label)
        
        # Results table
        self.mv_results_table = QTableWidget(0, 2)
        self.mv_results_table.setHorizontalHeaderLabels(["Asset", "Weight"])
        self.mv_results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(input_group)
        layout.addWidget(results_group)
        layout.addWidget(self.mv_results_table)
        
        # Optimize button
        optimize_btn = QPushButton("Run Mean-Variance Optimization")
        optimize_btn.clicked.connect(self.run_mean_variance_optimization)
        layout.addWidget(optimize_btn)
        
        return tab
    
    def create_risk_parity_tab(self):
        """Create Risk Parity optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Risk parity results
        results_group = QGroupBox("Risk Parity Results")
        results_layout = QFormLayout(results_group)
        
        self.rp_risk_label = QLabel("N/A")
        
        results_layout.addRow("Portfolio Risk:", self.rp_risk_label)
        
        # Risk contributions table
        self.rp_contributions_table = QTableWidget(0, 2)
        self.rp_contributions_table.setHorizontalHeaderLabels(["Asset", "Risk Contribution"])
        self.rp_contributions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(results_group)
        layout.addWidget(self.rp_contributions_table)
        
        # Optimize button
        optimize_btn = QPushButton("Run Risk Parity Optimization")
        optimize_btn.clicked.connect(self.run_risk_parity_optimization)
        layout.addWidget(optimize_btn)
        
        return tab
    
    def create_efficient_frontier_tab(self):
        """Create Efficient Frontier tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Efficient Frontier Parameters")
        input_layout = QFormLayout(input_group)
        
        self.portfolio_count_spin = QSpinBox()
        self.portfolio_count_spin.setRange(10, 1000)
        self.portfolio_count_spin.setValue(100)
        input_layout.addRow("Number of Portfolios:", self.portfolio_count_spin)
        
        # Frontier chart placeholder (would be implemented with pyqtgraph)
        chart_label = QLabel("Efficient Frontier Visualization (coming soon)")
        chart_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(input_group)
        layout.addWidget(chart_label)
        
        # Optimize button
        optimize_btn = QPushButton("Generate Efficient Frontier")
        optimize_btn.clicked.connect(self.generate_efficient_frontier)
        layout.addWidget(optimize_btn)
        
        return tab
    
    def load_portfolio_data(self):
        """Load portfolio data for optimization."""
        try:
            # Get current portfolio positions
            positions = self.portfolio_service.get_positions()
            if not positions:
                return
            
            # Get ticker data
            tickers = [position.ticker for position in positions]
            
            # Set up results tables
            self.update_mv_results_table(tickers)
            self.update_rp_contributions_table(tickers)
            
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
    
    def update_mv_results_table(self, tickers):
        """Update Mean-Variance optimization results table."""
        self.mv_results_table.setRowCount(len(tickers))
        for i, ticker in enumerate(tickers):
            self.mv_results_table.setItem(i, 0, QTableWidgetItem(ticker))
            self.mv_results_table.setItem(i, 1, QTableWidgetItem("0.00"))
    
    def update_rp_contributions_table(self, tickers):
        """Update Risk Parity contributions table."""
        self.rp_contributions_table.setRowCount(len(tickers))
        for i, ticker in enumerate(tickers):
            self.rp_contributions_table.setItem(i, 0, QTableWidgetItem(ticker))
            self.rp_contributions_table.setItem(i, 1, QTableWidgetItem("0.00%"))
    
    def run_mean_variance_optimization(self):
        """Run Mean-Variance optimization."""
        try:
            # Get current portfolio positions and their weights
            positions = self.portfolio_service.get_positions()
            if not positions:
                return
            
            # Simplified example - in a real implementation, you'd fetch historical returns
            tickers = [position.ticker for position in positions]
            weights = [1.0/len(tickers)] * len(tickers)  # Equal weights
            
            # Create a mock returns DataFrame for demonstration
            returns_data = {}
            for ticker in tickers:
                # Generate mock returns (in reality, fetch from yfinance or database)
                returns_data[ticker] = np.random.normal(0.08, 0.15, 252)  # 8% return, 15% volatility
            
            returns_df = pd.DataFrame(returns_data)
            
            # Run optimization
            result = self.optimizer.mean_variance_optimization(
                weights, 
                returns_df, 
                risk_free_rate=self.risk_free_rate_spin.value()
            )
            
            # Update UI with results
            if result['success']:
                self.mv_return_label.setText(f"{result['return']:.4f}")
                self.mv_risk_label.setText(f"{result['risk']:.4f}")
                self.mv_sharpe_label.setText(f"{result['sharpe_ratio']:.4f}")
                
                # Update weights table
                for i, weight in enumerate(result['weights']):
                    if i < self.mv_results_table.rowCount():
                        self.mv_results_table.setItem(i, 1, QTableWidgetItem(f"{weight:.4f}"))
            else:
                self.mv_return_label.setText("Error")
                self.mv_risk_label.setText("Error")
                self.mv_sharpe_label.setText("Error")
                
        except Exception as e:
            print(f"Error in Mean-Variance optimization: {e}")
    
    def run_risk_parity_optimization(self):
        """Run Risk Parity optimization."""
        try:
            # Get current portfolio positions and their weights
            positions = self.portfolio_service.get_positions()
            if not positions:
                return
            
            # Simplified example - in a real implementation, you'd fetch historical returns
            tickers = [position.ticker for position in positions]
            
            # Create a mock returns DataFrame for demonstration
            returns_data = {}
            for ticker in tickers:
                # Generate mock returns (in reality, fetch from yfinance or database)
                returns_data[ticker] = np.random.normal(0.08, 0.15, 252)  # 8% return, 15% volatility
            
            returns_df = pd.DataFrame(returns_data)
            
            # Run optimization
            result = self.optimizer.risk_parity_optimization(returns_df)
            
            # Update UI with results
            if result['success']:
                self.rp_risk_label.setText(f"{result['risk']:.4f}")
                
                # Update risk contributions table
                for i, contribution in enumerate(result['risk_contributions']):
                    if i < self.rp_contributions_table.rowCount():
                        self.rp_contributions_table.setItem(i, 1, QTableWidgetItem(f"{contribution:.4f}"))
            else:
                self.rp_risk_label.setText("Error")
                
        except Exception as e:
            print(f"Error in Risk Parity optimization: {e}")
    
    def generate_efficient_frontier(self):
        """Generate efficient frontier."""
        try:
            # Get current portfolio positions
            positions = self.portfolio_service.get_positions()
            if not positions:
                return
            
            # Simplified example - in a real implementation, you'd fetch historical returns
            tickers = [position.ticker for position in positions]
            
            # Create a mock returns DataFrame for demonstration
            returns_data = {}
            for ticker in tickers:
                # Generate mock returns (in reality, fetch from yfinance or database)
                returns_data[ticker] = np.random.normal(0.08, 0.15, 252)  # 8% return, 15% volatility
            
            returns_df = pd.DataFrame(returns_data)
            
            # Generate efficient frontier
            frontier_points = self.optimizer.efficient_frontier(
                returns_df, 
                num_portfolios=self.portfolio_count_spin.value()
            )
            
            # In a real implementation, this would display the frontier chart
            # For now, we'll just show the number of points generated
            print(f"Generated {len(frontier_points)} efficient frontier points")
            
        except Exception as e:
            print(f"Error generating efficient frontier: {e}")
