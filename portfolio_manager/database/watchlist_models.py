"""
Watchlist database models for Portfolio Manager.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

WatchlistBase = declarative_base()


class WatchlistItem(WatchlistBase):
    """A single stock on the user's watchlist."""

    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    company_name = Column(String(255), nullable=True)

    # Price recorded when the user adds the item — the "entry" reference point
    entry_price = Column(Float, nullable=False)
    entry_date = Column(Date, nullable=False)

    # Optional fields
    shares_hypothetical = Column(Float, nullable=True)   # how many shares they'd buy
    target_price = Column(Float, nullable=True)          # price target

    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WatchlistItem(id={self.id}, ticker='{self.ticker}')>"
