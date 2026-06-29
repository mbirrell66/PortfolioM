"""
Simple test to verify benchmark comparison tab functionality
"""
import sys
sys.path.insert(0, 'portfolio_manager')

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

from database.database import init_database
db_path = init_database()

from services.portfolio_service import PortfolioService
from services.market_data import MarketDataService
from gui.benchmark_comparison_tab import BenchmarkComparisonTab

portfolio_service = PortfolioService()
market_data_service = MarketDataService()

print(f"Creating BenchmarkComparisonTab...")
print(f"Portfolio service: {portfolio_service}")
print(f"Market data service: {market_data_service}")

benchmark_tab = BenchmarkComparisonTab(portfolio_service, market_data_service)

print(f"Tab created: {benchmark_tab}")
print(f"Has compare_btn: {hasattr(benchmark_tab, 'compare_btn')}")
print(f"Has on_compare_clicked: {hasattr(benchmark_tab, 'on_compare_clicked')}")

if hasattr(benchmark_tab, 'compare_btn'):
    print(f"Compare button: {benchmark_tab.compare_btn}")
    print(f"Compare button connected signals: {benchmark_tab.compare_btn.clicked}")

print("\nTest complete!")
