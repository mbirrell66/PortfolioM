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
from services.portfolio_service import PortfolioService
from database.personal_finance_models import IncomeCategory, ExpenseCategory


_TAB_SS = """
    QWidget { background-color: #0F1117; }
    QTabWidget::pane {
        background-color: #0F1117;
        border: 1px solid #222844;
        border-radius: 8px;
        margin-top: -1px;
    }
    QTabBar::tab {
        background-color: #191D2E; color: #7488B8;
        padding: 10px 20px; font-size: 13px; font-weight: 500;
        border: 1px solid #222844; border-bottom: none;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        margin-right: 4px;
    }
    QTabBar::tab:selected { background-color: #0F1117; color: #5295FF; font-weight: 600; }
    QTabBar::tab:hover { color: #5295FF; }
    QLabel { color: #7488B8; font-size: 13px; }
    QGroupBox {
        color: #7488B8; font-size: 12px; font-weight: 600;
        border: 1px solid #222844; border-radius: 6px;
        margin-top: 8px; padding-top: 8px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
    QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QComboBox {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px;
        padding: 6px 10px; font-size: 13px;
    }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus,
    QDoubleSpinBox:focus, QSpinBox:focus { border-color: #5295FF; }
    QComboBox::drop-down, QDateEdit::drop-down,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
    QSpinBox::up-button, QSpinBox::down-button { background-color: #222844; border: none; }
    QComboBox QAbstractItemView {
        background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;
        selection-background-color: rgba(74, 158, 255, 0.25);
    }
    QCheckBox { color: #DDE8FF; font-size: 13px; }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border: 1px solid #222844; border-radius: 3px; background-color: #191D2E;
    }
    QCheckBox::indicator:checked { background-color: #5295FF; border-color: #5295FF; }
    QPushButton {
        background-color: #5295FF; color: #0F1117; border: none;
        border-radius: 6px; padding: 8px 20px; font-size: 13px;
        font-weight: 600; min-width: 80px;
    }
    QPushButton:hover { background-color: #4080EE; }
    QPushButton:pressed { background-color: #327AE0; }
    QTableWidget, QTableView {
        background-color: #0F1117; alternate-background-color: #161928;
        color: #DDE8FF; gridline-color: transparent; border: none;
        selection-background-color: rgba(74, 158, 255, 0.25);
        selection-color: #DDE8FF; outline: none;
    }
    QTableWidget::item, QTableView::item { padding: 6px 10px; border: none; }
    QTableWidget::item:hover, QTableView::item:hover {
        background-color: rgba(74, 158, 255, 0.12);
    }
    QHeaderView::section {
        background-color: #191D2E; color: #7488B8;
        padding: 8px 10px; font-size: 11px; font-weight: 600;
        border: none; border-right: 1px solid #222844;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    QHeaderView::section:last { border-right: none; }
    QTextEdit {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px; font-size: 13px;
    }
    QSplitter::handle { background-color: #222844; }
    QProgressBar {
        background-color: #191D2E; border: 1px solid #222844; border-radius: 4px;
        color: #DDE8FF; text-align: center;
    }
    QProgressBar::chunk { background-color: #5295FF; border-radius: 3px; }
"""
class PersonalFinanceTab(QWidget):
    """Main tab for personal finance tracking."""
    
    def __init__(self, personal_finance_service: PersonalFinanceService,
                 portfolio_service=None):
        """Initialize the personal finance tab."""
        super().__init__()
        self.personal_finance_service = personal_finance_service
        self.portfolio_service = portfolio_service
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setStyleSheet(_TAB_SS)
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

        # Add ledger tab
        ledger_tab = LedgerTab(self.personal_finance_service, self.portfolio_service)
        tab_widget.addTab(ledger_tab, "Ledger")

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
        self.setStyleSheet(_TAB_SS)
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
        self.income_table.setAlternatingRowColors(True)
        self.income_table.setShowGrid(False)
        self.income_table.verticalHeader().setVisible(False)
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
        self.setStyleSheet(_TAB_SS)
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
        self.expense_table.setAlternatingRowColors(True)
        self.expense_table.setShowGrid(False)
        self.expense_table.verticalHeader().setVisible(False)
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
        self.setStyleSheet(_TAB_SS)
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
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.setShowGrid(False)
        self.budget_table.verticalHeader().setVisible(False)
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
        self.setStyleSheet(_TAB_SS)
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
        self.goals_table.setAlternatingRowColors(True)
        self.goals_table.setShowGrid(False)
        self.goals_table.verticalHeader().setVisible(False)
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
        self.setStyleSheet(_TAB_SS)
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


class LedgerTab(QWidget):
    """Full financial ledger — portfolio buys/sells, dividends, income, expenses,
    plus manually added deposits and withdrawals."""

    def __init__(self, personal_finance_service: PersonalFinanceService,
                 portfolio_service=None):
        super().__init__()
        self.pf_service = personal_finance_service
        self.port_service = portfolio_service
        self._all_rows = []      # (date, type, desc, debit, credit, balance, notes, ledger_id)
        self._visible_rows = []  # filtered subset, parallel to table rows
        self.setup_ui()
        self.load_data()

    # ------------------------------------------------------------------
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Toolbar row
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All", "Deposit", "Withdrawal",
            "Buy", "Sell", "Dividend", "Income", "Expense",
        ])
        self.type_filter.currentIndexChanged.connect(self._apply_filter)
        toolbar.addWidget(self.type_filter)
        toolbar.addStretch()

        add_btn = QPushButton("+ Add Transaction")
        add_btn.setToolTip("Record a deposit or withdrawal")
        add_btn.clicked.connect(self._add_transaction)
        toolbar.addWidget(add_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setToolTip("Delete the selected deposit / withdrawal")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_transaction)
        toolbar.addWidget(self.delete_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        # Summary strip
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(
            "color: #DDE8FF; font-size: 12px; padding: 4px 0;"
        )
        layout.addWidget(self.summary_label)

        # Ledger table
        self.ledger_table = QTableWidget(0, 7)
        self.ledger_table.setHorizontalHeaderLabels(
            ["Date", "Type", "Description", "Debit", "Credit", "Balance", "Notes"]
        )
        self.ledger_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ledger_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ledger_table.setSelectionMode(QTableWidget.SingleSelection)
        self.ledger_table.setAlternatingRowColors(True)
        self.ledger_table.setShowGrid(False)
        self.ledger_table.verticalHeader().setVisible(False)
        self.ledger_table.horizontalHeader().setStretchLastSection(True)
        self.ledger_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.ledger_table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.ledger_table)

    # ------------------------------------------------------------------
    def load_data(self):
        """Collect all transactions and display chronologically."""
        # (date, type, desc, debit, credit, notes, ledger_id_or_None)
        rows = []

        # --- portfolio buys / sells ---
        if self.port_service:
            try:
                for pos in self.port_service.get_positions():
                    buy_comm = pos.buy_commission or 0.0
                    amount = pos.purchase_price * pos.shares + buy_comm
                    desc = f"{pos.ticker} — {pos.shares} sh @ ${pos.purchase_price:.2f}"
                    if buy_comm:
                        desc += f"  +comm ${buy_comm:.2f}"
                    rows.append((pos.purchase_date, "Buy", desc,
                                 amount, 0.0, pos.notes or "", None))
                    if pos.sell_date:
                        sell_comm = pos.sell_commission or 0.0
                        proceeds = (pos.sell_price or 0.0) * pos.shares - sell_comm
                        sdesc = (f"{pos.ticker} — {pos.shares} sh"
                                 f" @ ${pos.sell_price:.2f}")
                        if sell_comm:
                            sdesc += f"  −comm ${sell_comm:.2f}"
                        rows.append((pos.sell_date, "Sell", sdesc,
                                     0.0, proceeds, "", None))
            except Exception as e:
                print(f"Ledger positions error: {e}")

            # --- dividends ---
            try:
                from database.models import DividendEvent
                from database.database import SessionLocal as _SL
                db = _SL()
                try:
                    for div in db.query(DividendEvent).all():
                        rows.append((div.payment_date, "Dividend",
                                     f"{div.ticker} dividend",
                                     0.0, div.cash_received, "", None))
                finally:
                    db.close()
            except Exception as e:
                print(f"Ledger dividends error: {e}")

        # --- income / expenses ---
        try:
            from database.personal_finance_models import Income, Expense
            from database.database import SessionLocal as _SL
            db = _SL()
            try:
                for inc in db.query(Income).all():
                    cat = inc.category.name if inc.category else "Income"
                    dt = inc.date.date() if hasattr(inc.date, 'date') else inc.date
                    rows.append((dt, "Income",
                                 f"{cat}: {inc.description or ''}",
                                 0.0, inc.amount, "", None))
                for exp in db.query(Expense).all():
                    cat = exp.category.name if exp.category else "Expense"
                    dt = exp.date.date() if hasattr(exp.date, 'date') else exp.date
                    rows.append((dt, "Expense",
                                 f"{cat}: {exp.description or ''}",
                                 exp.amount, 0.0, "", None))
            finally:
                db.close()
        except Exception as e:
            print(f"Ledger income/expense error: {e}")

        # --- manual deposits / withdrawals ---
        try:
            from database.personal_finance_models import LedgerTransaction
            from database.database import SessionLocal as _SL
            db = _SL()
            try:
                for txn in db.query(LedgerTransaction).all():
                    dt = txn.date.date() if hasattr(txn.date, 'date') else txn.date
                    if txn.transaction_type == "Deposit":
                        rows.append((dt, "Deposit",
                                     txn.description or "Deposit",
                                     0.0, txn.amount, txn.notes or "", txn.id))
                    else:
                        rows.append((dt, "Withdrawal",
                                     txn.description or "Withdrawal",
                                     txn.amount, 0.0, txn.notes or "", txn.id))
            finally:
                db.close()
        except Exception as e:
            print(f"Ledger transactions error: {e}")

        # Sort chronologically
        import datetime as _dt
        rows.sort(key=lambda r: r[0] if r[0] else _dt.date.min)

        # Build running balance (8-tuple: add balance after notes)
        self._all_rows = []
        balance = 0.0
        for dt, rtype, desc, debit, credit, notes, lid in rows:
            balance += credit - debit
            self._all_rows.append(
                (dt, rtype, desc, debit, credit, balance, notes, lid)
            )

        self._apply_filter()
        self._update_summary()

    # ------------------------------------------------------------------
    def _apply_filter(self):
        selected = self.type_filter.currentText()
        self._visible_rows = [
            r for r in self._all_rows
            if selected == "All" or r[1] == selected
        ]
        self.ledger_table.setRowCount(0)
        self.delete_btn.setEnabled(False)

        type_colors = {
            "Buy":        "#FF5068",
            "Sell":       "#38D88A",
            "Dividend":   "#5295FF",
            "Income":     "#38D88A",
            "Expense":    "#FF5068",
            "Deposit":    "#38D88A",
            "Withdrawal": "#FF5068",
        }

        from PySide6.QtGui import QColor as _QC
        for dt, rtype, desc, debit, credit, balance, notes, lid in self._visible_rows:
            row = self.ledger_table.rowCount()
            self.ledger_table.insertRow(row)
            date_str   = dt.strftime("%Y-%m-%d") if hasattr(dt, 'strftime') else str(dt)
            debit_str  = f"${debit:.2f}"   if debit  else ""
            credit_str = f"${credit:.2f}"  if credit else ""
            bal_str    = f"${balance:.2f}"

            for col, val in enumerate(
                [date_str, rtype, desc, debit_str, credit_str, bal_str, notes]
            ):
                item = QTableWidgetItem(val)
                if col == 1:
                    item.setForeground(_QC(type_colors.get(rtype, "#DDE8FF")))
                if col in (3, 4, 5):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if col == 5:
                    item.setForeground(
                        _QC("#38D88A") if balance >= 0 else _QC("#FF5068")
                    )
                self.ledger_table.setItem(row, col, item)

    # ------------------------------------------------------------------
    def _on_selection_changed(self):
        """Enable Delete only when a manual transaction is selected."""
        rows = self.ledger_table.selectedItems()
        if not rows:
            self.delete_btn.setEnabled(False)
            return
        row_idx = self.ledger_table.currentRow()
        if row_idx < len(self._visible_rows):
            lid = self._visible_rows[row_idx][7]   # ledger_id
            self.delete_btn.setEnabled(lid is not None)
        else:
            self.delete_btn.setEnabled(False)

    # ------------------------------------------------------------------
    def _add_transaction(self):
        dialog = _LedgerTransactionDialog(self)
        if dialog.exec():
            txn_type, desc, amount, dt, notes = dialog.get_data()
            try:
                from database.personal_finance_models import LedgerTransaction
                from database.database import SessionLocal as _SL
                import datetime as _dt
                db = _SL()
                try:
                    txn = LedgerTransaction(
                        date=_dt.datetime.combine(dt, _dt.time.min),
                        transaction_type=txn_type,
                        description=desc,
                        amount=amount,
                        notes=notes,
                    )
                    db.add(txn)
                    db.commit()
                finally:
                    db.close()
                self.load_data()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox as _MB
                _MB.critical(self, "Error", f"Failed to save transaction: {e}")

    # ------------------------------------------------------------------
    def _delete_transaction(self):
        row_idx = self.ledger_table.currentRow()
        if row_idx < 0 or row_idx >= len(self._visible_rows):
            return
        lid = self._visible_rows[row_idx][7]
        if lid is None:
            return
        from PySide6.QtWidgets import QMessageBox as _MB
        reply = _MB.question(
            self, "Delete Transaction",
            "Delete this transaction? This cannot be undone.",
            _MB.Yes | _MB.No, _MB.No
        )
        if reply != _MB.Yes:
            return
        try:
            from database.personal_finance_models import LedgerTransaction
            from database.database import SessionLocal as _SL
            db = _SL()
            try:
                txn = db.query(LedgerTransaction).filter(
                    LedgerTransaction.id == lid
                ).first()
                if txn:
                    db.delete(txn)
                    db.commit()
            finally:
                db.close()
            self.load_data()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox as _MB2
            _MB2.critical(self, "Error", f"Failed to delete transaction: {e}")

    # ------------------------------------------------------------------
    def _update_summary(self):
        if not self._all_rows:
            self.summary_label.setText("")
            return
        total_in  = sum(r[4] for r in self._all_rows)
        total_out = sum(r[3] for r in self._all_rows)
        net = self._all_rows[-1][5] if self._all_rows else 0.0
        col = "#38D88A" if net >= 0 else "#FF5068"
        self.summary_label.setText(
            f"Total In: <b style='color:#38D88A'>${total_in:,.2f}</b>"
            f"&nbsp;&nbsp;Total Out: <b style='color:#FF5068'>${total_out:,.2f}</b>"
            f"&nbsp;&nbsp;Net Balance: <b style='color:{col}'>${net:,.2f}</b>"
        )
        self.summary_label.setTextFormat(Qt.RichText)


# ---------------------------------------------------------------------------

class _LedgerTransactionDialog(QDialog if 'QDialog' in dir() else object):
    pass

# Replace the stub above with the real implementation
import importlib as _il
from PySide6.QtWidgets import (QDialog as _QD, QVBoxLayout as _QVL,
                                QFormLayout as _QFL, QComboBox as _QCB,
                                QLineEdit as _QLI, QDoubleSpinBox as _QDSP,
                                QDateEdit as _QDE, QTextEdit as _QTE,
                                QDialogButtonBox as _QDBB, QGroupBox as _QGB)
from PySide6.QtCore import QDate as _QDA

class _LedgerTransactionDialog(_QD):
    """Small dialog to enter a deposit or withdrawal."""

    _SS = """
        QDialog { background-color: #0F1117; }
        QLabel { color: #7488B8; font-size: 13px; }
        QGroupBox {
            color: #7488B8; font-size: 12px; font-weight: 600;
            border: 1px solid #222844; border-radius: 6px;
            margin-top: 8px; padding-top: 8px;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QComboBox, QDateEdit, QDoubleSpinBox, QLineEdit, QTextEdit {
            background-color: #191D2E; color: #DDE8FF;
            border: 1px solid #222844; border-radius: 6px;
            padding: 6px 10px; font-size: 13px;
        }
        QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus,
        QLineEdit:focus, QTextEdit:focus { border-color: #5295FF; }
        QComboBox::drop-down, QDateEdit::drop-down,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background-color: #222844; border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;
            selection-background-color: rgba(74,158,255,0.25);
        }
        QDialogButtonBox QPushButton {
            background-color: #5295FF; color: #0F1117; border: none;
            border-radius: 6px; padding: 8px 20px; font-size: 13px;
            font-weight: 600; min-width: 80px;
        }
        QDialogButtonBox QPushButton:hover { background-color: #4080EE; }
        QDialogButtonBox QPushButton:pressed { background-color: #327AE0; }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setStyleSheet(self._SS)
        self._build()

    def _build(self):
        layout = _QVL(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        grp = _QGB("Transaction Details")
        form = _QFL(grp)
        form.setSpacing(8)

        self.type_combo = _QCB()
        self.type_combo.addItems(["Deposit", "Withdrawal"])

        self.date_edit = _QDE()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(_QDA.currentDate())

        self.desc_input = _QLI()
        self.desc_input.setPlaceholderText("e.g., Bank transfer")

        self.amount_spin = _QDSP()
        self.amount_spin.setRange(0.01, 99_999_999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$")

        self.notes_input = _QTE()
        self.notes_input.setMaximumHeight(70)
        self.notes_input.setPlaceholderText("Optional notes")

        form.addRow("Type *", self.type_combo)
        form.addRow("Date *", self.date_edit)
        form.addRow("Description", self.desc_input)
        form.addRow("Amount *", self.amount_spin)
        form.addRow("Notes", self.notes_input)
        layout.addWidget(grp)

        btn_box = _QDBB(_QDBB.Ok | _QDBB.Cancel)
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        from PySide6.QtWidgets import QMessageBox as _MB
        if self.amount_spin.value() <= 0:
            _MB.warning(self, "Validation", "Amount must be greater than zero.")
            return
        self.accept()

    def get_data(self):
        return (
            self.type_combo.currentText(),
            self.desc_input.text().strip(),
            self.amount_spin.value(),
            self.date_edit.date().toPython(),
            self.notes_input.toPlainText().strip(),
        )
