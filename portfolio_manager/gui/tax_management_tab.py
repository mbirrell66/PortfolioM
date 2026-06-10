"""
Tax Management Tab
GUI component for tax tracking and reporting.
"""
from PySide6.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableView, QPushButton, QFormLayout, QLabel,
                             QDateEdit, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QGroupBox, QCheckBox, QHeaderView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from datetime import date
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.tax_event_dialog import TaxEventDialog
from gui.capital_gains_dialog import CapitalGainsDialog
from services.tax_service import TaxService

class TaxManagementTab(QWidget):
    """Tax management tab for tracking tax events and reporting."""
    
    def __init__(self, tax_service: TaxService):
        """Initialize the tax management tab."""
        super().__init__()
        self.tax_service = tax_service
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different tax sections
        tab_widget = QTabWidget()
        
        # Tax Events Tab
        tax_events_tab = self.create_tax_events_tab()
        tab_widget.addTab(tax_events_tab, "Tax Events")
        
        # Capital Gains Tab
        capital_gains_tab = self.create_capital_gains_tab()
        tab_widget.addTab(capital_gains_tab, "Capital Gains")
        
        # Tax Returns Tab
        tax_returns_tab = self.create_tax_returns_tab()
        tab_widget.addTab(tax_returns_tab, "Tax Returns")
        
        # Tax Summary Tab
        summary_tab = self.create_summary_tab()
        tab_widget.addTab(summary_tab, "Summary")
        
        layout.addWidget(tab_widget)
    
    def create_tax_events_tab(self):
        """Create the tax events tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create input form
        form_group = QGroupBox("Add New Tax Event")
        form_layout = QFormLayout(form_group)
        
        self.title_input = QLineEdit()
        self.description_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        self.category_combo = QComboBox()
        self.tax_rate_input = QLineEdit()
        self.deductible_checkbox = QCheckBox("Deductible")
        
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Amount ($):", self.amount_input)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Tax Rate (%):", self.tax_rate_input)
        form_layout.addRow("Deductible:", self.deductible_checkbox)
        
        # Add button
        add_btn = QPushButton("Add Tax Event")
        add_btn.clicked.connect(self.add_tax_event)
        
        # Create table for existing events
        self.tax_events_table = QTableWidget(0, 6)
        self.tax_events_table.setHorizontalHeaderLabels([
            "Title", "Category", "Amount", "Date", "Tax Rate", "Tax Amount"
        ])
        self.tax_events_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(form_group)
        layout.addWidget(add_btn)
        layout.addWidget(self.tax_events_table)
        
        return tab
    
    def create_capital_gains_tab(self):
        """Create the capital gains tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create input form
        form_group = QGroupBox("Add Capital Gains Event")
        form_layout = QFormLayout(form_group)
        
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems(["Shares", "Property", "Other"])
        
        self.acquisition_date_input = QDateEdit()
        self.acquisition_date_input.setDisplayFormat("dd/MM/yyyy")
        self.acquisition_date_input.setCalendarPopup(True)
        self.acquisition_date_input.setDate(QDate.currentDate())
        
        self.disposal_date_input = QDateEdit()
        self.disposal_date_input.setDisplayFormat("dd/MM/yyyy")
        self.disposal_date_input.setCalendarPopup(True)
        self.disposal_date_input.setDate(QDate.currentDate())
        
        self.acquisition_cost_input = QLineEdit()
        self.proceeds_input = QLineEdit()
        self.exempt_checkbox = QCheckBox("Exempt from CGT")
        
        form_layout.addRow("Asset Type:", self.asset_type_combo)
        form_layout.addRow("Acquisition Date:", self.acquisition_date_input)
        form_layout.addRow("Disposal Date:", self.disposal_date_input)
        form_layout.addRow("Acquisition Cost ($):", self.acquisition_cost_input)
        form_layout.addRow("Proceeds ($):", self.proceeds_input)
        form_layout.addRow("Exempt from CGT:", self.exempt_checkbox)
        
        # Add button
        add_btn = QPushButton("Add Capital Gains Event")
        add_btn.clicked.connect(self.add_capital_gains_event)
        
        # Create table for existing events
        self.capital_gains_table = QTableWidget(0, 7)
        self.capital_gains_table.setHorizontalHeaderLabels([
            "Asset Type", "Acquisition Date", "Disposal Date", "Gain", "Tax Rate", "Tax Liability", "Exempt"
        ])
        self.capital_gains_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(form_group)
        layout.addWidget(add_btn)
        layout.addWidget(self.capital_gains_table)
        
        return tab
    
    def create_tax_returns_tab(self):
        """Create the tax returns tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tax return creation
        form_group = QGroupBox("Create Tax Return")
        form_layout = QFormLayout(form_group)
        
        self.tax_year_input = QLineEdit()
        self.tax_year_input.setText("2023-2024")
        
        self.filing_date_input = QDateEdit()
        self.filing_date_input.setDisplayFormat("dd/MM/yyyy")
        self.filing_date_input.setCalendarPopup(True)
        self.filing_date_input.setDate(QDate.currentDate())
        
        form_layout.addRow("Tax Year:", self.tax_year_input)
        form_layout.addRow("Filing Date:", self.filing_date_input)
        
        create_btn = QPushButton("Create Tax Return")
        create_btn.clicked.connect(self.create_tax_return)
        
        # Create table for existing returns
        self.tax_returns_table = QTableWidget(0, 5)
        self.tax_returns_table.setHorizontalHeaderLabels([
            "Tax Year", "Filing Date", "Status", "Income", "Tax Liability"
        ])
        self.tax_returns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(form_group)
        layout.addWidget(create_btn)
        layout.addWidget(self.tax_returns_table)
        
        return tab
    
    def create_summary_tab(self):
        """Create the summary tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary information
        summary_group = QGroupBox("Tax Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_label = QLabel("Select date range to view summary")
        self.summary_label.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        self.summary_label.setFont(font)
        
        # Date range selection
        date_layout = QHBoxLayout()
        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("dd/MM/yyyy")
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addDays(-30))
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat("dd/MM/yyyy")
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        
        self.refresh_summary_btn = QPushButton("Refresh Summary")
        self.refresh_summary_btn.clicked.connect(self.refresh_summary)
        
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date_input)
        date_layout.addWidget(self.refresh_summary_btn)
        date_layout.addStretch()
        
        summary_layout.addWidget(self.summary_label)
        summary_layout.addLayout(date_layout)
        
        layout.addWidget(summary_group)
        
        return tab
    
    def load_data(self):
        """Load tax data into the UI."""
        # Load tax categories
        categories = self.tax_service.get_tax_categories()
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
        
        # Load existing tax events
        self.load_tax_events()
        
        # Load capital gains events
        self.load_capital_gains()
        
        # Load tax returns
        self.load_tax_returns()
    
    def load_tax_events(self):
        """Load tax events into the table."""
        events = self.tax_service.get_tax_events()
        self.tax_events_table.setRowCount(len(events))
        
        for i, event in enumerate(events):
            self.tax_events_table.setItem(i, 0, QTableWidgetItem(event.title))
            self.tax_events_table.setItem(i, 1, QTableWidgetItem(event.category.name if event.category else "N/A"))
            self.tax_events_table.setItem(i, 2, QTableWidgetItem(f"${event.amount:.2f}"))
            self.tax_events_table.setItem(i, 3, QTableWidgetItem(event.date.strftime("%d/%m/%Y")))
            self.tax_events_table.setItem(i, 4, QTableWidgetItem(f"{event.tax_rate}%"))
            self.tax_events_table.setItem(i, 5, QTableWidgetItem(f"${event.tax_amount:.2f}"))
    
    def load_capital_gains(self):
        """Load capital gains events into the table."""
        events = self.tax_service.get_capital_gains_events()
        self.capital_gains_table.setRowCount(len(events))
        
        for i, event in enumerate(events):
            self.capital_gains_table.setItem(i, 0, QTableWidgetItem(event.asset_type))
            self.capital_gains_table.setItem(i, 1, QTableWidgetItem(event.acquisition_date.strftime("%d/%m/%Y")))
            self.capital_gains_table.setItem(i, 2, QTableWidgetItem(event.disposal_date.strftime("%d/%m/%Y")))
            self.capital_gains_table.setItem(i, 3, QTableWidgetItem(f"${event.capital_gain:.2f}"))
            self.capital_gains_table.setItem(i, 4, QTableWidgetItem(f"{event.tax_rate}%"))
            self.capital_gains_table.setItem(i, 5, QTableWidgetItem(f"${event.tax_liability:.2f}"))
            self.capital_gains_table.setItem(i, 6, QTableWidgetItem("Yes" if event.is_exempt else "No"))
    
    def load_tax_returns(self):
        """Load tax returns into the table."""
        returns = self.tax_service.get_tax_returns()
        self.tax_returns_table.setRowCount(len(returns))
        
        for i, tax_return in enumerate(returns):
            self.tax_returns_table.setItem(i, 0, QTableWidgetItem(tax_return.tax_year))
            self.tax_returns_table.setItem(i, 1, QTableWidgetItem(tax_return.filing_date.strftime("%d/%m/%Y") if tax_return.filing_date else "N/A"))
            self.tax_returns_table.setItem(i, 2, QTableWidgetItem(tax_return.status))
            self.tax_returns_table.setItem(i, 3, QTableWidgetItem(f"${tax_return.total_income:.2f}"))
            self.tax_returns_table.setItem(i, 4, QTableWidgetItem(f"${tax_return.total_tax_owed:.2f}"))
    
    def add_tax_event(self):
        """Add a new tax event."""
        title = self.title_input.text()
        description = self.description_input.text()
        try:
            amount = float(self.amount_input.text())
            tax_rate = float(self.tax_rate_input.text()) if self.tax_rate_input.text() else 0.0
        except ValueError:
            # Show error dialog
            return
        
        date_value = self.date_input.date()
        selected_date = date_value.toPython()
        category_id = self.category_combo.currentData()
        is_deductible = self.deductible_checkbox.isChecked()
        
        try:
            self.tax_service.create_tax_event(
                category_id=category_id,
                title=title,
                description=description,
                amount=amount,
                date=selected_date,
                tax_rate=tax_rate,
                is_deductible=is_deductible
            )
            # Reload data
            self.load_tax_events()
            self.clear_tax_event_inputs()
        except Exception as e:
            # Show error dialog
            print(f"Error adding tax event: {e}")
    
    def add_capital_gains_event(self):
        """Add a new capital gains event."""
        asset_type = self.asset_type_combo.currentText()
        try:
            acquisition_cost = float(self.acquisition_cost_input.text())
            proceeds = float(self.proceeds_input.text())
        except ValueError:
            # Show error dialog
            return
        
        acquisition_date = self.acquisition_date_input.date().toPython()
        disposal_date = self.disposal_date_input.date().toPython()
        is_exempt = self.exempt_checkbox.isChecked()
        
        try:
            self.tax_service.create_capital_gains_event(
                asset_type=asset_type,
                acquisition_date=acquisition_date,
                disposal_date=disposal_date,
                acquisition_cost=acquisition_cost,
                proceeds=proceeds,
                is_exempt=is_exempt
            )
            # Reload data
            self.load_capital_gains()
            self.clear_capital_gains_inputs()
        except Exception as e:
            # Show error dialog
            print(f"Error adding capital gains event: {e}")
    
    def create_tax_return(self):
        """Create a new tax return."""
        tax_year = self.tax_year_input.text()
        filing_date = self.filing_date_input.date().toPython()
        
        try:
            self.tax_service.create_tax_return(
                tax_year=tax_year,
                filing_date=filing_date
            )
            # Reload data
            self.load_tax_returns()
            self.clear_tax_return_inputs()
        except Exception as e:
            # Show error dialog
            print(f"Error creating tax return: {e}")
    
    def refresh_summary(self):
        """Refresh tax summary."""
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()
        
        try:
            summary = self.tax_service.calculate_tax_summary(start_date, end_date)
            self.summary_label.setText(f"""
            Tax Summary ({start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}):
            
            Total Income Tax: ${summary['total_income_tax']:.2f}
            Total Capital Gains Tax: ${summary['total_capital_gains_tax']:.2f}
            Total Tax Liability: ${summary['total_tax_liability']:.2f}
            Tax Events: {summary['tax_events_count']}
            Capital Gains Events: {summary['capital_gains_count']}
            """)
        except Exception as e:
            self.summary_label.setText(f"Error calculating summary: {e}")
    
    def clear_tax_event_inputs(self):
        """Clear tax event input fields."""
        self.title_input.clear()
        self.description_input.clear()
        self.amount_input.clear()
        self.tax_rate_input.clear()
        self.deductible_checkbox.setChecked(False)
    
    def clear_capital_gains_inputs(self):
        """Clear capital gains input fields."""
        self.asset_type_combo.setCurrentIndex(0)
        self.acquisition_date_input.setDate(QDate.currentDate())
        self.disposal_date_input.setDate(QDate.currentDate())
        self.acquisition_cost_input.clear()
        self.proceeds_input.clear()
        self.exempt_checkbox.setChecked(False)
    
    def clear_tax_return_inputs(self):
        """Clear tax return input fields."""
        self.tax_year_input.clear()
        self.tax_year_input.setText("2023-2024")
        self.filing_date_input.setDate(QDate.currentDate())