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

CGT_DISCOUNT_RATE = 0.5  # individuals; assets held more than 12 months


def held_over_12_months(acquisition_date: date, disposal_date: date) -> bool:
    """True if the asset qualifies for the CGT discount on holding period.

    The asset must be owned for at least 12 months, and neither the day of
    acquisition nor the day of disposal counts. So something bought on
    1 Jan 2025 qualifies from 2 Jan 2026, not 1 Jan 2026.
    """
    try:
        anniversary = acquisition_date.replace(year=acquisition_date.year + 1)
    except ValueError:  # bought on 29 Feb
        anniversary = acquisition_date.replace(year=acquisition_date.year + 1, day=28)
    return disposal_date > anniversary


def calculate_net_capital_gain(events, prior_year_losses: float = 0.0) -> Dict:
    """Net capital gain for a set of disposals, the way the tax return works it out.

    1. Add up the gains (exempt events are ignored entirely).
    2. Subtract capital losses - this period's, then any carried forward.
       Losses come off non-discount gains first, which gives the lowest result
       and is the order a taxpayer is allowed to choose.
    3. Apply the 50% discount to what is left of the gains held over 12 months.

    The result is an amount of assessable income, not a tax bill. The tax on
    it depends on the person's marginal rate, which this app does not know.

    Each event needs: acquisition_date, disposal_date, acquisition_cost,
    proceeds, is_exempt.
    """
    discountable_gains = 0.0
    other_gains = 0.0
    losses = 0.0
    for e in events:
        if e.is_exempt:
            continue
        gain = e.proceeds - e.acquisition_cost
        if gain < 0:
            losses += -gain
        elif held_over_12_months(e.acquisition_date, e.disposal_date):
            discountable_gains += gain
        else:
            other_gains += gain

    available_losses = losses + max(prior_year_losses, 0.0)
    used_on_other = min(other_gains, available_losses)
    used_on_discountable = min(discountable_gains, available_losses - used_on_other)
    losses_applied = used_on_other + used_on_discountable

    discountable_after_losses = discountable_gains - used_on_discountable
    discount = discountable_after_losses * CGT_DISCOUNT_RATE
    net_gain = (other_gains - used_on_other) + discountable_after_losses - discount

    return {
        "total_capital_gains": other_gains + discountable_gains,
        "discountable_gains": discountable_gains,
        "other_gains": other_gains,
        "capital_losses": losses,
        "prior_year_losses": max(prior_year_losses, 0.0),
        "losses_applied": losses_applied,
        "cgt_discount": discount,
        "net_capital_gain": net_gain,
        "losses_carried_forward": available_losses - losses_applied,
    }


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
        """Record a disposal.

        Stores the raw gain or loss. tax_rate holds the CGT discount percentage
        this event qualifies for on its own (50 or 0). tax_liability is left at
        0: tax cannot be worked out per event, because losses are netted across
        all events first and the rate is the person's marginal rate. Use
        calculate_tax_summary() for the net capital gain.
        """
        if disposal_date < acquisition_date:
            raise ValueError("Disposal date cannot be before acquisition date")

        capital_gain = proceeds - acquisition_cost
        discount_eligible = (
            not is_exempt
            and capital_gain > 0
            and held_over_12_months(acquisition_date, disposal_date)
        )

        db = next(self.get_db())
        try:
            capital_gains_event = CapitalGainsEvent(
                asset_type=asset_type,
                acquisition_date=acquisition_date,
                disposal_date=disposal_date,
                acquisition_cost=acquisition_cost,
                proceeds=proceeds,
                capital_gain=capital_gain,
                tax_rate=CGT_DISCOUNT_RATE * 100 if discount_eligible else 0.0,
                tax_liability=0.0,
                is_exempt=is_exempt
            )
            db.add(capital_gains_event)
            db.commit()
            db.refresh(capital_gains_event)
            return capital_gains_event
        except Exception:
            db.rollback()
            raise
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
    
    def calculate_tax_summary(self, start_date: date, end_date: date,
                              prior_year_losses: float = 0.0) -> Dict:
        """Summary for a date range (normally one financial year, 1 Jul - 30 Jun).

        Capital gains are netted across the whole range - see
        calculate_net_capital_gain(). No capital gains tax figure is returned.
        """
        db = next(self.get_db())
        try:
            tax_events = db.query(TaxEvent).filter(
                TaxEvent.date >= start_date,
                TaxEvent.date <= end_date
            ).all()

            capital_gains = db.query(CapitalGainsEvent).filter(
                CapitalGainsEvent.disposal_date >= start_date,
                CapitalGainsEvent.disposal_date <= end_date
            ).all()

            total_income_tax = sum(
                event.tax_amount for event in tax_events
                if event.category and event.category.tax_type == 'income'
            )

            summary = {
                "total_income_tax": total_income_tax,
                "tax_events_count": len(tax_events),
                "capital_gains_count": len(capital_gains),
            }
            summary.update(calculate_net_capital_gain(capital_gains, prior_year_losses))
            return summary
        finally:
            db.close()
