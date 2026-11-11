"""Shared test setup.

Every test gets a throwaway SQLite file in a temp folder. Nothing here opens
data/portfolio.db, and nothing touches the network.
"""
import sys
import types
from pathlib import Path

import pytest

PKG_DIR = Path(__file__).resolve().parent.parent
# The code base imports modules two ways ("database.x" and
# "portfolio_manager.database.x"), so both roots have to be importable.
for _p in (str(PKG_DIR), str(PKG_DIR.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import yfinance  # noqa: F401
except ImportError:  # tests never fetch prices, so a stub is enough
    sys.modules["yfinance"] = types.ModuleType("yfinance")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session_factory(tmp_path, monkeypatch):
    """Temp database wired into the portfolio, options and finance services."""
    import database.database as dbmod
    import services.portfolio_service as portfolio_mod
    import services.options_service as options_mod
    from database.models import Base
    from database.personal_finance_models import Base as FinanceBase
    from database.options_models import OptionsBase

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    for base in (Base, FinanceBase, OptionsBase):
        base.metadata.create_all(engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(dbmod, "SessionLocal", factory)
    monkeypatch.setattr(portfolio_mod, "SessionLocal", factory)
    monkeypatch.setattr(options_mod, "SessionLocal", factory)
    yield factory
    engine.dispose()


@pytest.fixture
def tax_service(tmp_path):
    """TaxService on its own temp database."""
    from portfolio_manager.database.tax_models import Base as TaxBase
    from portfolio_manager.services.tax_service import TaxService

    engine = create_engine(f"sqlite:///{tmp_path / 'tax.db'}")
    TaxBase.metadata.create_all(engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    svc = TaxService()
    svc.get_db = get_db
    yield svc
    engine.dispose()
