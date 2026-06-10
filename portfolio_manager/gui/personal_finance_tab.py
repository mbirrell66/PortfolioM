"""
Personal Finance Tracking GUI Components
Provides GUI components for personal finance tracking functionality.
"""
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit, QGroupBox, 
    QCheckBox, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from services.personal_finance_service import PersonalFinanceService
from database.personal_finance_models import IncomeCategory, ExpenseCategory

class PersonalFinanceTab(QWidget):
    """Main tab for personal finance tracking."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the personal finance tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        
        # Add income tab
        income_tab = IncomeTab(self.personal_finance_service)
        tab_widget.addTab(income_tab, "Income")
        
        # Add expense tab
        expense_tab = ExpenseTab(self.personal_finance_service)
        tab_widget.addTab(expense_tab, "Expenses")
        
        # Add budget tab
        budget_tab = BudgetTab(self.personal_finance_service)
        tab_widget.addTab(budget_tab, "Budgets")
        
        # Add goals tab
        goals_tab = GoalsTab(self.personal_finance_service)
        tab_widget.addTab(goals_tab, "Goals")
        
        # Add summary tab
        summary_tab = SummaryTab(self.personal_finance_service)
        tab_widget.addTab(summary_tab, "Summary")
        
        layout.addWidget(tab_widget)
    
    def load_data(self):
        """Load initial data."""
        pass

class IncomeTab(QWidget):
    """Tab for income tracking."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the income tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
        self.load_income_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Input form
        form_layout = QGridLayout()
        
        # Category
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        form_layout.addWidget(category_label, 0, 0)
        form_layout.addWidget(self.category_combo, 0, 1)
        
        # Amount
        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        form_layout.addWidget(amount_label, 1, 0)
        form_layout.addWidget(self.amount_input, 1, 1)
        
        # Description
        description_label = QLabel("Description:")
        self.description_input = QLineEdit()
        form_layout.addWidget(description_label, 2, 0)
        form_layout.addWidget(self.description_input, 2, 1)
        
        # Date
        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(date_label, 3, 0)
        form_layout.addWidget(self.date_input, 3, 1)
        
        # Recurring
        self.recurring_checkbox = QCheckBox("Recurring")
        form_layout.addWidget(self.recurring_checkbox, 4, 1)
        
        # Add button
        add_button = QPushButton("Add Income")
        add_button.clicked.connect(self.add_income)
        form_layout.addWidget(add_button, 5, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Income table
        self.income_table = QTableWidget(0, 5)
        self.income_table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Description", "Recurring"])
        self.income_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.income_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.income_table)
        
        # Load categories
        self.load_categories()
    
    def load_categories(self):
        """Load income categories into combo box."""
        categories = self.personal_finance_service.get_income_categories()
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def load_income_data(self):
        """Load income data into table."""
        incomes = self.personal_finance_service.get_incomes()
        self.income_table.setRowCount(len(incomes))
        
        for i, income in enumerate(incomes):
            self.income_table.setItem(i, 0, QTableWidgetItem(income.date.strftime("%Y-%m-%d")))
            self.income_table.setItem(i, 1, QTableWidgetItem(income.category.name))
            self.income_table.setItem(i, 2, QTableWidgetItem(f"${income.amount:.2f}"))
            self.income_table.setItem(i, 3, QTableWidgetItem(income.description or ""))
            self.income_table.setItem(i, 4, QTableWidgetItem("Yes" if income.is_recurring else "No"))
    
    def add_income(self):
        """Add a new income record."""
        try:
            amount = float(self.amount_input.text())
            category_id = self.category_combo.currentData()
            description = self.description_input.text()
            date = self.date_input.date().toPython()
            is_recurring = self.recurring_checkbox.isChecked()
            
            self.personal_finance_service.create_income(
                amount=amount,
                category_id=category_id,
                description=description,
                date=date,
                is_recurring=is_recurring
            )
            
            # Refresh table
            self.load_income_data()
            self.amount_input.clear()
            self.description_input.clear()
            
            QMessageBox.information(self, "Success", "Income record added successfully!")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add income: {str(e)}")

class ExpenseTab(QWidget):
    """Tab for expense tracking."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the expense tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
        self.load_expense_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Input form
        form_layout = QGridLayout()
        
        # Category
        category_label = QLabel("Category:")
        self.expense_category_combo = QComboBox()
        form_layout.addWidget(category_label, 0, 0)
        form_layout.addWidget(self.expense_category_combo, 0, 1)
        
        # Amount
        amount_label = QLabel("Amount:")
        self.expense_amount_input = QLineEdit()
        form_layout.addWidget(amount_label, 1, 0)
        form_layout.addWidget(self.expense_amount_input, 1, 1)
        
        # Description
        description_label = QLabel("Description:")
        self.expense_description_input = QLineEdit()
        form_layout.addWidget(description_label, 2, 0)
        form_layout.addWidget(self.expense_description_input, 2, 1)
        
        # Date
        date_label = QLabel("Date:")
        self.expense_date_input = QDateEdit()
        self.expense_date_input.setCalendarPopup(True)
        self.expense_date_input.setDate(QDate.currentDate())
        form_layout.addWidget(date_label, 3, 0)
        form_layout.addWidget(self.expense_date_input, 3, 1)
        
        # Recurring
        self.expense_recurring_checkbox = QCheckBox("Recurring")
        form_layout.addWidget(self.expense_recurring_checkbox, 4, 1)
        
        # Add button
        add_button = QPushButton("Add Expense")
        add_button.clicked.connect(self.add_expense)
        form_layout.addWidget(add_button, 5, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Expense table
        self.expense_table = QTableWidget(0, 5)
        self.expense_table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Description", "Recurring"])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expense_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.expense_table)
        
        # Load categories
        self.load_categories()
    
    def load_categories(self):
        """Load expense categories into combo box."""
        categories = self.personal_finance_service.get_expense_categories()
        self.expense_category_combo.clear()
        for category in categories:
            self.expense_category_combo.addItem(category.name, category.id)
    
    def load_expense_data(self):
        """Load expense data into table."""
        expenses = self.personal_finance_service.get_expenses()
        self.expense_table.setRowCount(len(expenses))
        
        for i, expense in enumerate(expenses):
            self.expense_table.setItem(i, 0, QTableWidgetItem(expense.date.strftime("%Y-%m-%d")))
            self.expense_table.setItem(i, 1, QTableWidgetItem(expense.category.name))
            self.expense_table.setItem(i, 2, QTableWidgetItem(f"${expense.amount:.2f}"))
            self.expense_table.setItem(i, 3, QTableWidgetItem(expense.description or ""))
            self.expense_table.setItem(i, 4, QTableWidgetItem("Yes" if expense.is_recurring else "No"))
    
    def add_expense(self):
        """Add a new expense record."""
        try:
            amount = float(self.expense_amount_input.text())
            category_id = self.expense_category_combo.currentData()
            description = self.expense_description_input.text()
            date = self.expense_date_input.date().toPython()
            is_recurring = self.expense_recurring_checkbox.isChecked()
            
            self.personal_finance_service.create_expense(
                amount=amount,
                category_id=category_id,
                description=description,
                date=date,
                is_recurring=is_recurring
            )
            
            # Refresh table
            self.load_expense_data()
            self.expense_amount_input.clear()
            self.expense_description_input.clear()
            
            QMessageBox.information(self, "Success", "Expense record added successfully!")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add expense: {str(e)}")

class BudgetTab(QWidget):
    """Tab for budget management."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the budget tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
        self.load_budget_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Input form
        form_layout = QGridLayout()
        
        # Category
        category_label = QLabel("Category:")
        self.budget_category_combo = QComboBox()
        form_layout.addWidget(category_label, 0, 0)
        form_layout.addWidget(self.budget_category_combo, 0, 1)
        
        # Month
        month_label = QLabel("Month:")
        self.month_input = QComboBox()
        self.month_input.addItems(["January", "February", "March", "April", "May", "June",
                                  "July", "August", "September", "October", "November", "December"])
        form_layout.addWidget(month_label, 1, 0)
        form_layout.addWidget(self.month_input, 1, 1)
        
        # Year
        year_label = QLabel("Year:")
        self.year_input = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 3):
            self.year_input.addItem(str(year))
        self.year_input.setCurrentText(str(current_year))
        form_layout.addWidget(year_label, 2, 0)
        form_layout.addWidget(self.year_input, 2, 1)
        
        # Budget Limit
        limit_label = QLabel("Budget Limit:")
        self.budget_limit_input = QLineEdit()
        form_layout.addWidget(limit_label, 3, 0)
        form_layout.addWidget(self.budget_limit_input, 3, 1)
        
        # Add button
        add_button = QPushButton("Set Budget")
        add_button.clicked.connect(self.set_budget)
        form_layout.addWidget(add_button, 4, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Budget table
        self.budget_table = QTableWidget(0, 4)
        self.budget_table.setHorizontalHeaderLabels(["Category", "Month", "Budget Limit", "Status"])
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.budget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.budget_table)
        
        # Load categories
        self.load_categories()
    
    def load_categories(self):
        """Load expense categories into combo box."""
        categories = self.personal_finance_service.get_expense_categories()
        self.budget_category_combo.clear()
        for category in categories:
            self.budget_category_combo.addItem(category.name, category.id)
    
    def load_budget_data(self):
        """Load budget data into table."""
        budgets = self.personal_finance_service.get_budgets()
        self.budget_table.setRowCount(len(budgets))
        
        for i, budget in enumerate(budgets):
            category = self.personal_finance_service.get_expense_categories()
            category_name = next((c.name for c in category if c.id == budget.category_id), "Unknown")
            self.budget_table.setItem(i, 0, QTableWidgetItem(category_name))
            self.budget_table.setItem(i, 1, QTableWidgetItem(budget.month))
            self.budget_table.setItem(i, 2, QTableWidgetItem(f"${budget.budget_limit:.2f}"))
            
            # Calculate status (simplified - in real app would compare with actual expenses)
            status = "Under Budget"  # Simplified
            self.budget_table.setItem(i, 3, QTableWidgetItem(status))
    
    def set_budget(self):
        """Set a budget for an expense category."""
        try:
            category_id = self.budget_category_combo.currentData()
            month = self.month_input.currentText()
            year = self.year_input.currentText()
            budget_limit = float(self.budget_limit_input.text())
            
            # Format month and year into YYYY-MM
            month_num = self.month_input.currentIndex() + 1
            month_year = f"{year}-{month_num:02d}"
            
            self.personal_finance_service.create_budget(
                category_id=category_id,
                month=month_year,
                budget_limit=budget_limit
            )
            
            # Refresh table
            self.load_budget_data()
            self.budget_limit_input.clear()
            
            QMessageBox.information(self, "Success", "Budget set successfully!")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid budget amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set budget: {str(e)}")

class GoalsTab(QWidget):
    """Tab for financial goals tracking."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the goals tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
        self.load_goals_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Input form
        form_layout = QGridLayout()
        
        # Title
        title_label = QLabel("Goal Title:")
        self.title_input = QLineEdit()
        form_layout.addWidget(title_label, 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)
        
        # Description
        description_label = QLabel("Description:")
        self.description_input = QLineEdit()
        form_layout.addWidget(description_label, 1, 0)
        form_layout.addWidget(self.description_input, 1, 1)
        
        # Target Amount
        amount_label = QLabel("Target Amount:")
        self.amount_input = QLineEdit()
        form_layout.addWidget(amount_label, 2, 0)
        form_layout.addWidget(self.amount_input, 2, 1)
        
        # Deadline
        deadline_label = QLabel("Deadline:")
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        form_layout.addWidget(deadline_label, 3, 0)
        form_layout.addWidget(self.deadline_input, 3, 1)
        
        # Add button
        add_button = QPushButton("Add Goal")
        add_button.clicked.connect(self.add_goal)
        form_layout.addWidget(add_button, 4, 0, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Goals table
        self.goals_table = QTableWidget(0, 5)
        self.goals_table.setHorizontalHeaderLabels(["Title", "Amount", "Deadline", "Progress", "Status"])
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.goals_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.goals_table)
    
    def load_goals_data(self):
        """Load goals data into table."""
        goals = self.personal_finance_service.get_financial_goals()
        self.goals_table.setRowCount(len(goals))
        
        for i, goal in enumerate(goals):
            self.goals_table.setItem(i, 0, QTableWidgetItem(goal.title))
            self.goals_table.setItem(i, 1, QTableWidgetItem(f"${goal.target_amount:.2f}"))
            self.goals_table.setItem(i, 2, QTableWidgetItem(goal.deadline.strftime("%Y-%m-%d") if goal.deadline else ""))
            
            progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            self.goals_table.setItem(i, 3, QTableWidgetItem(f"{progress:.1f}%"))
            
            status = "Completed" if goal.is_completed else "In Progress"
            self.goals_table.setItem(i, 4, QTableWidgetItem(status))
    
    def add_goal(self):
        """Add a new financial goal."""
        try:
            title = self.title_input.text()
            description = self.description_input.text()
            target_amount = float(self.amount_input.text())
            deadline = self.deadline_input.date().toPython()
            
            self.personal_finance_service.create_financial_goal(
                title=title,
                description=description,
                target_amount=target_amount,
                deadline=deadline
            )
            
            # Refresh table
            self.load_goals_data()
            self.title_input.clear()
            self.description_input.clear()
            self.amount_input.clear()
            
            QMessageBox.information(self, "Success", "Financial goal added successfully!")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid target amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add goal: {str(e)}")

class SummaryTab(QWidget):
    """Tab for financial summary."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService):
        """Initialize the summary tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Summary information
        summary_group = QGroupBox("Monthly Summary")
        summary_layout = QGridLayout(summary_group)
        
        # Current month
        current_month_label = QLabel("Current Month:")
        self.current_month_label = QLabel()
        summary_layout.addWidget(current_month_label, 0, 0)
        summary_layout.addWidget(self.current_month_label, 0, 1)
        
        # Income
        income_label = QLabel("Total Income:")
        self.income_label = QLabel("$0.00")
        summary_layout.addWidget(income_label, 1, 0)
        summary_layout.addWidget(self.income_label, 1, 1)
        
        # Expenses
        expenses_label = QLabel("Total Expenses:")
        self.expenses_label = QLabel("$0.00")
        summary_layout.addWidget(expenses_label, 2, 0)
        summary_layout.addWidget(self.expenses_label, 2, 1)
        
        # Net
        net_label = QLabel("Net:")
        self.net_label = QLabel("$0.00")
        summary_layout.addWidget(net_label, 3, 0)
        summary_layout.addWidget(self.net_label, 3, 1)
        
        layout.addWidget(summary_group)
        
        # Load current summary
        self.update_summary()
    
    def update_summary(self):
        """Update the summary information."""
        # In a real implementation, this would fetch actual data from the service
        # For now, just show placeholder information
        current_date = datetime.now()
        self.current_month_label.setText(current_date.strftime("%B %Y"))
        self.income_label.setText("$2,500.00")
        self.expenses_label.setText("$1,800.00")
        self.net_label.setText("$700.00")