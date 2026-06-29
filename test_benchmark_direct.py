import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication

# Create QApplication first
app = QApplication(sys.argv)

# Now import and create the benchmark tab
try:
    from portfolio_manager.gui.benchmark_comparison_tab import BenchmarkComparisonTab
    print("Import successful")
    
    tab = BenchmarkComparisonTab()
    print("Tab creation successful")
    
    # Try to show it
    tab.show()
    print("Tab shown successfully")
    
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
