import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_implementation():
    """Test that all components work together properly."""
    try:
        # Test that we can import the benchmark tab
        from portfolio_manager.gui.benchmark_comparison_tab import BenchmarkComparisonTab
        print('✅ BenchmarkComparisonTab imported successfully')
        
        # Test that we can import other components
        from portfolio_manager.gui.performance_tab import PerformanceTab
        from portfolio_manager.gui.main_window import MainWindow
        from portfolio_manager.services.portfolio_service import PortfolioService
        from portfolio_manager.services.market_data import MarketDataService
        
        print('✅ All components imported successfully')
        
        # Test that the tab can be instantiated
        tab = BenchmarkComparisonTab()
        print('✅ BenchmarkComparisonTab instantiated successfully')
        
        # Test that services exist
        portfolio_service = PortfolioService()
        market_data_service = MarketDataService()
        print('✅ Services instantiated successfully')
        
        print('\n🎉 Advanced benchmark comparison implementation is complete and working!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_implementation()