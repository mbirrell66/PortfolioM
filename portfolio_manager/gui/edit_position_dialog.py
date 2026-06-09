"""
Edit position dialog for Portfolio Manager
"""

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QDateEdit, QSpinBox, QTextEdit,
                             QLabel, QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QDate
from datetime import date
from services.portfolio_service import PortfolioService

class EditPositionDialog(QDialog):
    """Dialog for editing an existing position."""
    
    def __init__(self, position_id, parent=None):
        """Initialize dialog with existing position data."""
        super().__init__(parent)
        self.position_id = position_id
        self.setWindowTitle("Edit Position")
        self.setModal(True)
        
        # Initialize services
        self.portfolio_service = PortfolioService()
        
        # Get existing position data
        self.position = self.portfolio_service.get_position(position_id)
        if not self.position:
            QMessageBox.critical(self, "Error", "Position not found.")
            self.reject()
            return
            
        # Create UI
        self.create_ui()
        self.create_layout()
        self.create_connections()
        
        # Populate with existing data
        self.populate_fields()
        
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
        
        # Purchase price - make it read-only as this should not be changed
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0.01, 999999.99)
        self.purchase_price_spin.setDecimals(2)
        self.purchase_price_spin.setPrefix("$")
        self.purchase_price_spin.setReadOnly(True)
        self.purchase_price_spin.setEnabled(False)
        
        # Shares
        self.shares_spin = QSpinBox()
        self.shares_spin.setRange(1, 999999)
        
        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        
    def create_layout(self):
        """Create layout for dialog."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.addRow("Ticker:", self.ticker_input)
        form_layout.addRow("Company Name:", self.company_name_input)
        form_layout.addRow("Purchase Date:", self.purchase_date_edit)
        form_layout.addRow("Purchase Price:", self.purchase_price_spin)
        form_layout.addRow("Shares:", self.shares_spin)
        form_layout.addRow("Notes:", self.notes_text)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        
        # Set dialog size
        self.resize(400, 300)
    
    def create_connections(self):
        """Create signal connections."""
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
    
    def populate_fields(self):
        """Populate dialog fields with existing position data."""
        self.ticker_input.setText(self.position.ticker)
        self.company_name_input.setText(self.position.company_name)
        
        # Convert date object to QDate
        if self.position.purchase_date:
            self.purchase_date_edit.setDate(QDate(
                self.position.purchase_date.year,
                self.position.purchase_date.month,
                self.position.purchase_date.day
            ))
        
        self.purchase_price_spin.setValue(self.position.purchase_price)
        self.shares_spin.setValue(self.position.shares)
        self.notes_text.setText(self.position.notes or "")
    
    def validate_input(self):
        """Validate user input."""
        ticker = self.ticker_input.text().strip()
        company_name = self.company_name_input.text().strip()
        purchase_date = self.purchase_date_edit.date()
        purchase_price = self.purchase_price_spin.value()
        shares = self.shares_spin.value()
        
        if not ticker:
            QMessageBox.warning(self, "Validation Error", "Ticker is required.")
            return False
            
        if not company_name:
            QMessageBox.warning(self, "Validation Error", "Company name is required.")
            return False
            
        if purchase_price <= 0:
            QMessageBox.warning(self, "Validation Error", "Purchase price must be greater than zero.")
            return False
            
        if shares <= 0:
            QMessageBox.warning(self, "Validation Error", "Shares must be greater than zero.")
            return False
            
        return True
    
    def get_position_data(self):
        """Get position data from dialog fields."""
        # Note: purchase_price is not included here as it should not be editable
        return {
            'ticker': self.ticker_input.text().strip(),
            'company_name': self.company_name_input.text().strip(),
            'purchase_date': self.purchase_date_edit.date().toPython(),
            'shares': self.shares_spin.value(),
            'notes': self.notes_text.toPlainText().strip()
        }
    
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate_input():
            try:
                # Update the position
                position_data = self.get_position_data()
                # Ensure purchase_price is not in the update data (as it should be immutable)
                if 'purchase_price' in position_data:
                    del position_data['purchase_price']
                success = self.portfolio_service.update_position(self.position_id, **position_data)
                
                if success:
                    super().accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update position.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")