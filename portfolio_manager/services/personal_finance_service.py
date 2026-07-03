"""
Personal Finance Tracking Service
Provides services for personal finance tracking functionality.
"""
import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker, joinedload
from database.personal_finance_models import (
    IncomeCategory, Income, ExpenseCategory, Expense,
    FinancialGoal, Budget
)
from database.database import get_db, init_database

class PersonalFinanceService:
    """Service class for personal finance tracking functionality."""
    
    def __init__(self):
        """Initialize the personal finance service."""
        from database.database import get_db
        self.get_db = get_db

    @staticmethod
    def _to_datetime(value):
        """Normalize a date or datetime (or None) to a datetime for storage."""
        if value is None:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return value

    @staticmethod
    def _next_month(dt: datetime, anchor_day: int) -> datetime:
        """Return the same time next month, clamping to month length
        (e.g. an anchor of 31 posts on Feb 28, then Mar 31 again)."""
        import calendar
        year, month = (dt.year + 1, 1) if dt.month == 12 else (dt.year, dt.month + 1)
        day = min(anchor_day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)

    def process_recurring_transactions(self) -> int:
        """Post monthly occurrences for recurring incomes/expenses up to today.

        Records with is_recurring=True act as templates. Each elapsed month
        since the template's last posted occurrence gets a normal (non-
        recurring) record linked back via parent_id. Returns count posted.
        """
        posted = 0
        now = datetime.utcnow()
        db = next(self.get_db())
        try:
            for model in (Income, Expense):
                templates = db.query(model).filter(
                    model.is_recurring == True,  # noqa: E712
                    model.parent_id == None      # noqa: E711
                ).all()
                for tpl in templates:
                    tpl_date = self._to_datetime(tpl.date)
                    anchor_day = tpl_date.day
                    last = db.query(model).filter(
                        model.parent_id == tpl.id
                    ).order_by(model.date.desc()).first()
                    cursor = self._to_datetime(last.date) if last else tpl_date
                    next_date = self._next_month(cursor, anchor_day)
                    while next_date <= now:
                        db.add(model(
                            amount=tpl.amount,
                            category_id=tpl.category_id,
                            description=tpl.description,
                            date=next_date,
                            is_recurring=False,
                            parent_id=tpl.id,
                        ))
                        posted += 1
                        next_date = self._next_month(next_date, anchor_day)
            if posted:
                db.commit()
            return posted
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_income_category(self, name: str, description: str = "") -> IncomeCategory:
        """Create a new income category."""
        db = next(self.get_db())
        try:
            category = IncomeCategory(name=name, description=description)
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_income_categories(self) -> List[IncomeCategory]:
        """Get all income categories."""
        db = next(self.get_db())
        try:
            return db.query(IncomeCategory).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_income(self, amount: float, category_id: int, description: str = "", 
                     date: datetime = None, is_recurring: bool = False) -> Income:
        """Create a new income record."""
        db = next(self.get_db())
        try:
            income = Income(
                amount=amount,
                category_id=category_id,
                description=description,
                date=self._to_datetime(date),
                is_recurring=is_recurring
            )
            db.add(income)
            db.commit()
            db.refresh(income)
            return income
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_incomes(self, start_date: datetime = None, end_date: datetime = None) -> List[Income]:
        """Get income records within a date range."""
        db = next(self.get_db())
        try:
            query = db.query(Income).options(joinedload(Income.category))
            if start_date:
                query = query.filter(Income.date >= start_date)
            if end_date:
                query = query.filter(Income.date <= end_date)
            return query.all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_expense_category(self, name: str, description: str = "", 
                               budget_limit: float = 0.0) -> ExpenseCategory:
        """Create a new expense category."""
        db = next(self.get_db())
        try:
            category = ExpenseCategory(
                name=name, 
                description=description,
                budget_limit=budget_limit
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
    
    def get_expense_categories(self) -> List[ExpenseCategory]:
        """Get all expense categories."""
        db = next(self.get_db())
        try:
            return db.query(ExpenseCategory).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_expense(self, amount: float, category_id: int, description: str = "", 
                      date: datetime = None, is_recurring: bool = False) -> Expense:
        """Create a new expense record."""
        db = next(self.get_db())
        try:
            expense = Expense(
                amount=amount,
                category_id=category_id,
                description=description,
                date=self._to_datetime(date),
                is_recurring=is_recurring
            )
            db.add(expense)
            db.commit()
            db.refresh(expense)
            return expense
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_expenses(self, start_date: datetime = None, end_date: datetime = None) -> List[Expense]:
        """Get expense records within a date range."""
        db = next(self.get_db())
        try:
            query = db.query(Expense).options(joinedload(Expense.category))
            if start_date:
                query = query.filter(Expense.date >= start_date)
            if end_date:
                query = query.filter(Expense.date <= end_date)
            return query.all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def create_financial_goal(self, title: str, description: str, target_amount: float, 
                             deadline: datetime = None) -> FinancialGoal:
        """Create a new financial goal."""
        db = next(self.get_db())
        try:
            goal = FinancialGoal(
                title=title,
                description=description,
                target_amount=target_amount,
                deadline=deadline
            )
            db.add(goal)
            db.commit()
            db.refresh(goal)
            return goal
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_financial_goals(self) -> List[FinancialGoal]:
        """Get all financial goals."""
        db = next(self.get_db())
        try:
            return db.query(FinancialGoal).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def update_financial_goal_amount(self, goal_id: int, amount: float) -> FinancialGoal:
        """Update the current amount for a financial goal."""
        db = next(self.get_db())
        try:
            goal = db.query(FinancialGoal).filter(FinancialGoal.id == goal_id).first()
            if goal:
                goal.current_amount = amount
                goal.is_completed = goal.current_amount >= goal.target_amount
                db.commit()
                db.refresh(goal)
                return goal
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_budget(self, category_id: int, month: str, budget_limit: float) -> Budget:
        """Create or update a monthly budget for an expense category."""
        db = next(self.get_db())
        try:
            budget = db.query(Budget).filter(
                Budget.category_id == category_id,
                Budget.month == month
            ).first()
            
            if budget:
                budget.budget_limit = budget_limit
            else:
                budget = Budget(
                    category_id=category_id,
                    month=month,
                    budget_limit=budget_limit
                )
            db.add(budget)
            db.commit()
            db.refresh(budget)
            return budget
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_budgets(self) -> List[Budget]:
        """Get all budgets."""
        db = next(self.get_db())
        try:
            return db.query(Budget).all()
        except Exception as e:
            raise e
        finally:
            db.close()
    
    def get_ledger_balance(self, portfolio_service=None) -> float:
        """Return the current running balance from the full ledger.

        Mirrors the calculation in LedgerTab.load_data() so the Options tab
        can read the live cash position without going through the GUI.
        """
        from database.database import SessionLocal as _SL
        credits = 0.0
        debits  = 0.0

        # Portfolio buys / sells
        if portfolio_service:
            try:
                for pos in portfolio_service.get_positions():
                    debits += pos.purchase_price * pos.shares + (pos.buy_commission or 0.0)
                    if pos.sell_date and pos.sell_price:
                        credits += pos.sell_price * pos.shares - (pos.sell_commission or 0.0)
            except Exception:
                pass

            # Dividends
            try:
                from database.models import DividendEvent
                db = _SL()
                try:
                    for div in db.query(DividendEvent).all():
                        credits += div.cash_received
                finally:
                    db.close()
            except Exception:
                pass

        # Income / expenses
        try:
            from database.personal_finance_models import Income, Expense
            db = _SL()
            try:
                for inc in db.query(Income).all():
                    credits += inc.amount
                for exp in db.query(Expense).all():
                    debits += exp.amount
            finally:
                db.close()
        except Exception:
            pass

        # Manual deposits / withdrawals + option ledger entries
        _CREDIT_TYPES = {"Deposit", "Option Premium"}
        try:
            from database.personal_finance_models import LedgerTransaction
            db = _SL()
            try:
                for txn in db.query(LedgerTransaction).all():
                    if txn.transaction_type in _CREDIT_TYPES:
                        credits += txn.amount
                    else:
                        debits += txn.amount
            finally:
                db.close()
        except Exception:
            pass

        return credits - debits

    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get financial summary for a specific month."""
        db = next(self.get_db())
        try:
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)

            # Get all income for the month
            income_query = db.query(Income).filter(
                Income.date >= month_start,
                Income.date < month_end
            ).all()

            # Get all expenses for the month
            expense_query = db.query(Expense).filter(
                Expense.date >= month_start,
                Expense.date < month_end
            ).all()
            
            total_income = sum(income.amount for income in income_query)
            total_expenses = sum(expense.amount for expense in expense_query)
            
            return {
                "income": total_income,
                "expenses": total_expenses,
                "net": total_income - total_expenses,
                "income_count": len(income_query),
                "expense_count": len(expense_query)
            }
        except Exception as e:
            raise e
        finally:
            db.close()