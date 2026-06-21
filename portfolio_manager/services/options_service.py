"""
Service layer for Options tracking.
"""
from __future__ import annotations
from datetime import date as _date
from database.database import SessionLocal
from database.options_models import OptionsPosition, OptionsCashBalance


class OptionsService:
    # ------------------------------------------------------------------ CRUD

    def get_all_positions(self) -> list[OptionsPosition]:
        db = SessionLocal()
        try:
            return (db.query(OptionsPosition)
                    .order_by(OptionsPosition.ticker, OptionsPosition.end_date.desc())
                    .all())
        finally:
            db.close()

    def get_position(self, position_id: int) -> OptionsPosition | None:
        db = SessionLocal()
        try:
            return db.query(OptionsPosition).filter(OptionsPosition.id == position_id).first()
        finally:
            db.close()

    def add_position(
        self, ticker: str, option_type: str, premium: float,
        strike_price: float, end_date: _date, num_contracts: int,
        num_shares: int, fees: float = 0.0, status: str = "Open",
        open_date: _date | None = None,
        close_premium: float | None = None, close_fees: float = 0.0,
        close_date: _date | None = None,
        notes: str | None = None,
    ) -> OptionsPosition:
        from datetime import date as _today
        db = SessionLocal()
        try:
            pos = OptionsPosition(
                ticker=ticker.upper(), option_type=option_type,
                premium=premium, strike_price=strike_price, end_date=end_date,
                num_contracts=num_contracts, num_shares=num_shares,
                fees=fees, status=status,
                open_date=open_date or _today.today(),
                close_premium=close_premium, close_fees=close_fees or 0.0,
                close_date=close_date,
                notes=notes,
            )
            db.add(pos)
            db.commit()
            db.refresh(pos)
            pos_id = pos.id
        finally:
            db.close()
        self._sync_ledger_entries(pos_id)
        return self.get_position(pos_id)

    def update_position(self, position_id: int, **kwargs) -> bool:
        db = SessionLocal()
        try:
            pos = db.query(OptionsPosition).filter(OptionsPosition.id == position_id).first()
            if not pos:
                return False
            for k, v in kwargs.items():
                if hasattr(pos, k):
                    setattr(pos, k, v)
            db.commit()
            ok = True
        finally:
            db.close()
        if ok:
            self._sync_ledger_entries(position_id)
        return ok

    def delete_position(self, position_id: int) -> bool:
        self._delete_ledger_entries(position_id)
        db = SessionLocal()
        try:
            pos = db.query(OptionsPosition).filter(OptionsPosition.id == position_id).first()
            if not pos:
                return False
            db.delete(pos)
            db.commit()
            return True
        finally:
            db.close()

    # ------------------------------------------------------- Ledger sync

    def _sync_ledger_entries(self, position_id: int) -> None:
        """Delete and recreate ledger entries for an options position."""
        from database.personal_finance_models import LedgerTransaction
        from datetime import datetime, date as _date_cls

        db = SessionLocal()
        try:
            pos = db.query(OptionsPosition).filter(OptionsPosition.id == position_id).first()
            if not pos:
                return

            # Clear old entries for this position
            db.query(LedgerTransaction).filter(
                LedgerTransaction.source_type == 'option',
                LedgerTransaction.source_id == position_id,
            ).delete()

            num_shares = pos.num_shares
            total_prem = pos.premium * num_shares
            contracts  = pos.num_contracts
            suffix = 's' if contracts > 1 else ''
            desc_base  = (f"{pos.ticker} {pos.option_type} ${pos.strike_price:.2f} "
                          f"({contracts} contract{suffix})")

            open_dt = datetime.combine(
                pos.open_date if pos.open_date else _date_cls.today(),
                datetime.min.time()
            )

            # 1. Premium received — credit
            db.add(LedgerTransaction(
                date=open_dt,
                transaction_type='Option Premium',
                description=f"{desc_base} — premium received",
                amount=total_prem,
                source_type='option',
                source_id=position_id,
            ))

            # 2. Opening fees — debit
            if pos.fees and pos.fees > 0:
                db.add(LedgerTransaction(
                    date=open_dt,
                    transaction_type='Option Fees',
                    description=f"{desc_base} — trading fees",
                    amount=pos.fees,
                    source_type='option',
                    source_id=position_id,
                ))

            # 3. Buyback cost — debit (only for Closed / Exercised)
            if pos.status in ('Closed', 'Exercised') and pos.close_premium is not None:
                close_dt_val = pos.close_date or pos.end_date or _date_cls.today()
                close_dt = datetime.combine(close_dt_val, datetime.min.time())
                buyback = pos.close_premium * num_shares
                db.add(LedgerTransaction(
                    date=close_dt,
                    transaction_type='Option Buyback',
                    description=f"{desc_base} — {pos.status.lower()}",
                    amount=buyback,
                    source_type='option',
                    source_id=position_id,
                ))
                if pos.close_fees and pos.close_fees > 0:
                    db.add(LedgerTransaction(
                        date=close_dt,
                        transaction_type='Option Fees',
                        description=f"{desc_base} — close fees",
                        amount=pos.close_fees,
                        source_type='option',
                        source_id=position_id,
                    ))

            db.commit()
        finally:
            db.close()

    def _delete_ledger_entries(self, position_id: int) -> None:
        from database.personal_finance_models import LedgerTransaction
        db = SessionLocal()
        try:
            db.query(LedgerTransaction).filter(
                LedgerTransaction.source_type == 'option',
                LedgerTransaction.source_id == position_id,
            ).delete()
            db.commit()
        finally:
            db.close()

    # ---------------------------------------------------------- Calculations

    @staticmethod
    def calc_total_premium(premium: float, num_shares: int) -> float:
        return premium * num_shares

    @staticmethod
    def calc_net_premium(total_premium: float, fees: float) -> float:
        return total_premium - fees

    @staticmethod
    def calc_net_per_share(net_premium: float, num_shares: int) -> float:
        return net_premium / num_shares if num_shares else 0.0

    @staticmethod
    def calc_total_value(strike_price: float, num_shares: int) -> float:
        """Capital locked away to cover a put (or value at strike for a call)."""
        return strike_price * num_shares

    @staticmethod
    def calc_profit_loss(
        status: str, net_premium: float,
        close_premium: float | None, num_shares: int, close_fees: float,
    ) -> float | None:
        if status == "Open":
            return None
        if status == "Expired":
            return net_premium          # option expired worthless — keep all premium
        # Closed (bought back) or Exercised
        if close_premium is not None:
            close_cost = close_premium * num_shares + (close_fees or 0.0)
            return net_premium - close_cost
        return net_premium

    def get_locked_capital(self) -> float:
        """Sum of Total Value for all open Put positions."""
        positions = self.get_all_positions()
        total = 0.0
        for p in positions:
            if p.status == "Open" and p.option_type == "Put":
                total += self.calc_total_value(p.strike_price, p.num_shares)
        return total

    def get_available_funds(self, ledger_balance: float) -> float:
        return ledger_balance - self.get_locked_capital()
