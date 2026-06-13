"""
Personal Finance Tracking Database Models
Defines database models for personal finance tracking functionality.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class IncomeCategory(Base):
    """Database model for income categories."""
    __tablename__ = 'income_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    incomes = relationship("Income", back_populates="category")

class Income(Base):
    """Database model for income tracking."""
    __tablename__ = 'incomes'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('income_categories.id'), nullable=False)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("IncomeCategory", back_populates="incomes")

class ExpenseCategory(Base):
    """Database model for expense categories."""
    __tablename__ = 'expense_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    budget_limit = Column(Float, default=0.0)  # Monthly budget limit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    """Database model for expense tracking."""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('expense_categories.id'), nullable=False)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("ExpenseCategory", back_populates="expenses")

class FinancialGoal(Base):
    """Database model for financial goals."""
    __tablename__ = 'financial_goals'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Budget(Base):
    """Database model for monthly budgets."""
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('expense_categories.id'), nullable=False)
    month = Column(String(7), nullable=False)  # Format: YYYY-MM
    budget_limit = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    category = relationship("ExpenseCategory")


class LedgerTransaction(Base):
    """Manual ledger entries: deposits and withdrawals."""
    __tablename__ = 'ledger_transactions'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    transaction_type = Column(String(20), nullable=False)   # 'Deposit' | 'Withdrawal'
    description = Column(String(500), nullable=True)
    amount = Column(Float, nullable=False)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
