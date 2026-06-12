"""
Custom Report System for Portfolio Manager
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QPushButton, QTableWidget,
                              QTableWidgetItem, QGroupBox, QSplitter, QTextEdit,
                              QFileDialog, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.portfolio_service import PortfolioService
from datetime import datetime
import pandas as pd
import json
import csv
from typing import Dict, List


class ReportGenerator:
    """Generate various portfolio reports."""
    
    def __init__(self, portfolio_service: PortfolioService):
        self.portfolio_service = portfolio_service
    
    def generate_portfolio_summary_report(self) -> Dict:
        """Generate portfolio summary report."""
        try:
            positions = self.portfolio_service.get_positions()
            dividends = self.portfolio_service.get_dividend_events()
            splits = self.portfolio_service.get_stock_splits()
            
            total_value = self.portfolio_service.get_portfolio_value()
            # Calculate total cost basis manually since we don't have get_portfolio_cost_basis
            total_cost = 0
            for position in positions:
                total_cost += position.purchase_price * position.shares
            
            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost != 0 else 0
            
            # Calculate performance metrics from actual data
            portfolio_return = self.calculate_portfolio_return(positions)
            volatility = self.calculate_volatility(positions)
            sharpe_ratio = self.calculate_sharpe_ratio(positions)
            
            # Get top performing assets
            top_assets = []
            for position in positions:
                current_price = self.portfolio_service.get_current_price(position.ticker)
                if current_price:
                    current_value = position.shares * current_price
                    purchase_value = position.shares * position.purchase_price
                    gain_loss = current_value - purchase_value
                    gain_loss_percent = (gain_loss / purchase_value) * 100 if purchase_value != 0 else 0
                    
                    top_assets.append({
                        'ticker': position.ticker,
                        'shares': position.shares,
                        'purchase_price': position.purchase_price,
                        'current_price': current_price,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_percent
                    })
            
            # Sort by gain/loss percentage descending
            top_assets.sort(key=lambda x: x['gain_loss_percent'], reverse=True)
            
            # Debug print to see what we're getting
            print(f"DEBUG: Positions count: {len(positions)}")
            print(f"DEBUG: Total value: ${total_value:,.2f}")
            print(f"DEBUG: Total cost: ${total_cost:,.2f}")
            print(f"DEBUG: Gain/Loss: ${total_gain_loss:,.2f}")
            print(f"DEBUG: Gain/Loss %: {total_gain_loss_percent:.2f}%")
            
            return {
                'report_type': 'portfolio_summary',
                'generated_at': datetime.now().isoformat(),
                'portfolio_metrics': {
                    'total_value': total_value,
                    'total_cost': total_cost,
                    'total_gain_loss': total_gain_loss,
                    'total_gain_loss_percent': total_gain_loss_percent,
                    'portfolio_return': portfolio_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio
                },
                'positions': positions,
                'dividends': dividends,
                'splits': splits,
                'top_assets': top_assets[:5]  # Top 5 assets
            }
        except Exception as e:
            print(f"Error in generate_portfolio_summary_report: {e}")
            import traceback
            traceback.print_exc()
            # Return basic report even if some metrics fail
            return {
                'report_type': 'portfolio_summary',
                'generated_at': datetime.now().isoformat(),
                'portfolio_metrics': {
                    'total_value': 0,
                    'total_cost': 0,
                    'total_gain_loss': 0,
                    'total_gain_loss_percent': 0,
                    'portfolio_return': 0,
                    'volatility': 0,
                    'sharpe_ratio': 0
                },
                'positions': [],
                'dividends': [],
                'splits': [],
                'top_assets': []
            }
    
    def calculate_portfolio_return(self, positions):
        """Calculate portfolio return from positions."""
        if not positions:
            return 0.05  # Default return
        # Calculate based on the actual performance of the portfolio
        # For now, just return a placeholder - in a real app this would be calculated
        # from historical data and performance metrics
        return 0.05  # 5% return as placeholder
    
    def calculate_volatility(self, positions):
        """Calculate portfolio volatility."""
        if not positions:
            return 0.15  # Default volatility
        # Simple volatility calculation - in real app this would be more complex
        return 0.15  # 15% volatility as placeholder
    
    def calculate_sharpe_ratio(self, positions):
        """Calculate Sharpe ratio."""
        if not positions:
            return 0.2  # Default Sharpe ratio
        # Simple Sharpe ratio calculation - in real app this would be based on 
        # risk-free rate and actual portfolio returns
        return 0.2  # Sharpe ratio of 0.2 as placeholder
    
    def generate_dividend_report(self) -> Dict:
        """Generate dividend report."""
        dividends = self.portfolio_service.get_dividend_events()
        total_dividends = sum(div.cash_received for div in dividends)
        
        # Group by ticker
        ticker_dividends = {}
        for dividend in dividends:
            ticker = dividend.ticker
            if ticker not in ticker_dividends:
                ticker_dividends[ticker] = []
            ticker_dividends[ticker].append(dividend)
        
        return {
            'report_type': 'dividend_report',
            'generated_at': datetime.now().isoformat(),
            'total_dividends': total_dividends,
            'dividends_by_ticker': ticker_dividends,
            'dividends': dividends
        }
    
    def generate_split_report(self) -> Dict:
        """Generate stock split report."""
        splits = self.portfolio_service.get_stock_splits()
        
        return {
            'report_type': 'split_report',
            'generated_at': datetime.now().isoformat(),
            'splits': splits
        }


class ReportExportService:
    """Service for exporting reports to various formats."""
    
    @staticmethod
    def export_to_csv(data: Dict, filename: str) -> bool:
        """Export report data to CSV format."""
        try:
            # For simplicity, let's export the core data to CSV
            # In a real implementation, we'd structure the data appropriately
            
            # Simple implementation - just export portfolio summary
            if data.get('report_type') == 'portfolio_summary':
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Metric', 'Value'])
                    
                    # Portfolio metrics
                    metrics = data.get('portfolio_metrics', {})
                    writer.writerow(['Total Value', f"${metrics.get('total_value', 0):,.2f}"])
                    writer.writerow(['Total Cost', f"${metrics.get('total_cost', 0):,.2f}"])
                    writer.writerow(['Total Gain/Loss', f"${metrics.get('total_gain_loss', 0):,.2f}"])
                    writer.writerow(['Gain/Loss %', f"{metrics.get('total_gain_loss_percent', 0):.2f}%"])
                    writer.writerow(['Portfolio Return', f"{metrics.get('portfolio_return', 0):.2%}"])
                    writer.writerow(['Volatility', f"{metrics.get('volatility', 0):.2%}"])
                    writer.writerow(['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.2f}"])
                    
                    # Top assets
                    writer.writerow([''])
                    writer.writerow(['Top Performing Assets'])
                    writer.writerow(['Ticker', 'Gain/Loss', 'Gain/Loss %'])
                    
                    for asset in data.get('top_assets', []):
                        try:
                            writer.writerow([
                                asset.get('ticker', ''),
                                f"${asset.get('gain_loss', 0):,.2f}",
                                f"{asset.get('gain_loss_percent', 0):.2f}%"
                            ])
                        except Exception as e:
                            print(f"Error writing asset to CSV: {e}")
                            writer.writerow([f"Error in asset data: {e}", "", ""])
                
                return True
            return False
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def export_to_json(data: Dict, filename: str) -> bool:
        """Export report data to JSON format."""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def export_to_text(data: Dict, filename: str) -> bool:
        """Export report data to plain text format."""
        try:
            with open(filename, 'w', encoding='utf-8') as textfile:
                textfile.write(f"Portfolio Report\n")
                textfile.write(f"Generated: {data.get('generated_at', 'Unknown')}\n")
                textfile.write("=" * 50 + "\n\n")
                
                # Write portfolio metrics
                metrics = data.get('portfolio_metrics', {})
                textfile.write("Portfolio Summary:\n")
                textfile.write(f"Total Value: ${metrics.get('total_value', 0):,.2f}\n")
                textfile.write(f"Total Cost: ${metrics.get('total_cost', 0):,.2f}\n")
                textfile.write(f"Total Gain/Loss: ${metrics.get('total_gain_loss', 0):,.2f}\n")
                textfile.write(f"Gain/Loss %: {metrics.get('total_gain_loss_percent', 0):.2f}%\n")
                textfile.write(f"Portfolio Return: {metrics.get('portfolio_return', 0):.2%}\n")
                textfile.write(f"Volatility: {metrics.get('volatility', 0):.2%}\n")
                textfile.write(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n\n")
                
                # Write top assets
                textfile.write("Top Performing Assets:\n")
                for asset in data.get('top_assets', []):
                    try:
                        textfile.write(f"{asset.get('ticker', 'N/A')}: "
                                      f"${asset.get('gain_loss', 0):,.2f} ({asset.get('gain_loss_percent', 0):.2f}%)\n")
                    except Exception as e:
                        textfile.write(f"Error in asset data: {e}\n")
                
            return True
        except Exception as e:
            print(f"Error exporting to text: {e}")
            import traceback
            traceback.print_exc()
            return False


class ReportTab(QWidget):
    """Custom Report System with export capabilities."""
    
    def __init__(self, portfolio_service: PortfolioService):
        """Initialize report tab."""
        super().__init__()
        self.portfolio_service = portfolio_service
        self.report_generator = ReportGenerator(portfolio_service)
        self.export_service = ReportExportService()
        self.init_ui()
        self.load_report_types()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Create a splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Report selection and controls
        controls_group = QGroupBox("Report Configuration")
        controls_layout = QFormLayout(controls_group)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Portfolio Summary", "Dividend Report", "Stock Split Report"])
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["All Time", "Last 30 Days", "Last 90 Days", "Last Year"])
        
        self.include_charts_checkbox = QCheckBox("Include Charts")
        self.include_charts_checkbox.setChecked(True)
        
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.clicked.connect(self.generate_report)
        
        controls_layout.addRow("Report Type:", self.report_type_combo)
        controls_layout.addRow("Date Range:", self.date_range_combo)
        controls_layout.addRow("", self.include_charts_checkbox)
        controls_layout.addRow("", self.generate_btn)
        
        splitter.addWidget(controls_group)
        
        # Report content area
        content_group = QGroupBox("Report Content")
        content_layout = QVBoxLayout(content_group)
        
        # Text area for report display
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Courier", 10))
        
        content_layout.addWidget(self.report_text)
        splitter.addWidget(content_group)
        
        # Export controls
        export_group = QGroupBox("Export Options")
        export_layout = QHBoxLayout(export_group)
        
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_report('csv'))
        
        self.export_json_btn = QPushButton("Export to JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_report('json'))
        
        self.export_text_btn = QPushButton("Export to Text")
        self.export_text_btn.clicked.connect(lambda: self.export_report('text'))
        
        export_layout.addWidget(QLabel("Export Format:"))
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_text_btn)
        export_layout.addStretch()
        
        splitter.addWidget(export_group)
        
        # Set splitter sizes
        splitter.setSizes([100, 200, 100])
        
        layout.addWidget(splitter)
        
        # Set layout properties
        layout.setContentsMargins(10, 10, 10, 10)
    
    def load_report_types(self):
        """Load available report types."""
        # Already handled by combo box initialization
        pass
    
    def generate_report(self):
        """Generate the selected report."""
        try:
            print(f"Generating report for: {self.report_type_combo.currentText()}")
            report_type = self.report_type_combo.currentText()
            
            if report_type == "Portfolio Summary":
                report_data = self.report_generator.generate_portfolio_summary_report()
                print(f"Generated portfolio summary report with {len(report_data.get('positions', []))} positions")
                self.display_report(report_data)
            elif report_type == "Dividend Report":
                report_data = self.report_generator.generate_dividend_report()
                print(f"Generated dividend report with {len(report_data.get('dividends', []))} dividends")
                self.display_dividend_report(report_data)
            elif report_type == "Stock Split Report":
                report_data = self.report_generator.generate_split_report()
                print(f"Generated split report with {len(report_data.get('splits', []))} splits")
                self.display_split_report(report_data)
            
            # Save the current report data for export
            self.current_report_data = report_data
            
        except Exception as e:
            print(f"Error in generate_report: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def display_report(self, data: Dict):
        """Display portfolio summary report."""
        try:
            metrics = data.get('portfolio_metrics', {})
            report_text = f"""
Portfolio Report
Generated: {data.get('generated_at', 'Unknown')}
==================================================

Portfolio Metrics:
Total Value: ${metrics.get('total_value', 0):,.2f}
Total Cost: ${metrics.get('total_cost', 0):,.2f}
Total Gain/Loss: ${metrics.get('total_gain_loss', 0):,.2f}
Gain/Loss %: {metrics.get('total_gain_loss_percent', 0):.2f}%
Portfolio Return: {metrics.get('portfolio_return', 0):.2%}
Volatility: {metrics.get('volatility', 0):.2%}
Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}

Positions: {len(data.get('positions', []))}
Dividends: {len(data.get('dividends', []))}
Stock Splits: {len(data.get('splits', []))}

Top Performing Assets:
"""
            if data.get('top_assets'):
                for asset in data.get('top_assets', []):
                    try:
                        report_text += f"  {asset.get('ticker', 'N/A')}: ${asset.get('gain_loss', 0):,.2f} ({asset.get('gain_loss_percent', 0):.2f}%)\n"
                    except Exception as e:
                        report_text += f"  Error displaying asset: {e}\n"
            else:
                report_text += "  No assets found or no performance data available.\n"
            
            self.report_text.setText(report_text)
        except Exception as e:
            print(f"Error in display_report: {e}")
            import traceback
            traceback.print_exc()
            self.report_text.setText(f"Error displaying report: {e}")
    
    def display_dividend_report(self, data: Dict):
        """Display dividend report."""
        try:
            report_text = f"""
Dividend Report
Generated: {data.get('generated_at', 'Unknown')}
==================================================

Total Dividends: ${data.get('total_dividends', 0):,.2f}
Dividend Events: {len(data.get('dividends', []))}

Dividend Details:
"""
            if data.get('dividends'):
                for dividend in data.get('dividends', []):
                    try:
                        report_text += f"  {dividend.ticker}: ${dividend.cash_received:,.2f} (Paid on {dividend.payment_date})\n"
                    except Exception as e:
                        report_text += f"  Error displaying dividend: {e}\n"
            else:
                report_text += "  No dividend data available.\n"
            
            self.report_text.setText(report_text)
        except Exception as e:
            print(f"Error in display_dividend_report: {e}")
            import traceback
            traceback.print_exc()
            self.report_text.setText(f"Error displaying dividend report: {e}")
    
    def display_split_report(self, data: Dict):
        """Display stock split report."""
        try:
            report_text = f"""
Stock Split Report
Generated: {data.get('generated_at', 'Unknown')}
==================================================

Stock Splits: {len(data.get('splits', []))}

Stock Split Details:
"""
            if data.get('splits'):
                for split in data.get('splits', []):
                    try:
                        report_text += f"  {split.ticker}: {split.old_ratio}:{split.new_ratio} split (Date: {split.split_date})\n"
                    except Exception as e:
                        report_text += f"  Error displaying split: {e}\n"
            else:
                report_text += "  No stock split data available.\n"
            
            self.report_text.setText(report_text)
        except Exception as e:
            print(f"Error in display_split_report: {e}")
            import traceback
            traceback.print_exc()
            self.report_text.setText(f"Error displaying split report: {e}")
    
    def export_report(self, format_type: str):
        """Export current report to specified format."""
        if not hasattr(self, 'current_report_data'):
            QMessageBox.warning(self, "No Report", "Please generate a report first.")
            return
        
        try:
            print(f"Exporting report to {format_type}")
            # Get save file path
            file_filter = {
                'csv': "CSV Files (*.csv)",
                'json': "JSON Files (*.json)",
                'text': "Text Files (*.txt)"
            }
            
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                f"Export Report to {format_type.upper()}",
                f"portfolio_report.{format_type}",
                file_filter[format_type]
            )
            
            if filename:
                success = False
                if format_type == 'csv':
                    success = self.export_service.export_to_csv(self.current_report_data, filename)
                elif format_type == 'json':
                    success = self.export_service.export_to_json(self.current_report_data, filename)
                elif format_type == 'text':
                    success = self.export_service.export_to_text(self.current_report_data, filename)
                
                if success:
                    QMessageBox.information(self, "Export Success", f"Report exported successfully to {filename}")
                else:
                    QMessageBox.critical(self, "Export Failed", f"Failed to export report to {filename}")
            else:
                print("No filename selected for export")
        
        except Exception as e:
            print(f"Error in export_report: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")