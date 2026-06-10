"""
Tax Management Service
Provides services for tax tracking and calculation based on Australian tax laws.
"""
import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker
from portfolio_manager.database.tax_models import (
    TaxCategory, TaxEvent, CapitalGainsEvent, TaxReturn
)
from portfolio_manager.database.database import get_db

class TaxService:
    """Service class for tax tracking and calculation functionality."""
    
    def __init__(self):
        """Initialize the tax service."""
        self.get_db = get_db
    
    def create_tax_category(self, name: str, description: str, tax_type: str) -> TaxCategory:
        """Create a new tax category."""
        db = next(self.get_db())
        try:
            category = TaxCategory(
                name=name,
                description=description,
                tax_type=tax_type
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_tax_categories(self) -> List[TaxCategory]:
        """Get all tax categories."""
        db = next(self.get_db())
        try:
            return db.query(TaxCategory).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_tax_event(self, category_id: int, title: str, description: str, 
                        amount: float, date: date, tax_rate: float = 0.0, 
                        is_deductible: bool = False) -> TaxEvent:
        """Create a new tax event."""
        db = next(self.get_db())
        try:
            # Calculate tax amount
            tax_amount = amount * (tax_rate / 100)
            
            tax_event = TaxEvent(
                category_id=category_id,
                title=title,
                description=description,
                amount=amount,
                date=date,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                is_deductible=is_deductible
            )
            db.add(tax_event)
            db.commit()
            db.refresh(tax_event)
            return tax_event
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_tax_events(self, start_date: date = None, end_date: date = None) -> List[TaxEvent]:
        """Get tax events within a date range."""
        db = next(self.get_db())
        try:
            query = db.query(TaxEvent)
            if start_date:
                query = query.filter(TaxEvent.date >= start_date)
            if end_date:
                query = query.filter(TaxEvent.date <= end_date)
            return query.all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_capital_gains_event(self, asset_type: str, acquisition_date: date, 
                                  disposal_date: date, acquisition_cost: float, 
                                  proceeds: float, is_exempt: bool = False) -> CapitalGainsEvent:
        """Create a capital gains event for Australian tax calculation."""
        db = next(self.get_db())
        try:
            # Calculate capital gain
            capital_gain = proceeds - acquisition_cost
            
            # Apply Australian CGT rules - 50% discount for holding period > 1 year
            # Simplified version for this implementation
            tax_rate = 0.0  # Default, will be calculated based on holding period
            tax_liability = 0.0
            
            # Calculate tax liability if not exempt
            if not is_exempt and capital_gain > 0:
                # Apply 50% CGT discount for individuals (simplified)
                taxable_gain = capital_gain * 0.5
                # Apply current tax rates for individuals (simplified)
                # This is a basic approximation - actual CGT calculation is more complex
                tax_rate = 0.15  # Simplified rate
                tax_liability = taxable_gain * tax_rate
            
            capital_gains_event = CapitalGainsEvent(
                asset_type=asset_type,
                acquisition_date=acquisition_date,
                disposal_date=disposal_date,
                acquisition_cost=acquisition_cost,
                proceeds=proceeds,
                capital_gain=capital_gain,
                tax_rate=tax_rate,
                tax_liability=tax_liability,
                is_exempt=is_exempt
            )
            db.add(capital_gains_event)
            db.commit()
            db.refresh(capital_gains_event)
            return capital_gains_event
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_capital_gains_events(self, start_date: date = None, end_date: date = None) -> List[CapitalGainsEvent]:
        """Get capital gains events within a date range."""
        db = next(self.get_db())
        try:
            query = db.query(CapitalGainsEvent)
            if start_date:
                query = query.filter(CapitalGainsEvent.disposal_date >= start_date)
            if end_date:
                query = query.filter(CapitalGainsEvent.disposal_date <= end_date)
            return query.all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_tax_return(self, tax_year: str, filing_date: date = None) -> TaxReturn:
        """Create a new tax return."""
        db = next(self.get_db())
        try:
            tax_return = TaxReturn(
                tax_year=tax_year,
                filing_date=filing_date,
                status='draft'
            )
            db.add(tax_return)
            db.commit()
            db.refresh(tax_return)
            return tax_return
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_tax_returns(self) -> List[TaxReturn]:
        """Get all tax returns."""
        db = next(self.get_db())
        try:
            return db.query(TaxReturn).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def calculate_tax_summary(self, start_date: date, end_date: date) -> Dict:
        """Calculate tax summary for a date range."""
        db = next(self.get_db())
        try:
            # Get all tax events in date range
            tax_events = db.query(TaxEvent).filter(
                TaxEvent.date >= start_date,
                TaxEvent.date <= end_date
            ).all()
            
            # Get all capital gains events in date range
            capital_gains = db.query(CapitalGainsEvent).filter(
                CapitalGainsEvent.disposal_date >= start_date,
                CapitalGainsEvent.disposal_date <= end_date
            ).all()
            
            # Calculate totals
            total_income_tax = sum(event.tax_amount for event in tax_events if event.category.tax_type == 'income')
            total_capital_gains_tax = sum(event.tax_liability for event in capital_gains)
            total_tax_liability = total_income_tax + total_capital_gains_tax
            
            return {
                "total_income_tax": total_income_tax,
                "total_capital_gains_tax": total_capital_gains_tax,
                "total_tax_liability": total_tax_liability,
                "tax_events_count": len(tax_events),
                "capital_gains_count": len(capital_gains)
            }
        except Exception as e:
            raise e
        finally:
            db.close()