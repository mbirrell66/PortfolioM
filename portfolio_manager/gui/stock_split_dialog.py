"""
Stock Split Dialog for Portfolio Manager
"""

from datetime import date
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QDateEdit, QSpinBox, QPushButton, QMessageBox, QComboBox)
from PySide6.QtCore import Qt, QDate
from services.portfolio_service import PortfolioService

class StockSplitDialog(QDialog):
    """Dialog for adding stock splits."""
    
    def __init__(self, parent=None, ticker=None):
        super().__init__(parent)
        self.setWindowTitle("Add Stock Split")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #0F1117; }
            QLabel { color: #7488B8; font-size: 13px; }
            QComboBox, QDateEdit, QSpinBox {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus { border-color: #5295FF; }
            QComboBox::drop-down, QDateEdit::drop-down,
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #222844; border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844;
                selection-background-color: rgba(74, 158, 255, 0.25);
            }
            QPushButton {
                background-color: #5295FF; color: #0F1117; border: none;
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
                font-weight: 600; min-width: 80px;
            }
            QPushButton:hover { background-color: #4080EE; }
            QPushButton:pressed { background-color: #327AE0; }
        """)

        self.ticker = ticker
        self.portfolio_service = PortfolioService()
        
        self.init_ui()
        self.load_ticker_data()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        ticker_layout = QHBoxLayout()
        ticker_layout.addWidget(QLabel("Ticker:"))
        self.ticker_combo = QComboBox()
        self.ticker_combo.setEditable(True)
        ticker_layout.addWidget(self.ticker_combo)
        layout.addLayout(ticker_layout)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Split Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        old_layout = QHBoxLayout()
        old_layout.addWidget(QLabel("Old Ratio (e.g., 1):"))
        self.old_ratio_spin = QSpinBox()
        self.old_ratio_spin.setRange(1, 100)
        self.old_ratio_spin.setValue(1)
        old_layout.addWidget(self.old_ratio_spin)
        layout.addLayout(old_layout)
        
        new_layout = QHBoxLayout()
        new_layout.addWidget(QLabel("New Ratio (e.g., 4):"))
        self.new_ratio_spin = QSpinBox()
        self.new_ratio_spin.setRange(1, 100)
        self.new_ratio_spin.setValue(4)
        new_layout.addWidget(self.new_ratio_spin)
        layout.addLayout(new_layout)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add Split")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_ticker_data(self):
        """Load available ticker symbols."""
        try:
            positions = self.portfolio_service.get_positions()
            tickers = list(set([pos.ticker for pos in positions]))
            self.ticker_combo.addItems(tickers)
            if self.ticker and self.ticker in tickers:
                self.ticker_combo.setCurrentText(self.ticker)
        except Exception as e:
            print(f"Error loading ticker data: {e}")
        
    def get_split_data(self):
        """Get the stock split data entered by user."""
        return {
            'ticker': self.ticker_combo.currentText().strip().upper(),
            'split_date': self.date_edit.date().toPython(),
            'old_ratio': self.old_ratio_spin.value(),
            'new_ratio': self.new_ratio_spin.value()
        }
        
    def validate_input(self):
        """Validate the input data."""
        ticker = self.ticker_combo.currentText().strip()
        if not ticker:
            QMessageBox.warning(self, "Invalid Input", "Ticker symbol is required.")
            return False
            
        if self.old_ratio_spin.value() >= self.new_ratio_spin.value():
            QMessageBox.warning(self, "Invalid Input", "New ratio must be greater than old ratio.")
            return False
            
        return True
        
    def accept(self):
        """Handle OK button click."""
        if self.validate_input():
            try:
                split_data = self.get_split_data()
                self.portfolio_service.add_stock_split(
                    split_data['ticker'],
                    split_data['split_date'],
                    split_data['old_ratio'],
                    split_data['new_ratio']
                )
                super().accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add stock split: {str(e)}")
