"""
Tax Management Database Models
Defines database models for tax tracking functionality based on Australian tax laws.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TaxCategory(Base):
    """Database model for tax categories."""
    __tablename__ = 'tax_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    tax_type = Column(String(50), nullable=False)  # 'income', 'capital_gains', 'fringe_benefit'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    tax_events = relationship("TaxEvent", back_populates="category")

class TaxEvent(Base):
    """Database model for tax events tracking."""
    __tablename__ = 'tax_events'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('tax_categories.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    tax_rate = Column(Float, default=0.0)  # Tax rate applicable
    tax_amount = Column(Float, default=0.0)  # Calculated tax amount
    is_deductible = Column(Boolean, default=False)  # If this tax can be deducted
    is_reported = Column(Boolean, default=False)  # If this is reported in tax return
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("TaxCategory", back_populates="tax_events")

class CapitalGainsEvent(Base):
    """Database model for capital gains events (Australian tax law compliant)."""
    __tablename__ = 'capital_gains_events'
    
    id = Column(Integer, primary_key=True)
    asset_type = Column(String(100), nullable=False)  # 'shares', 'property', etc.
    acquisition_date = Column(Date, nullable=False)
    disposal_date = Column(Date, nullable=False)
    acquisition_cost = Column(Float, nullable=False)
    proceeds = Column(Float, nullable=False)
    capital_gain = Column(Float, default=0.0)  # Calculated capital gain
    tax_rate = Column(Float, default=0.0)  # Applicable tax rate (e.g., 50% for CGT discount)
    tax_liability = Column(Float, default=0.0)  # Calculated tax liability
    is_exempt = Column(Boolean, default=False)  # If this is exempt from CGT
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to portfolio positions for tracking (commented out for now to avoid foreign key issues)
    # position_id = Column(Integer, ForeignKey('positions.id'), nullable=True)
    # position = relationship("Position")

class TaxReturn(Base):
    """Database model for tax return tracking."""
    __tablename__ = 'tax_returns'
    
    id = Column(Integer, primary_key=True)
    tax_year = Column(String(9), nullable=False)  # Format: '2023-2024'
    filing_date = Column(Date)
    total_income = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    total_tax_owed = Column(Float, default=0.0)
    total_refund = Column(Float, default=0.0)
    status = Column(String(50), default='draft')  # 'draft', 'submitted', 'processed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)