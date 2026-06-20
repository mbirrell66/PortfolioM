"""
Tax Event Dialog
Dialog for creating and editing tax events.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFormLayout, QLabel, QLineEdit, QDateEdit, 
                             QComboBox, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt, QDate
from datetime import date
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TaxEventDialog(QDialog):
    """Dialog for adding tax events."""
    
    def __init__(self, tax_service, parent=None):
        """Initialize the tax event dialog."""
        super().__init__(parent)
        self.tax_service = tax_service
        self.setWindowTitle("Add Tax Event")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setStyleSheet("""
            QDialog { background-color: #0F1117; }
            QLabel { color: #7488B8; font-size: 13px; }
            QGroupBox {
                color: #7488B8; font-size: 12px; font-weight: 600;
                border: 1px solid #222844; border-radius: 6px;
                margin-top: 8px; padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px; padding: 0 4px;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus { border-color: #5295FF; }
            QDateEdit::drop-down, QComboBox::drop-down {
                background-color: #222844; border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844;
                selection-background-color: rgba(74, 158, 255, 0.25);
            }
            QCheckBox { color: #DDE8FF; font-size: 13px; }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1px solid #222844; border-radius: 3px;
                background-color: #191D2E;
            }
            QCheckBox::indicator:checked {
                background-color: #5295FF; border-color: #5295FF;
            }
            QPushButton {
                background-color: #5295FF; color: #0F1117; border: none;
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
                font-weight: 600; min-width: 80px;
            }
            QPushButton:hover { background-color: #4080EE; }
            QPushButton:pressed { background-color: #327AE0; }
        """)

        layout = QVBoxLayout(self)

        # Main form
        form_group = QGroupBox("Tax Event Details")
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
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.save_tax_event)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        
        # Load tax categories
        self.load_tax_categories()
    
    def load_tax_categories(self):
        """Load tax categories into the combo box."""
        categories = self.tax_service.get_tax_categories()
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def save_tax_event(self):
        """Save the tax event."""
        title = self.title_input.text()
        description = self.description_input.text()
        try:
            amount = float(self.amount_input.text())
            tax_rate = float(self.tax_rate_input.text()) if self.tax_rate_input.text() else 0.0
        except ValueError:
            # Show error message
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
            self.accept()
        except Exception as e:
            # Show error dialog
            print(f"Error saving tax event: {e}")