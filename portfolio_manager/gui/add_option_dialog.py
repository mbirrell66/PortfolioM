"""
Add / Edit Options Position dialog.
"""
from __future__ import annotations
from datetime import date

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit,
    QTextEdit, QRadioButton, QButtonGroup, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor

from services.options_service import OptionsService
from services.portfolio_service import PortfolioService

_SS = """
    QDialog { background-color: #0F1117; }
    QLabel { color: #7488B8; font-size: 13px; }
    QLabel#calc_label { color: #DDE8FF; font-size: 13px; font-weight: 600; }
    QLabel#section { color: #5295FF; font-size: 11px; font-weight: 700;
                     letter-spacing: 0.5px; text-transform: uppercase; }
    QGroupBox {
        color: #7488B8; font-size: 12px; font-weight: 600;
        border: 1px solid #222844; border-radius: 6px;
        margin-top: 8px; padding-top: 8px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
    QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px;
        padding: 6px 10px; font-size: 13px;
    }
    QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus,
    QSpinBox:focus { border-color: #5295FF; }
    QComboBox::drop-down, QDateEdit::drop-down { background-color: #222844; border: none; }
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
    QSpinBox::up-button, QSpinBox::down-button { background-color: #222844; border: none; }
    QComboBox QAbstractItemView {
        background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;
        selection-background-color: rgba(74, 158, 255, 0.25);
    }
    QRadioButton { color: #DDE8FF; font-size: 13px; }
    QRadioButton::indicator {
        width: 16px; height: 16px;
        border: 1px solid #222844; border-radius: 8px; background-color: #191D2E;
    }
    QRadioButton::indicator:checked { background-color: #5295FF; border-color: #5295FF; }
    QTextEdit {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px; font-size: 13px;
    }
    QFrame#divider { background-color: #222844; }
    QDialogButtonBox QPushButton {
        background-color: #5295FF; color: #0F1117; border: none;
        border-radius: 6px; padding: 8px 20px; font-size: 13px;
        font-weight: 600; min-width: 80px;
    }
    QDialogButtonBox QPushButton:hover { background-color: #4080EE; }
    QDialogButtonBox QPushButton:pressed { background-color: #327AE0; }
"""

_CALENDAR_POPUP_SS = """
    QWidget { background-color: #0F1117; color: #DDE8FF; }
    QWidget#qt_calendar_navigationbar { background-color: #191D2E; }
    QToolButton { color: #DDE8FF; background-color: #191D2E; border: none;
                  border-radius: 4px; padding: 4px 10px; margin: 2px; font-size: 13px; }
    QToolButton:hover { background-color: #222844; color: #5295FF; }
    QToolButton::menu-indicator { image: none; }
    QSpinBox { background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844;
               border-radius: 4px; padding: 2px 4px; }
    QMenu { background-color: #191D2E; color: #DDE8FF; border: 1px solid #222844; }
    QMenu::item:selected { background-color: #5295FF; color: #0F1117; }
    QAbstractItemView { background-color: #0F1117; color: #DDE8FF;
                        selection-background-color: #5295FF; selection-color: #0F1117;
                        outline: none; border: none; }
    QAbstractItemView::item { padding: 2px; border: none; }
    QHeaderView::section { color: #7488B8; background-color: #191D2E;
                           padding: 4px 2px; border: none; letter-spacing: 0; }
"""


def _style_calendar(de: QDateEdit) -> None:
    cal = de.calendarWidget()
    cal.setStyleSheet(_CALENDAR_POPUP_SS)
    day_fmt = QTextCharFormat()
    day_fmt.setForeground(QColor("#DDE8FF"))
    for d in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday):
        cal.setWeekdayTextFormat(d, day_fmt)
    sat_fmt = QTextCharFormat(); sat_fmt.setForeground(QColor("#7EB8FF"))
    cal.setWeekdayTextFormat(Qt.Saturday, sat_fmt)
    sun_fmt = QTextCharFormat(); sun_fmt.setForeground(QColor("#FF7E7E"))
    cal.setWeekdayTextFormat(Qt.Sunday, sun_fmt)
    hdr_fmt = QTextCharFormat(); hdr_fmt.setForeground(QColor("#7488B8"))
    cal.setHeaderTextFormat(hdr_fmt)


class AddOptionDialog(QDialog):
    """Dialog for adding or editing an options position."""

    def __init__(self, options_service: OptionsService,
                 portfolio_service: PortfolioService,
                 position_id: int | None = None,
                 parent=None):
        super().__init__(parent)
        self._svc = options_service
        self._port_svc = portfolio_service
        self._position_id = position_id
        self._editing = position_id is not None

        self.setWindowTitle("Edit Option" if self._editing else "Add Option")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet(_SS)
        self._build()
        if self._editing:
            self._populate()

    # ------------------------------------------------------------------ build

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # ── Option type ───────────────────────────────────────────────────
        type_group = QGroupBox("Option Type")
        type_row = QHBoxLayout(type_group)
        self._call_rb = QRadioButton("Covered Call")
        self._put_rb  = QRadioButton("Cash-Secured Put")
        self._call_rb.setChecked(True)
        self._type_bg = QButtonGroup(self)
        self._type_bg.addButton(self._call_rb)
        self._type_bg.addButton(self._put_rb)
        type_row.addWidget(self._call_rb)
        type_row.addWidget(self._put_rb)
        type_row.addStretch()
        layout.addWidget(type_group)

        # ── Entry details ─────────────────────────────────────────────────
        entry_group = QGroupBox("Entry Details")
        form = QFormLayout(entry_group)
        form.setSpacing(8)

        # Ticker
        self._ticker_combo = QComboBox()
        self._ticker_combo.setEditable(True)
        self._ticker_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        tickers = self._load_portfolio_tickers()
        self._ticker_combo.addItems(tickers)
        form.addRow("Ticker *", self._ticker_combo)

        # Date written
        self._open_date_edit = QDateEdit()
        self._open_date_edit.setCalendarPopup(True)
        _style_calendar(self._open_date_edit)
        self._open_date_edit.setDate(QDate.currentDate())
        self._open_date_edit.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Date Written *", self._open_date_edit)

        # Premium
        self._premium_spin = QDoubleSpinBox()
        self._premium_spin.setRange(0.0, 99_999.99)
        self._premium_spin.setDecimals(4)
        self._premium_spin.setPrefix("$")
        form.addRow("Premium (per share) *", self._premium_spin)

        # Strike price
        self._strike_spin = QDoubleSpinBox()
        self._strike_spin.setRange(0.0, 999_999.99)
        self._strike_spin.setDecimals(2)
        self._strike_spin.setPrefix("$")
        form.addRow("Strike Price *", self._strike_spin)

        # Expiry date
        self._expiry_edit = QDateEdit()
        self._expiry_edit.setCalendarPopup(True)
        _style_calendar(self._expiry_edit)
        self._expiry_edit.setDate(QDate.currentDate())
        self._expiry_edit.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Expiry Date *", self._expiry_edit)

        # Contracts
        self._contracts_spin = QSpinBox()
        self._contracts_spin.setRange(1, 9_999)
        self._contracts_spin.setValue(1)
        form.addRow("No. of Contracts *", self._contracts_spin)

        # Shares (auto-calculated)
        self._shares_spin = QSpinBox()
        self._shares_spin.setRange(1, 999_999)
        self._shares_spin.setValue(100)
        form.addRow("No. of Shares", self._shares_spin)

        # Fees
        self._fees_spin = QDoubleSpinBox()
        self._fees_spin.setRange(0.0, 9_999.99)
        self._fees_spin.setDecimals(2)
        self._fees_spin.setPrefix("$")
        form.addRow("Fees", self._fees_spin)

        layout.addWidget(entry_group)

        # ── Calculated summary ────────────────────────────────────────────
        calc_group = QGroupBox("Calculated")
        calc_form = QFormLayout(calc_group)
        calc_form.setSpacing(6)

        self._lbl_total_prem  = QLabel("$0.00"); self._lbl_total_prem.setObjectName("calc_label")
        self._lbl_net_prem    = QLabel("$0.00"); self._lbl_net_prem.setObjectName("calc_label")
        self._lbl_net_share   = QLabel("$0.00"); self._lbl_net_share.setObjectName("calc_label")
        self._lbl_total_val   = QLabel("$0.00"); self._lbl_total_val.setObjectName("calc_label")

        calc_form.addRow("Total Premium:",    self._lbl_total_prem)
        calc_form.addRow("Net Premium:",      self._lbl_net_prem)
        calc_form.addRow("Net per Share:",    self._lbl_net_share)
        self._total_val_lbl_row = QLabel("Capital Required:")
        calc_form.addRow(self._total_val_lbl_row, self._lbl_total_val)

        layout.addWidget(calc_group)

        # ── Status / close ────────────────────────────────────────────────
        close_group = QGroupBox("Status")
        close_form = QFormLayout(close_group)
        close_form.setSpacing(8)

        self._status_combo = QComboBox()
        self._status_combo.addItems(["Open", "Expired", "Closed", "Exercised"])
        close_form.addRow("Status", self._status_combo)

        self._close_date_edit = QDateEdit()
        self._close_date_edit.setCalendarPopup(True)
        _style_calendar(self._close_date_edit)
        self._close_date_edit.setDate(QDate.currentDate())
        self._close_date_edit.setDisplayFormat("dd/MM/yyyy")

        self._close_prem_spin = QDoubleSpinBox()
        self._close_prem_spin.setRange(0.0, 99_999.99)
        self._close_prem_spin.setDecimals(4)
        self._close_prem_spin.setPrefix("$")

        self._close_fees_spin = QDoubleSpinBox()
        self._close_fees_spin.setRange(0.0, 9_999.99)
        self._close_fees_spin.setDecimals(2)
        self._close_fees_spin.setPrefix("$")

        self._close_date_row_label = QLabel("Date Closed")
        self._close_prem_row_label = QLabel("Buy-back Premium (per share)")
        self._close_fees_row_label = QLabel("Close Fees")
        close_form.addRow(self._close_date_row_label, self._close_date_edit)
        close_form.addRow(self._close_prem_row_label, self._close_prem_spin)
        close_form.addRow(self._close_fees_row_label, self._close_fees_spin)
        self._lbl_pl = QLabel("—"); self._lbl_pl.setObjectName("calc_label")
        close_form.addRow("Profit / Loss:", self._lbl_pl)

        layout.addWidget(close_group)

        # ── Notes ─────────────────────────────────────────────────────────
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(70)
        notes_layout.addWidget(self._notes_edit)
        layout.addWidget(notes_group)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        # Connections
        self._contracts_spin.valueChanged.connect(self._on_contracts_changed)
        self._premium_spin.valueChanged.connect(self._refresh_calcs)
        self._strike_spin.valueChanged.connect(self._refresh_calcs)
        self._shares_spin.valueChanged.connect(self._refresh_calcs)
        self._fees_spin.valueChanged.connect(self._refresh_calcs)
        self._close_prem_spin.valueChanged.connect(self._refresh_calcs)
        self._close_fees_spin.valueChanged.connect(self._refresh_calcs)
        self._status_combo.currentTextChanged.connect(self._on_status_changed)
        self._call_rb.toggled.connect(self._refresh_calcs)

        self._on_status_changed("Open")
        self._refresh_calcs()

    # ---------------------------------------------------------------- helpers

    def _load_portfolio_tickers(self) -> list[str]:
        try:
            positions = self._port_svc.get_positions()
            seen, tickers = set(), []
            for p in positions:
                if p.ticker not in seen:
                    seen.add(p.ticker)
                    tickers.append(p.ticker)
            return sorted(tickers)
        except Exception:
            return []

    def _on_contracts_changed(self, value: int):
        self._shares_spin.setValue(value * 100)
        self._refresh_calcs()

    def _on_status_changed(self, status: str):
        show_close = status in ("Closed", "Exercised")
        self._close_date_edit.setVisible(show_close)
        self._close_date_row_label.setVisible(show_close)
        self._close_prem_spin.setVisible(show_close)
        self._close_fees_spin.setVisible(show_close)
        self._close_prem_row_label.setVisible(show_close)
        self._close_fees_row_label.setVisible(show_close)
        self._refresh_calcs()

    def _refresh_calcs(self):
        svc = OptionsService
        premium   = self._premium_spin.value()
        shares    = self._shares_spin.value()
        fees      = self._fees_spin.value()
        strike    = self._strike_spin.value()
        status    = self._status_combo.currentText()
        close_px  = self._close_prem_spin.value() if self._status_combo.currentText() in ("Closed", "Exercised") else None
        close_f   = self._close_fees_spin.value()

        total_prem = svc.calc_total_premium(premium, shares)
        net_prem   = svc.calc_net_premium(total_prem, fees)
        net_share  = svc.calc_net_per_share(net_prem, shares)
        total_val  = svc.calc_total_value(strike, shares)
        pl         = svc.calc_profit_loss(status, net_prem, close_px, shares, close_f)

        self._lbl_total_prem.setText(f"${total_prem:,.2f}")
        self._lbl_net_prem.setText(f"${net_prem:,.2f}")
        self._lbl_net_share.setText(f"${net_share:,.4f}")
        self._lbl_total_val.setText(f"${total_val:,.2f}")

        is_put = self._put_rb.isChecked()
        self._total_val_lbl_row.setText("Capital Required:" if is_put else "Total Value at Strike:")

        if pl is None:
            self._lbl_pl.setText("—")
            self._lbl_pl.setStyleSheet("color: #7488B8;")
        elif pl >= 0:
            self._lbl_pl.setText(f"${pl:,.2f}")
            self._lbl_pl.setStyleSheet("color: #38D88A; font-size: 13px; font-weight: 600;")
        else:
            self._lbl_pl.setText(f"−${abs(pl):,.2f}")
            self._lbl_pl.setStyleSheet("color: #FF5068; font-size: 13px; font-weight: 600;")

    def _populate(self):
        """Pre-fill form when editing an existing position."""
        pos = self._svc.get_position(self._position_id)
        if not pos:
            return
        # Ticker
        idx = self._ticker_combo.findText(pos.ticker)
        if idx >= 0:
            self._ticker_combo.setCurrentIndex(idx)
        else:
            self._ticker_combo.setEditText(pos.ticker)
        # Type
        if pos.option_type == "Call":
            self._call_rb.setChecked(True)
        else:
            self._put_rb.setChecked(True)
        self._premium_spin.setValue(pos.premium)
        self._strike_spin.setValue(pos.strike_price)
        if pos.open_date:
            self._open_date_edit.setDate(QDate(pos.open_date.year, pos.open_date.month, pos.open_date.day))
        self._expiry_edit.setDate(QDate(pos.end_date.year, pos.end_date.month, pos.end_date.day))
        self._contracts_spin.setValue(pos.num_contracts)
        self._shares_spin.setValue(pos.num_shares)
        self._fees_spin.setValue(pos.fees)
        status_idx = self._status_combo.findText(pos.status)
        if status_idx >= 0:
            self._status_combo.setCurrentIndex(status_idx)
        if pos.close_date:
            self._close_date_edit.setDate(QDate(pos.close_date.year, pos.close_date.month, pos.close_date.day))
        if pos.close_premium is not None:
            self._close_prem_spin.setValue(pos.close_premium)
        if pos.close_fees:
            self._close_fees_spin.setValue(pos.close_fees)
        if pos.notes:
            self._notes_edit.setPlainText(pos.notes)
        self._refresh_calcs()

    # ---------------------------------------------------------------- accept

    def _on_accept(self):
        ticker = self._ticker_combo.currentText().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Validation", "Ticker is required.")
            return
        if self._premium_spin.value() <= 0:
            QMessageBox.warning(self, "Validation", "Premium must be greater than zero.")
            return
        if self._strike_spin.value() <= 0:
            QMessageBox.warning(self, "Validation", "Strike price must be greater than zero.")
            return

        option_type   = "Call" if self._call_rb.isChecked() else "Put"
        premium       = self._premium_spin.value()
        strike_price  = self._strike_spin.value()
        open_date     = self._open_date_edit.date().toPython()
        end_date      = self._expiry_edit.date().toPython()
        num_contracts = self._contracts_spin.value()
        num_shares    = self._shares_spin.value()
        fees          = self._fees_spin.value()
        status        = self._status_combo.currentText()
        is_closed     = status in ("Closed", "Exercised")
        close_date    = self._close_date_edit.date().toPython() if is_closed else None
        close_prem    = self._close_prem_spin.value() if is_closed else None
        close_fees    = self._close_fees_spin.value() if is_closed else 0.0
        notes         = self._notes_edit.toPlainText().strip() or None

        try:
            if self._editing:
                self._svc.update_position(
                    self._position_id,
                    ticker=ticker, option_type=option_type,
                    premium=premium, strike_price=strike_price,
                    open_date=open_date, end_date=end_date,
                    num_contracts=num_contracts, num_shares=num_shares,
                    fees=fees, status=status,
                    close_premium=close_prem, close_fees=close_fees,
                    close_date=close_date, notes=notes,
                )
            else:
                self._svc.add_position(
                    ticker=ticker, option_type=option_type,
                    premium=premium, strike_price=strike_price,
                    open_date=open_date, end_date=end_date,
                    num_contracts=num_contracts, num_shares=num_shares,
                    fees=fees, status=status,
                    close_premium=close_prem, close_fees=close_fees,
                    close_date=close_date, notes=notes,
                )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to save option:\n{exc}")
