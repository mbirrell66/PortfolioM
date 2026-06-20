"""
Portfolio service for Portfolio Manager
"""

from datetime import datetime, date
from typing import List, Dict, Optional
from database.models import Position, Dividend, DividendEvent, StockSplit
from database.database import SessionLocal
from services.market_data import MarketDataService

class PortfolioService:
    """Service for portfolio management operations."""
    
    def __init__(self):
        self.market_data_service = MarketDataService()
    
    def add_position(self, ticker: str, company_name: str, purchase_date: date,
                    purchase_price: float, shares: int, notes: str = "",
                    buy_commission: float = 0.0) -> Position:
        """Add a new position to the portfolio."""
        db = SessionLocal()
        try:
            position = Position(
                ticker=ticker,
                company_name=company_name,
                purchase_date=purchase_date,
                purchase_price=purchase_price,
                shares=shares,
                notes=notes,
                buy_commission=buy_commission,
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
        """Get all positions."""
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

    def get_open_positions(self) -> List[Position]:
        """Return positions that have not been sold."""
        db = SessionLocal()
        try:
            return db.query(Position).filter(Position.sell_date.is_(None)).all()
        finally:
            db.close()

    def get_closed_positions(self) -> List[Position]:
        """Return positions that have been sold."""
        db = SessionLocal()
        try:
            return db.query(Position).filter(Position.sell_date.isnot(None)).all()
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

    def partial_close_position(self, position_id: int, shares_to_sell: int,
                               sell_date: date, sell_price: float,
                               sell_commission: float = 0.0) -> bool:
        """Close part or all of a position.

        Full close (shares_to_sell == position.shares):
            Updates the position in-place with sell details.

        Partial close (shares_to_sell < position.shares):
            - Reduces the original position's share count and proportionally
              adjusts its buy commission so it remains open for the unsold shares.
            - Creates a new closed Position record for the sold tranche,
              carrying the proportional slice of the original buy commission.

        Returns True on success; raises on error.
        """
        db = SessionLocal()
        try:
            pos = db.query(Position).filter(Position.id == position_id).first()
            if not pos:
                return False
            if shares_to_sell <= 0 or shares_to_sell > pos.shares:
                raise ValueError(
                    "shares_to_sell ({}) must be between 1 and {}".format(
                        shares_to_sell, pos.shares))

            if shares_to_sell == pos.shares:
                # Full close — update in-place
                pos.sell_date       = sell_date
                pos.sell_price      = sell_price
                pos.sell_commission = sell_commission
                pos.updated_at      = datetime.now()
                db.commit()
            else:
                # Partial close — split the position
                total_shares         = pos.shares
                orig_commission      = pos.buy_commission or 0.0
                sold_frac            = shares_to_sell / total_shares
                sold_buy_commission  = round(orig_commission * sold_frac, 4)
                remaining_commission = round(orig_commission - sold_buy_commission, 4)

                # New closed record for the sold tranche
                closed = Position(
                    ticker          = pos.ticker,
                    company_name    = pos.company_name,
                    purchase_date   = pos.purchase_date,
                    purchase_price  = pos.purchase_price,
                    shares          = shares_to_sell,
                    buy_commission  = sold_buy_commission,
                    sell_date       = sell_date,
                    sell_price      = sell_price,
                    sell_commission = sell_commission,
                    notes           = pos.notes,
                )
                db.add(closed)

                # Shrink the original (stays open)
                pos.shares         = total_shares - shares_to_sell
                pos.buy_commission = remaining_commission
                pos.updated_at     = datetime.now()

                db.commit()

            return True
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
        db = SessionLocal()
        try:
            return db.query(Dividend).filter(Dividend.position_id == position_id).all()
        finally:
            db.close()

    def add_dividend(self, position_id: int, amount: float, payment_date: date) -> Dividend:
        """Add a dividend payment for a position."""
        db = SessionLocal()
        try:
            dividend = Dividend(
                position_id=position_id,
                amount=amount,
                payment_date=payment_date
            )
            db.add(dividend)
            db.commit()
            db.refresh(dividend)
            return dividend
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def add_dividend_event(self, ticker: str, amount_per_share: float,
                           ex_date: date, payment_date: date,
                           dividend_type: str = "Regular") -> DividendEvent:
        """Add a dividend event."""
        db = SessionLocal()
        try:
            event = DividendEvent(
                ticker=ticker,
                amount_per_share=amount_per_share,
                ex_date=ex_date,
                payment_date=payment_date,
                dividend_type=dividend_type
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_dividend_events(self) -> List[DividendEvent]:
        """Get all dividend events."""
        db = SessionLocal()
        try:
            return db.query(DividendEvent).all()
        finally:
            db.close()

    def get_dividend_events_for_ticker(self, ticker: str) -> List[DividendEvent]:
        """Get all dividend events for a specific ticker."""
        db = SessionLocal()
        try:
            return db.query(DividendEvent).filter(DividendEvent.ticker == ticker).all()
        finally:
            db.close()

    def add_stock_split(self, ticker: str, split_date: date,
                        old_ratio: int, new_ratio: int) -> StockSplit:
        """Add a new stock split to the database."""
        db = SessionLocal()
        try:
            stock_split = StockSplit(
                ticker=ticker,
                split_date=split_date,
                old_ratio=old_ratio,
                new_ratio=new_ratio
            )
            db.add(stock_split)
            db.commit()
            db.refresh(stock_split)
            return stock_split
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_stock_splits(self) -> List[StockSplit]:
        """Get all stock splits."""
        db = SessionLocal()
        try:
            return db.query(StockSplit).all()
        finally:
            db.close()

    def get_portfolio_value(self) -> float:
        """Get total portfolio value (open positions only)."""
        positions = self.get_open_positions()
        total_value = 0
        for position in positions:
            current_price = self.get_current_price(position.ticker)
            if current_price:
                total_value += current_price * position.shares
        return total_value

    def get_total_gain_loss(self) -> float:
        """Get total gain/loss for open positions."""
        positions = self.get_open_positions()
        total_value = 0
        total_cost = 0
        for position in positions:
            current_price = self.get_current_price(position.ticker)
            if current_price:
                total_value += current_price * position.shares
                total_cost += position.purchase_price * position.shares
        return total_value - total_cost

    def get_total_gain_loss_percent(self) -> float:
        """Get total gain/loss percentage for open positions."""
        positions = self.get_open_positions()
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

    def get_portfolio_cost_basis(self) -> float:
        """Get total portfolio cost basis (open positions only)."""
        positions = self.get_open_positions()
        total_cost = 0
        for position in positions:
            total_cost += position.purchase_price * position.shares
        return total_cost
