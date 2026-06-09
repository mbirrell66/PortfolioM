"""
Add position dialog for Portfolio Manager
"""

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QDateEdit, QSpinBox, QTextEdit,
                             QLabel, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
from datetime import date
from services.portfolio_service import PortfolioService

class AddPositionDialog(QDialog):
    """Dialog for adding a new position."""
    
    def __init__(self, parent=None):
        """Initialize dialog."""
        super().__init__(parent)
        self.setWindowTitle("Add Position")
        self.setModal(True)
        
        # Initialize services
        self.portfolio_service = PortfolioService()
        
        # Create UI
        self.create_ui()
        self.create_layout()
        self.create_connections()
        
        # Set initial date to today
        self.purchase_date_edit.setDate(QDate.currentDate())
    
    def create_ui(self):
        """Create UI elements."""
        # Ticker input
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL")
        
        # Company name input
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("e.g., Apple Inc.")
        
        # Purchase date
        self.purchase_date_edit = QDateEdit()
        self.purchase_date_edit.setCalendarPopup(True)
        
        # Purchase price
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0.01, 999999.99)
        self.purchase_price_spin.setDecimals(2)
        self.purchase_price_spin.setPrefix("$")
        
        # Shares
        self.shares_spin = QSpinBox()
        self.shares_spin.setRange(1, 999999)
        
        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
    
    def create_layout(self):
        """Create layout."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.addRow("Ticker*", self.ticker_input)
        form_layout.addRow("Company Name", self.company_name_input)
        form_layout.addRow("Purchase Date", self.purchase_date_edit)
        form_layout.addRow("Purchase Price*", self.purchase_price_spin)
        form_layout.addRow("Shares*", self.shares_spin)
        form_layout.addRow("Notes", self.notes_text)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        layout.addWidget(button_box)
        
        # Set button connections
        self.button_box = button_box
        
    def create_connections(self):
        """Create signal connections."""
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
    
    def validate_input(self):
        """Validate input fields."""
        ticker = self.ticker_input.text().strip()
        purchase_price = self.purchase_price_spin.value()
        shares = self.shares_spin.value()
        
        # Check required fields
        if not ticker:
            self.show_error("Ticker is required")
            return False
        
        if purchase_price <= 0:
            self.show_error("Purchase price must be greater than 0")
            return False
        
        if shares <= 0:
            self.show_error("Shares must be greater than 0")
            return False
        
        return True
    
    def show_error(self, message):
        """Show error message."""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Input Error")
        msg.exec()
    
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate_input():
            try:
                # Create position
                ticker = self.ticker_input.text().strip()
                company_name = self.company_name_input.text().strip()
                purchase_date = self.purchase_date_edit.date().toPython()
                purchase_price = self.purchase_price_spin.value()
                shares = self.shares_spin.value()
                notes = self.notes_text.toPlainText().strip()
                
                # Add to database (using the service)
                position = self.portfolio_service.add_position(
                    ticker=ticker,
                    company_name=company_name or ticker,
                    purchase_date=purchase_date,
                    purchase_price=purchase_price,
                    shares=shares,
                    notes=notes
                )
                
                super().accept()
                
            except Exception as e:
                self.show_error(f"Error adding position: {str(e)}")
        else:
            super().reject()