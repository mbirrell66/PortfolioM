"""
Portfolio service for Portfolio Manager
"""

from datetime import datetime, date
from typing import List, Dict, Optional
from database.models import Position, Dividend
from database.database import SessionLocal
from services.market_data import MarketDataService

class PortfolioService:
    """Service for portfolio management operations."""
    
    def __init__(self):
        """Initialize portfolio service."""
        self.market_data_service = MarketDataService()
    
    def add_position(self, ticker: str, company_name: str, purchase_date: date, 
                    purchase_price: float, shares: int, notes: str = "") -> Position:
        """Add a new position to the portfolio."""
        db = SessionLocal()
        try:
            position = Position(
                ticker=ticker,
                company_name=company_name,
                purchase_date=purchase_date,
                purchase_price=purchase_price,
                shares=shares,
                notes=notes
            )
            db.add(position)
            db.commit()
            db.refresh(position)
            return position
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_positions(self) -> List[Position]:
        """Get all positions from the portfolio."""
        db = SessionLocal()
        try:
            return db.query(Position).all()
        finally:
            db.close()
    
    def get_position(self, position_id: int) -> Optional[Position]:
        """Get a specific position by ID."""
        db = SessionLocal()
        try:
            return db.query(Position).filter(Position.id == position_id).first()
        finally:
            db.close()
    
    def update_position(self, position_id: int, **kwargs) -> Optional[Position]:
        """Update a position."""
        db = SessionLocal()
        try:
            position = db.query(Position).filter(Position.id == position_id).first()
            if position:
                for key, value in kwargs.items():
                    if hasattr(position, key):
                        setattr(position, key, value)
                position.updated_at = datetime.now()
                db.commit()
                db.refresh(position)
                return position
            return None
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def delete_position(self, position_id: int) -> bool:
        """Delete a position."""
        db = SessionLocal()
        try:
            position = db.query(Position).filter(Position.id == position_id).first()
            if position:
                db.delete(position)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_current_prices(self, positions: List[Position]) -> Dict[str, Dict]:
        """Get current prices for all positions."""
        tickers = [pos.ticker for pos in positions]
        return self.market_data_service.get_multiple_stocks_data(tickers)
    
    def get_current_price(self, ticker: str) -> float:
        """Get current price for a single ticker."""
        data = self.market_data_service.get_stock_data(ticker)
        return data.get('current_price', 0.0) if data else 0.0
    
    def calculate_position_metrics(self, position: Position, current_price: float) -> Dict:
        """Calculate financial metrics for a position."""
        cost_basis = position.purchase_price * position.shares
        market_value = current_price * position.shares
        gain_loss = market_value - cost_basis
        gain_percent = (gain_loss / cost_basis) * 100 if cost_basis != 0 else 0
        
        return {
            'cost_basis': cost_basis,
            'market_value': market_value,
            'gain_loss': gain_loss,
            'gain_percent': gain_percent
        }
    
    def get_dividends_for_position(self, position_id: int) -> List:
        """Get all dividends for a specific position."""
        db = self.get_db()
        try:
            dividends = db.query(Dividend).filter(Dividend.position_id == position_id).all()
            return dividends
        except Exception as e:
            print(f"Error retrieving dividends: {e}")
            return []
        finally:
            db.close()
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value."""
        positions = self.get_positions()
        total_value = 0
        
        for position in positions:
            current_price = self.get_current_price(position.ticker)
            if current_price:
                total_value += current_price * position.shares
                
        return total_value
    
    def get_total_gain_loss(self) -> float:
        """Get total gain/loss for the portfolio."""
        positions = self.get_positions()
        total_value = 0
        total_cost = 0
        
        for position in positions:
            current_price = self.get_current_price(position.ticker)
            if current_price:
                total_value += current_price * position.shares
                total_cost += position.purchase_price * position.shares
                
        return total_value - total_cost
    
    def get_total_gain_loss_percent(self) -> float:
        """Get total gain/loss percentage for the portfolio."""
        positions = self.get_positions()
        total_value = 0
        total_cost = 0
        
        for position in positions:
            current_price = self.get_current_price(position.ticker)
            if current_price:
                total_value += current_price * position.shares
                total_cost += position.purchase_price * position.shares
                
        if total_cost != 0:
            return ((total_value - total_cost) / total_cost) * 100
        return 0.0