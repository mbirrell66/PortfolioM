"""
Database Models for Portfolio Manager
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Position(Base):
    """Database model for a stock position."""
    
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    company_name = Column(String(255), nullable=True)
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Float, nullable=False)
    shares = Column(Integer, nullable=False)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Position(id={self.id}, ticker='{self.ticker}', shares={self.shares})>"

class Dividend(Base):
    """Database model for dividend payments."""
    
    __tablename__ = 'dividends'
    
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, nullable=False)
    ticker = Column(String(10), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount_per_share = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Dividend(id={self.id}, ticker='{self.ticker}', amount={self.total_amount})>"

class DividendEvent(Base):
    """Database model for dividend events including reinvestment details."""
    
    __tablename__ = 'dividend_events'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    ex_dividend_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=False)
    dividend_per_share = Column(Float, nullable=False)
    shares_owned = Column(Integer, nullable=False)
    cash_received = Column(Float, nullable=False)
    shares_purchased = Column(Integer, nullable=True)
    reinvestment_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StockSplit(Base):
    """Database model for stock splits."""
    
    __tablename__ = 'stock_splits'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    split_date = Column(Date, nullable=False)
    old_ratio = Column(Integer, nullable=False)
    new_ratio = Column(Integer, nullable=False)

class PortfolioSnapshot(Base):
    """Database model for portfolio snapshots."""
    
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(Date, nullable=False)
    portfolio_value = Column(Float, nullable=False)
    benchmark_value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<PortfolioSnapshot(id={self.id}, date={self.snapshot_date})>"