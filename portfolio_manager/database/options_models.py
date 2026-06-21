"""
SQLAlchemy models for Options tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text
from sqlalchemy.ext.declarative import declarative_base

OptionsBase = declarative_base()


class OptionsPosition(OptionsBase):
    __tablename__ = "options_positions"

    id            = Column(Integer, primary_key=True)
    ticker        = Column(String(10), nullable=False, index=True)
    option_type   = Column(String(4),  nullable=False)          # 'Call' | 'Put'
    premium       = Column(Float,      nullable=False)           # per share
    strike_price  = Column(Float,      nullable=False)
    end_date      = Column(Date,       nullable=False)
    num_contracts = Column(Integer,    nullable=False)           # No. buy or sell
    num_shares    = Column(Integer,    nullable=False)           # num_contracts × 100
    fees          = Column(Float,      nullable=False, default=0.0)
    status        = Column(String(10), nullable=False, default="Open")
    open_date     = Column(Date, nullable=True)              # date option was written
    # Populated when position is closed / bought back
    close_premium = Column(Float, nullable=True)
    close_fees    = Column(Float, nullable=True, default=0.0)
    close_date    = Column(Date, nullable=True)              # date position was closed
    notes         = Column(Text,  nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"<OptionsPosition(id={self.id}, ticker='{self.ticker}', "
                f"type='{self.option_type}', status='{self.status}')>")


class OptionsCashBalance(OptionsBase):
    """Single-row table that stores the user's total account cash balance."""
    __tablename__ = "options_cash_balance"

    id      = Column(Integer, primary_key=True)
    balance = Column(Float, nullable=False, default=0.0)
