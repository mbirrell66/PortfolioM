"""
Add Watchlist Item dialog for Portfolio Manager.

Matches the same fields as AddPositionDialog plus watchlist-specific extras:
entry_date, target_price, shares_hypothetical, notes.
"""

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout,
    QLineEdit, QDateEdit, QDoubleSpinBox, QTextEdit, QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from services.watchlist_service import WatchlistService


class AddWatchlistItemDialog(QDialog):
    """Modal dialog for adding a stock to the watchlist."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add to Watchlist")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._watchlist_service = WatchlistService()
        self._setup_ui()

    # ------------------------------------------------------------------ UI --

    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0F1117;
            }
            QLabel {
                color: #7488B8;
                font-size: 13px;
            }
            QLineEdit, QDateEdit, QDoubleSpinBox, QTextEdit {
                background-color: #191D2E;
                color: #DDE8FF;
                border: 1px solid #222844;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QDateEdit:focus,
            QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #5295FF;
            }
            QDateEdit::drop-down, QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                background-color: #222844;
                border: none;
            }
            QDialogButtonBox QPushButton {
                background-color: #5295FF;
                color: #0F1117;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover { background-color: #4080EE; }
            QDialogButtonBox QPushButton:pressed { background-color: #327AE0; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 20)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        # Ticker
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g. AAPL")
        form.addRow("Ticker *", self.ticker_input)

        # Company name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("e.g. Apple Inc.")
        form.addRow("Company Name", self.company_name_input)

        # Entry date — the reference date for performance calculations
        self.entry_date_edit = QDateEdit()
        self.entry_date_edit.setCalendarPopup(True)
        self.entry_date_edit.setDate(QDate.currentDate())
        self.entry_date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Entry Date *", self.entry_date_edit)

        # Entry price — price on that date (the "purchase price" equivalent)
        self.entry_price_spin = QDoubleSpinBox()
        self.entry_price_spin.setRange(0.01, 9_999_999.99)
        self.entry_price_spin.setDecimals(2)
        self.entry_price_spin.setPrefix("$")
        self.entry_price_spin.setGroupSeparatorShown(True)
        form.addRow("Entry Price *", self.entry_price_spin)

        # Hypothetical shares — optional, enables P&L columns
        self.shares_spin = QDoubleSpinBox()
        self.shares_spin.setRange(0, 9_999_999)
        self.shares_spin.setDecimals(4)
        self.shares_spin.setValue(0)
        self.shares_spin.setSpecialValueText("—")
        self.shares_spin.setGroupSeparatorShown(True)
        form.addRow("Hypothetical Shares", self.shares_spin)

        # Target price — optional
        self.target_price_spin = QDoubleSpinBox()
        self.target_price_spin.setRange(0, 9_999_999.99)
        self.target_price_spin.setDecimals(2)
        self.target_price_spin.setPrefix("$")
        self.target_price_spin.setValue(0)
        self.target_price_spin.setSpecialValueText("—")
        self.target_price_spin.setGroupSeparatorShown(True)
        form.addRow("Target Price", self.target_price_spin)

        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(72)
        self.notes_text.setPlaceholderText("Optional notes…")
        form.addRow("Notes", self.notes_text)

        layout.addLayout(form)

        # OK / Cancel
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ------------------------------------------------------------ helpers --

    def _show_error(self, message: str):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Input Error")
        msg.exec()

    # ------------------------------------------------------------ accept  --

    def _on_accept(self):
        ticker = self.ticker_input.text().strip().upper()
        if not ticker:
            self._show_error("Ticker is required.")
            return
        if self.entry_price_spin.value() <= 0:
            self._show_error("Entry price must be greater than zero.")
            return

        try:
            company = self.company_name_input.text().strip() or ticker
            entry_price = self.entry_price_spin.value()
            entry_date = self.entry_date_edit.date().toPython()
            shares = round(self.shares_spin.value()) if self.shares_spin.value() > 0 else None
            target = self.target_price_spin.value() if self.target_price_spin.value() > 0 else None
            notes = self.notes_text.toPlainText().strip() or None

            self._watchlist_service.add_item(
                ticker=ticker,
                company_name=company,
                entry_price=entry_price,
                entry_date=entry_date,
                shares_hypothetical=shares,
                target_price=target,
                notes=notes,
            )
            self.accept()
        except Exception as exc:
            self._show_error(f"Error adding to watchlist:\n{exc}")
