"""
Capital Gains Dialog
Dialog for creating and editing capital gains events.
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

class CapitalGainsDialog(QDialog):
    """Dialog for adding capital gains events."""
    
    def __init__(self, tax_service, parent=None):
        """Initialize the capital gains dialog."""
        super().__init__(parent)
        self.tax_service = tax_service
        self.setWindowTitle("Add Capital Gains Event")
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
        form_group = QGroupBox("Capital Gains Details")
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
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.save_capital_gains_event)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
    
    def save_capital_gains_event(self):
        """Save the capital gains event."""
        asset_type = self.asset_type_combo.currentText()
        try:
            acquisition_cost = float(self.acquisition_cost_input.text())
            proceeds = float(self.proceeds_input.text())
        except ValueError:
            # Show error message
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
            self.accept()
        except Exception as e:
            # Show error dialog
            print(f"Error saving capital gains event: {e}")