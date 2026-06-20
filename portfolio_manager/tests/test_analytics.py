"""
Test the portfolio analytics functionality
"""

import unittest
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.portfolio_analytics import PortfolioAnalytics, format_currency, format_percentage
from services.portfolio_service import PortfolioService

class TestPortfolioAnalytics(unittest.TestCase):
    """Test portfolio analytics functionality."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        self.assertEqual(format_currency(1234.56), "$1,234.56")
        self.assertEqual(format_currency(0), "$0.00")
        self.assertEqual(format_currency(1000000), "$1,000,000.00")
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        self.assertEqual(format_percentage(5.678), "+5.68%")
        self.assertEqual(format_percentage(-5.678), "-5.68%")
        self.assertEqual(format_percentage(0), "+0.00%")

if __name__ == "__main__":
    unittest.main()