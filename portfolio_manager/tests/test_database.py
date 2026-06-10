"""
Database tests for Portfolio Manager
"""

import unittest
from pathlib import Path
import sys
from datetime import date

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Position, PortfolioSnapshot

class TestDatabase(unittest.TestCase):
    """Test database functionality."""

    def setUp(self):
        """Set up an isolated in-memory database for each test method."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = TestSession()

    def tearDown(self):
        """Clean up after each test method."""
        self.session.close()
        self.engine.dispose()

    def test_position_model(self):
        """Test Position model creation."""
        # Create a position
        position = Position(
            ticker="AAPL",
            company_name="Apple Inc.",
            purchase_date=date(2024, 1, 1),
            purchase_price=150.0,
            shares=100,
            notes="Test position"
        )

        # Add to database
        self.session.add(position)
        self.session.commit()

        # Verify it was saved
        db_position = self.session.query(Position).filter_by(ticker="AAPL").first()
        self.assertIsNotNone(db_position)
        self.assertEqual(db_position.ticker, "AAPL")
        self.assertEqual(db_position.shares, 100)

    def test_portfolio_snapshot_model(self):
        """Test PortfolioSnapshot model creation."""
        # Create a portfolio snapshot
        snapshot = PortfolioSnapshot(
            snapshot_date=date(2024, 1, 1),
            portfolio_value=100000.0,
            benchmark_value=95000.0
        )

        # Add to database
        self.session.add(snapshot)
        self.session.commit()

        # Verify it was saved
        db_snapshot = self.session.query(PortfolioSnapshot).filter_by(
            snapshot_date=date(2024, 1, 1)
        ).first()
        self.assertIsNotNone(db_snapshot)
        self.assertEqual(db_snapshot.portfolio_value, 100000.0)

if __name__ == "__main__":
    unittest.main()
