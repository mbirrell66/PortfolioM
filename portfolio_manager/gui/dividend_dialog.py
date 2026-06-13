"""
Dividend Entry Dialog for Portfolio Manager
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QComboBox, QDateEdit, QDoubleSpinBox,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, QDate
from database.models import Dividend
from services.portfolio_service import PortfolioService
import datetime


class DividendEntryDialog(QDialog):
    """Dialog for entering dividend payments."""
    
    def __init__(self, parent=None):
        """Initialize dividend entry dialog."""
        super().__init__(parent)
        self.portfolio_service = PortfolioService()
        self.setWindowTitle("Add Dividend Payment")
        self.setModal(True)
        self.resize(500, 420)
        self.init_ui()
        self.load_positions()
    
    def init_ui(self):
        """Initialize user interface."""
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
            QComboBox, QDateEdit, QDoubleSpinBox {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus { border-color: #5295FF; }
            QComboBox::drop-down, QDateEdit::drop-down,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #222844; border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #191D2E; color: #DDE8FF;
                border: 1px solid #222844;
                selection-background-color: rgba(74, 158, 255, 0.25);
            }
            QTableWidget {
                background-color: #0F1117; alternate-background-color: #161928;
                color: #DDE8FF; gridline-color: transparent;
                border: 1px solid #222844; border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #191D2E; color: #7488B8;
                padding: 6px 8px; font-size: 11px; font-weight: 600;
                border: none; border-right: 1px solid #222844;
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
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Dividend entry form
        form_group = QGroupBox("Dividend Details")
        form_layout = QFormLayout(form_group)
        
        self.ticker_combo = QComboBox()
        self.ticker_combo.setEditable(True)
        
        self.payment_date_edit = QDateEdit()
        self.payment_date_edit.setCalendarPopup(True)
        self.payment_date_edit.setDate(QDate.currentDate())
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(4)
        self.amount_spin.setRange(0, 1000000)
        self.amount_spin.setSuffix(" USD")
        
        self.total_amount_label = QLabel("Total: $0.00")
        
        form_layout.addRow("Stock Ticker:", self.ticker_combo)
        form_layout.addRow("Payment Date:", self.payment_date_edit)
        form_layout.addRow("Amount per Share:", self.amount_spin)
        form_layout.addRow("Total Amount:", self.total_amount_label)
        
        layout.addWidget(form_group)
        
        # Position details
        position_group = QGroupBox("Position Details")
        position_layout = QVBoxLayout(position_group)
        
        self.position_table = QTableWidget(0, 4)
        self.position_table.setHorizontalHeaderLabels(["Ticker", "Shares", "Purchase Price", "Current Value"])
        self.position_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.position_table.horizontalHeader().setStretchLastSection(True)
        
        position_layout.addWidget(self.position_table)
        layout.addWidget(position_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Dividend")
        save_btn.clicked.connect(self.save_dividend)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.amount_spin.valueChanged.connect(self.update_total_amount)
        self.ticker_combo.currentTextChanged.connect(self.update_position_details)
    
    def load_positions(self):
        """Load available positions for selection."""
        try:
            positions = self.portfolio_service.get_positions()
            tickers = [pos.ticker for pos in positions]
            self.ticker_combo.clear()
            self.ticker_combo.addItems(tickers)
        except Exception as e:
            print(f"Error loading positions: {e}")
    
    def update_position_details(self):
        """Update position details when ticker is selected."""
        try:
            ticker = self.ticker_combo.currentText()
            if not ticker:
                return
                
            positions = self.portfolio_service.get_positions()
            position = next((p for p in positions if p.ticker == ticker), None)
            
            if position:
                self.position_table.setRowCount(0)
                self.position_table.setRowCount(1)
                self.position_table.setItem(0, 0, QTableWidgetItem(ticker))
                self.position_table.setItem(0, 1, QTableWidgetItem(str(position.shares)))
                self.position_table.setItem(0, 2, QTableWidgetItem(f"${position.purchase_price:.2f}"))
                
                current_price = self.portfolio_service.get_current_price(ticker)
                if current_price:
                    current_value = position.shares * current_price
                    self.position_table.setItem(0, 3, QTableWidgetItem(f"${current_value:.2f}"))
                else:
                    self.position_table.setItem(0, 3, QTableWidgetItem("N/A"))
            else:
                self.position_table.setRowCount(0)
                
        except Exception as e:
            print(f"Error updating position details: {e}")
    
    def update_total_amount(self):
        """Update total amount when amount per share changes."""
        try:
            ticker = self.ticker_combo.currentText()
            if not ticker:
                return
                
            positions = self.portfolio_service.get_positions()
            position = next((p for p in positions if p.ticker == ticker), None)
            
            if position:
                total = self.amount_spin.value() * position.shares
                self.total_amount_label.setText(f"Total: ${total:.2f}")
            else:
                self.total_amount_label.setText("Total: $0.00")
                
        except Exception as e:
            print(f"Error updating total amount: {e}")
    
    def save_dividend(self):
        """Save dividend payment to database."""
        try:
            ticker = self.ticker_combo.currentText().strip()
            if not ticker:
                QMessageBox.warning(self, "Invalid Input", "Please select a stock ticker.")
                return
            
            payment_date = self.payment_date_edit.date().toPython()
            amount_per_share = self.amount_spin.value()
            
            if amount_per_share <= 0:
                QMessageBox.warning(self, "Invalid Input", "Amount per share must be greater than zero.")
                return
            
            positions = self.portfolio_service.get_positions()
            position = next((p for p in positions if p.ticker == ticker), None)
            
            if not position:
                QMessageBox.warning(self, "Invalid Input", "Selected ticker not found in positions.")
                return
            
            total_amount = amount_per_share * position.shares
            
            dividend = Dividend(
                position_id=position.id,
                ticker=ticker,
                payment_date=payment_date,
                amount_per_share=amount_per_share,
                total_amount=total_amount
            )
            
            from database.database import SessionLocal
            db = SessionLocal()
            try:
                db.add(dividend)
                db.commit()
            finally:
                db.close()
            
            QMessageBox.information(self, "Success", f"Dividend payment for {ticker} saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save dividend payment: {str(e)}")
            print(f"Error saving dividend: {e}")
