"""
Add position dialog for Portfolio Manager
"""

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QDateEdit, QSpinBox, QTextEdit,
                             QLabel, QDoubleSpinBox, QMessageBox)
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
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background-color: #0F1117; }
            QLabel { color: #7488B8; font-size: 13px; }
            QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus,
            QSpinBox:focus, QTextEdit:focus { border-color: #5295FF; }
            QDateEdit::drop-down, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #222844; border: none;
            }
            QDialogButtonBox QPushButton {
                background-color: #5295FF; color: #0F1117; border: none;
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
                font-weight: 600; min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover { background-color: #4080EE; }
            QDialogButtonBox QPushButton:pressed { background-color: #327AE0; }
        """)

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
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g., AAPL")
        
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("e.g., Apple Inc.")
        
        self.purchase_date_edit = QDateEdit()
        self.purchase_date_edit.setCalendarPopup(True)
        
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0.01, 999999.99)
        self.purchase_price_spin.setDecimals(2)
        self.purchase_price_spin.setPrefix("$")
        
        self.shares_spin = QSpinBox()
        self.shares_spin.setRange(1, 999999)
        
        self.buy_commission_spin = QDoubleSpinBox()
        self.buy_commission_spin.setRange(0.0, 9999.99)
        self.buy_commission_spin.setDecimals(2)
        self.buy_commission_spin.setPrefix("$")
        self.buy_commission_spin.setValue(0.0)

        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
    
    def create_layout(self):
        """Create layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.addRow("Ticker *", self.ticker_input)
        form_layout.addRow("Company Name", self.company_name_input)
        form_layout.addRow("Purchase Date", self.purchase_date_edit)
        form_layout.addRow("Purchase Price *", self.purchase_price_spin)
        form_layout.addRow("Shares *", self.shares_spin)
        form_layout.addRow("Buy Commission", self.buy_commission_spin)
        form_layout.addRow("Notes", self.notes_text)
        
        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        layout.addWidget(self.button_box)
        
    def create_connections(self):
        """Create signal connections."""
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
    
    def validate_input(self):
        """Validate input fields."""
        ticker = self.ticker_input.text().strip()
        purchase_price = self.purchase_price_spin.value()
        shares = self.shares_spin.value()
        
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
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Input Error")
        msg.exec()
    
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate_input():
            try:
                ticker = self.ticker_input.text().strip()
                company_name = self.company_name_input.text().strip()
                purchase_date = self.purchase_date_edit.date().toPython()
                purchase_price = self.purchase_price_spin.value()
                shares = self.shares_spin.value()
                notes = self.notes_text.toPlainText().strip()
                
                buy_commission = self.buy_commission_spin.value()
                self.portfolio_service.add_position(
                    ticker=ticker,
                    company_name=company_name or ticker,
                    purchase_date=purchase_date,
                    purchase_price=purchase_price,
                    shares=shares,
                    buy_commission=buy_commission,
                    notes=notes
                )
                
                super().accept()
                
            except Exception as e:
                self.show_error(f"Error adding position: {str(e)}")
        else:
            super().reject()
