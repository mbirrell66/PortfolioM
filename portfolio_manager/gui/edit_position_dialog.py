"""
Edit position dialog for Portfolio Manager
"""

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                               QFormLayout, QLineEdit, QDateEdit, QSpinBox, QTextEdit,
                               QLabel, QDoubleSpinBox, QMessageBox, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt, QDate
from datetime import date
from services.portfolio_service import PortfolioService


class EditPositionDialog(QDialog):
    """Dialog for editing an existing position, including closing (selling) it."""

    _SS = """
        QDialog { background-color: #0F1117; }
        QLabel { color: #7488B8; font-size: 13px; }
        QGroupBox {
            color: #7488B8; font-size: 12px; font-weight: 600;
            border: 1px solid #222844; border-radius: 6px;
            margin-top: 8px; padding-top: 8px;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {
            background-color: #191D2E; color: #DDE8FF;
            border: 1px solid #222844; border-radius: 6px;
            padding: 6px 10px; font-size: 13px;
        }
        QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus,
        QSpinBox:focus, QTextEdit:focus { border-color: #5295FF; }
        QLineEdit:disabled, QDateEdit:disabled, QDoubleSpinBox:disabled,
        QSpinBox:disabled { color: #4B6599; background-color: #141720; }
        QDateEdit::drop-down, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #222844; border: none;
        }
        QCheckBox { color: #DDE8FF; font-size: 13px; }
        QCheckBox::indicator {
            width: 16px; height: 16px;
            border: 1px solid #222844; border-radius: 3px;
            background-color: #191D2E;
        }
        QCheckBox::indicator:checked { background-color: #5295FF; border-color: #5295FF; }
        QDialogButtonBox QPushButton {
            background-color: #5295FF; color: #0F1117; border: none;
            border-radius: 6px; padding: 8px 20px; font-size: 13px;
            font-weight: 600; min-width: 80px;
        }
        QDialogButtonBox QPushButton:hover { background-color: #4080EE; }
        QDialogButtonBox QPushButton:pressed { background-color: #327AE0; }
    """

    def __init__(self, position_id, parent=None):
        """Initialize dialog with existing position data."""
        super().__init__(parent)
        self.position_id = position_id
        self.setWindowTitle("Edit Position")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(self._SS)

        self.portfolio_service = PortfolioService()
        self.position = self.portfolio_service.get_position(position_id)
        if not self.position:
            QMessageBox.critical(self, "Error", "Position not found.")
            self.reject()
            return

        self._build_ui()
        self._populate_fields()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        # ---- Buy details group ----------------------------------------
        buy_group = QGroupBox("Buy Transaction")
        buy_form = QFormLayout(buy_group)
        buy_form.setSpacing(8)

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
        self.purchase_price_spin.setReadOnly(True)
        self.purchase_price_spin.setEnabled(False)

        self.shares_spin = QSpinBox()
        self.shares_spin.setRange(1, 9999999)

        self.buy_commission_spin = QDoubleSpinBox()
        self.buy_commission_spin.setRange(0.0, 9999.99)
        self.buy_commission_spin.setDecimals(2)
        self.buy_commission_spin.setPrefix("$")

        buy_form.addRow("Ticker:", self.ticker_input)
        buy_form.addRow("Company Name:", self.company_name_input)
        buy_form.addRow("Buy Date:", self.purchase_date_edit)
        buy_form.addRow("Buy Price:", self.purchase_price_spin)
        buy_form.addRow("Shares:", self.shares_spin)
        buy_form.addRow("Buy Commission:", self.buy_commission_spin)
        layout.addWidget(buy_group)

        # ---- Sell details group ---------------------------------------
        sell_group = QGroupBox("Sell Transaction")
        sell_layout = QVBoxLayout(sell_group)

        self.sold_checkbox = QCheckBox("Mark as sold")
        self.sold_checkbox.toggled.connect(self._on_sold_toggled)
        sell_layout.addWidget(self.sold_checkbox)

        sell_form = QFormLayout()
        sell_form.setSpacing(8)

        self.sell_date_edit = QDateEdit()
        self.sell_date_edit.setCalendarPopup(True)
        self.sell_date_edit.setDate(QDate.currentDate())

        self.sell_price_spin = QDoubleSpinBox()
        self.sell_price_spin.setRange(0.01, 999999.99)
        self.sell_price_spin.setDecimals(2)
        self.sell_price_spin.setPrefix("$")

        self.sell_commission_spin = QDoubleSpinBox()
        self.sell_commission_spin.setRange(0.0, 9999.99)
        self.sell_commission_spin.setDecimals(2)
        self.sell_commission_spin.setPrefix("$")

        sell_form.addRow("Sell Date:", self.sell_date_edit)
        sell_form.addRow("Sell Price:", self.sell_price_spin)
        sell_form.addRow("Sell Commission:", self.sell_commission_spin)
        sell_layout.addLayout(sell_form)
        layout.addWidget(sell_group)

        # ---- Notes ----------------------------------------------------
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_text)
        layout.addWidget(notes_group)

        # ---- Buttons --------------------------------------------------
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Start with sell fields disabled
        self._set_sell_enabled(False)

    def _set_sell_enabled(self, enabled: bool):
        self.sell_date_edit.setEnabled(enabled)
        self.sell_price_spin.setEnabled(enabled)
        self.sell_commission_spin.setEnabled(enabled)

    def _on_sold_toggled(self, checked: bool):
        self._set_sell_enabled(checked)

    # ------------------------------------------------------------------
    def _populate_fields(self):
        p = self.position
        self.ticker_input.setText(p.ticker or "")
        self.company_name_input.setText(p.company_name or "")

        if p.purchase_date:
            self.purchase_date_edit.setDate(
                QDate(p.purchase_date.year, p.purchase_date.month, p.purchase_date.day)
            )
        self.purchase_price_spin.setValue(p.purchase_price or 0.0)
        self.shares_spin.setValue(p.shares or 1)
        self.buy_commission_spin.setValue(p.buy_commission or 0.0)

        if p.sell_date:
            self.sold_checkbox.setChecked(True)
            self.sell_date_edit.setDate(
                QDate(p.sell_date.year, p.sell_date.month, p.sell_date.day)
            )
            self.sell_price_spin.setValue(p.sell_price or 0.0)
            self.sell_commission_spin.setValue(p.sell_commission or 0.0)
        else:
            self.sold_checkbox.setChecked(False)

        self.notes_text.setText(p.notes or "")

    # ------------------------------------------------------------------
    def _validate(self) -> bool:
        if not self.ticker_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Ticker is required.")
            return False
        if not self.company_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Company name is required.")
            return False
        if self.shares_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Shares must be greater than zero.")
            return False
        if self.sold_checkbox.isChecked() and self.sell_price_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Sell price must be greater than zero.")
            return False
        return True

    # ------------------------------------------------------------------
    def accept(self):
        """Save changes on OK."""
        if not self._validate():
            return

        try:
            kwargs = dict(
                ticker=self.ticker_input.text().strip().upper(),
                company_name=self.company_name_input.text().strip(),
                purchase_date=self.purchase_date_edit.date().toPython(),
                shares=self.shares_spin.value(),
                buy_commission=self.buy_commission_spin.value(),
                notes=self.notes_text.toPlainText().strip(),
            )
            if self.sold_checkbox.isChecked():
                kwargs['sell_date'] = self.sell_date_edit.date().toPython()
                kwargs['sell_price'] = self.sell_price_spin.value()
                kwargs['sell_commission'] = self.sell_commission_spin.value()
            else:
                kwargs['sell_date'] = None
                kwargs['sell_price'] = None
                kwargs['sell_commission'] = 0.0

            self.portfolio_service.update_position(self.position_id, **kwargs)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save position: {str(e)}")
