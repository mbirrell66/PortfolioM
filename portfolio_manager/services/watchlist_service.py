"""
Watchlist service for Portfolio Manager.
"""

from database.database import SessionLocal
from database.watchlist_models import WatchlistItem


class WatchlistService:
    """CRUD operations for watchlist items."""

    def add_item(self, ticker, company_name, entry_price, entry_date,
                 shares_hypothetical=None, target_price=None, notes=None):
        """Persist a new watchlist item and return it."""
        db = SessionLocal()
        try:
            item = WatchlistItem(
                ticker=ticker.upper().strip(),
                company_name=company_name or ticker.upper().strip(),
                entry_price=entry_price,
                entry_date=entry_date,
                shares_hypothetical=shares_hypothetical,
                target_price=target_price,
                notes=notes,
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        finally:
            db.close()

    def get_items(self):
        """Return all watchlist items ordered by entry_date descending."""
        db = SessionLocal()
        try:
            return (
                db.query(WatchlistItem)
                .order_by(WatchlistItem.entry_date.desc())
                .all()
            )
        finally:
            db.close()

    def get_item(self, item_id):
        """Return a single WatchlistItem by primary key, or None."""
        db = SessionLocal()
        try:
            return (
                db.query(WatchlistItem)
                .filter(WatchlistItem.id == item_id)
                .first()
            )
        finally:
            db.close()

    def remove_item(self, item_id):
        """Delete a watchlist item by primary key. Returns True on success."""
        db = SessionLocal()
        try:
            item = (
                db.query(WatchlistItem)
                .filter(WatchlistItem.id == item_id)
                .first()
            )
            if item:
                db.delete(item)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def update_item(self, item_id, **kwargs):
        """Update named fields on a watchlist item. Returns True on success."""
        db = SessionLocal()
        try:
            item = (
                db.query(WatchlistItem)
                .filter(WatchlistItem.id == item_id)
                .first()
            )
            if not item:
                return False
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.commit()
            return True
        finally:
            db.close()
