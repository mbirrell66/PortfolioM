"""
Database initialization and connection for Portfolio Manager
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base
from .personal_finance_models import Base as PersonalFinanceBase
from .tax_models import Base as TaxBase
from .watchlist_models import WatchlistBase

# Resolve data directory correctly whether running from source or as a
# PyInstaller bundle.  When frozen, __file__ points inside _internal/ and
# is not writable; use the directory containing the .exe instead.
if getattr(sys, 'frozen', False):
    DATA_DIR = Path(sys.executable).parent / "data"
else:
    DATA_DIR = Path(__file__).parent.parent / "data"

DB_PATH = DATA_DIR / "portfolio.db"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database by creating tables."""
    # Import all models to ensure foreign key relationships are properly set up
    from .models import Position, Dividend, DividendEvent, StockSplit, PortfolioSnapshot
    from .personal_finance_models import (
        IncomeCategory, ExpenseCategory, Income, Expense, Budget,
        FinancialGoal
    )
    from .tax_models import (
        TaxCategory, TaxEvent, CapitalGainsEvent, TaxReturn
    )

    Base.metadata.create_all(engine)
    PersonalFinanceBase.metadata.create_all(engine)
    TaxBase.metadata.create_all(engine)
    WatchlistBase.metadata.create_all(engine)

    # Non-destructive migration: add new columns to positions if they don't exist
    _migrate_positions_table()


def _migrate_positions_table():
    """Add sell/commission columns to positions table if not already present."""
    new_columns = [
        ('buy_commission',  'FLOAT DEFAULT 0.0'),
        ('sell_date',       'DATE'),
        ('sell_price',      'FLOAT'),
        ('sell_commission', 'FLOAT DEFAULT 0.0'),
    ]
    try:
        insp = inspect(engine)
        existing = {c['name'] for c in insp.get_columns('positions')}
        with engine.connect() as conn:
            for col_name, col_def in new_columns:
                if col_name not in existing:
                    conn.execute(text(
                        f'ALTER TABLE positions ADD COLUMN {col_name} {col_def}'
                    ))
            conn.commit()
    except Exception as e:
        # Table may not exist yet (first run) — create_all handles it
        print(f"Migration note: {e}")


def get_db():
    """Generator-style session factory for use with next(get_db())."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
