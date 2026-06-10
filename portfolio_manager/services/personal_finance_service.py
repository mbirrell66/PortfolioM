"""
Personal Finance Tracking Service
Provides services for personal finance tracking functionality.
"""
import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import sessionmaker
from portfolio_manager.database.personal_finance_models import (
    IncomeCategory, Income, ExpenseCategory, Expense, 
    FinancialGoal, Budget
)
from portfolio_manager.database.database import get_db, init_database

class PersonalFinanceService:
    """Service class for personal finance tracking functionality."""
    
    def __init__(self):
        """Initialize the personal finance service."""
        from database.database import get_db
        self.get_db = get_db
    
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
                date=date or datetime.utcnow(),
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
            query = db.query(Income)
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
                date=date or datetime.utcnow(),
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
            query = db.query(Expense)
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
                if goal.current_amount >= goal.target_amount:
                    goal.is_completed = True
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
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Get financial summary for a specific month."""
        db = next(self.get_db())
        try:
            # Get all income for the month
            income_query = db.query(Income).filter(
                Income.date >= datetime(year, month, 1),
                Income.date < datetime(year, month, 1) + timedelta(days=32)
            ).all()
            
            # Get all expenses for the month
            expense_query = db.query(Expense).filter(
                Expense.date >= datetime(year, month, 1),
                Expense.date < datetime(year, month, 1) + timedelta(days=32)
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