"""
Position Size Calculator Dialog
Calculates recommended share count based on account equity and risk parameters.
Also calculates historical CAGR and estimates time to reach a target price.
"""

import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QFrame, QComboBox, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt, QTimer

_DLG_SS = """
QDialog {
    background-color: #0F1117;
    color: #DDE8FF;
}
QGroupBox {
    background-color: #111520;
    border: 1px solid #222844;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-size: 12px;
    font-weight: 600;
    color: #7488B8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #7488B8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
QLabel {
    color: #7488B8;
    font-size: 12px;
}
QLabel#value_label {
    color: #DDE8FF;
    font-size: 13px;
    font-weight: 600;
}
QLabel#section_title {
    color: #5295FF;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
}
QLabel#result_shares {
    color: #5295FF;
    font-size: 22px;
    font-weight: 700;
}
QLabel#warn_label {
    color: #FF5068;
    font-size: 11px;
    font-weight: 600;
}
QLabel#fetched_label {
    color: #38D88A;
    font-size: 12px;
    font-weight: 600;
}
QLineEdit {
    background-color: #191D2E;
    border: 1px solid #2C3356;
    border-radius: 6px;
    color: #DDE8FF;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: #3A52A8;
}
QLineEdit:focus { border-color: #5295FF; }
QDoubleSpinBox {
    background-color: #191D2E;
    border: 1px solid #2C3356;
    border-radius: 6px;
    color: #DDE8FF;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: #3A52A8;
}
QDoubleSpinBox:focus { border-color: #5295FF; }
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0; border: none; }
QComboBox {
    background-color: #191D2E;
    border: 1px solid #2C3356;
    border-radius: 6px;
    color: #DDE8FF;
    padding: 5px 10px;
    font-size: 12px;
    min-width: 80px;
}
QComboBox:focus { border-color: #5295FF; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #191D2E;
    color: #DDE8FF;
    border: 1px solid #2C3356;
    selection-background-color: #2C3A6A;
}
QPushButton {
    background-color: #1E2540;
    color: #DDE8FF;
    border: 1px solid #2C3356;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #263057;
    border-color: #5295FF;
    color: #5295FF;
}
QPushButton:pressed { background-color: #1A2044; }
QPushButton#fetch_btn {
    background-color: #1A3A5C;
    border-color: #2E5A8A;
    color: #5CB8FF;
    padding: 7px 14px;
}
QPushButton#fetch_btn:hover {
    background-color: #1F4A72;
    border-color: #5295FF;
    color: #82CAFF;
}
QFrame#divider {
    background-color: #222844;
    max-height: 1px;
    min-height: 1px;
}
QScrollArea {
    background: #0F1117;
    border: none;
}
"""


def _spin(min_val=0.0, max_val=999_999_999.0, decimals=2,
          prefix="", suffix="", value=0.0):
    s = QDoubleSpinBox()
    s.setMinimum(min_val)
    s.setMaximum(max_val)
    s.setDecimals(decimals)
    s.setSingleStep(0.01)
    if prefix:
        s.setPrefix(prefix)
    if suffix:
        s.setSuffix(suffix)
    s.setValue(value)
    s.setFixedHeight(34)
    return s


def _divider():
    d = QFrame()
    d.setObjectName("divider")
    d.setFrameShape(QFrame.HLine)
    return d


class _ResultRow:
    """Label-value pair for a results section."""

    def __init__(self, parent_layout, label_text, label_width=190):
        row = QHBoxLayout()
        row.setContentsMargins(0, 1, 0, 1)
        lbl = QLabel(label_text)
        lbl.setFixedWidth(label_width)
        lbl.setStyleSheet("color: #7488B8; font-size: 12px;")
        self.val = QLabel("--")
        self.val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.val.setStyleSheet("color: #4A5578; font-size: 13px; font-weight: 600;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.val)
        parent_layout.addLayout(row)

    def set(self, text, color="#DDE8FF"):
        self.val.setText(text)
        self.val.setStyleSheet(
            "color: " + color + "; font-size: 13px; font-weight: 600;")

    def clear(self):
        self.val.setText("--")
        self.val.setStyleSheet("color: #4A5578; font-size: 13px; font-weight: 600;")


class PositionSizeCalculator(QDialog):
    """
    Modal dialog for calculating position size based on risk parameters,
    with CAGR analysis and time-to-target estimation.

    Position sizing (risk-based):
        Dollar Risk = Total Portfolio Equity x (Risk% / 100)
        Shares      = Dollar Risk / (Entry Price - Stop Loss)
        Position $  = Shares x Entry Price

    CAGR:
        CAGR = (End Price / Start Price)^(1 / years) - 1

    Time to target (at historical CAGR):
        years = ln(Target / Current) / ln(1 + CAGR)
    """

    _PERIODS = [("1 Year", 1), ("3 Years", 3), ("5 Years", 5), ("10 Years", 10)]

    def __init__(self, portfolio_service, parent=None):
        super().__init__(parent)
        self.portfolio_service = portfolio_service
        self._fetched_price = 0.0
        self._company_name = ""
        self._cagr = 0.0
        self._ticker = ""

        self.setWindowTitle("Position Size Calculator")
        self.setMinimumWidth(540)
        self.setMinimumHeight(300)
        self.resize(560, 820)
        self.setSizeGripEnabled(True)
        self.setModal(True)
        self.setStyleSheet(_DLG_SS)

        self._build_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._prefill_equity)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer layout holds only the scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        _content = QWidget()
        _content.setStyleSheet("background: #0F1117;")
        scroll.setWidget(_content)

        root = QVBoxLayout(_content)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        # ── Account ──────────────────────────────────────────────────────────
        acct_box = QGroupBox("ACCOUNT")
        acct_form = QFormLayout(acct_box)
        acct_form.setLabelAlignment(Qt.AlignRight)
        acct_form.setSpacing(8)
        acct_form.setContentsMargins(8, 8, 8, 8)

        self.equity_spin = _spin(0, 999_999_999, 2, "$", value=0.0)
        self.equity_spin.setToolTip("Total market value of your portfolio")
        acct_form.addRow("Total Portfolio Equity:", self.equity_spin)

        self.liquid_spin = _spin(0, 999_999_999, 2, "$", value=0.0)
        self.liquid_spin.setToolTip("Cash available to deploy")
        acct_form.addRow("Liquid / Available Cash:", self.liquid_spin)

        root.addWidget(acct_box)

        # ── Stock ─────────────────────────────────────────────────────────────
        stock_box = QGroupBox("STOCK")
        stock_vbox = QVBoxLayout(stock_box)
        stock_vbox.setSpacing(8)
        stock_vbox.setContentsMargins(8, 8, 8, 8)

        ticker_row = QHBoxLayout()
        self.ticker_edit = QLineEdit()
        self.ticker_edit.setPlaceholderText("e.g. AAPL")
        self.ticker_edit.setFixedHeight(34)
        self.ticker_edit.setMaximumWidth(120)
        self.fetch_btn = QPushButton("Fetch Price")
        self.fetch_btn.setObjectName("fetch_btn")
        self.fetch_btn.setFixedHeight(34)
        self.fetch_status = QLabel("")
        self.fetch_status.setObjectName("fetched_label")
        ticker_row.addWidget(QLabel("Ticker:"))
        ticker_row.addWidget(self.ticker_edit)
        ticker_row.addWidget(self.fetch_btn)
        ticker_row.addWidget(self.fetch_status)
        ticker_row.addStretch()
        stock_vbox.addLayout(ticker_row)

        company_row = QHBoxLayout()
        self.company_label = QLabel("--")
        self.company_label.setObjectName("value_label")
        company_row.addWidget(QLabel("Company:"))
        company_row.addWidget(self.company_label)
        company_row.addStretch()
        stock_vbox.addLayout(company_row)

        price_form = QFormLayout()
        price_form.setLabelAlignment(Qt.AlignRight)
        price_form.setSpacing(8)

        self.current_price_label = QLabel("--")
        self.current_price_label.setObjectName("value_label")
        price_form.addRow("Current Price:", self.current_price_label)

        self.entry_spin = _spin(0.001, 999_999, 4, "$", value=0.0)
        self.entry_spin.setToolTip("Your intended buy price (defaults to fetched price)")
        price_form.addRow("Entry Price:", self.entry_spin)

        self.stop_spin = _spin(0.0, 999_999, 4, "$", value=0.0)
        self.stop_spin.setToolTip("Stop-loss price -- used to calculate dollar risk per share")
        price_form.addRow("Stop Loss Price:", self.stop_spin)

        self.target_spin = _spin(0.0, 999_999, 4, "$", value=0.0)
        self.target_spin.setToolTip("Target / take-profit price -- used for R:R and time-to-target")
        price_form.addRow("Target Price:", self.target_spin)

        stock_vbox.addLayout(price_form)
        root.addWidget(stock_box)

        # ── Risk ─────────────────────────────────────────────────────────────
        risk_box = QGroupBox("RISK")
        risk_form = QFormLayout(risk_box)
        risk_form.setLabelAlignment(Qt.AlignRight)
        risk_form.setSpacing(8)
        risk_form.setContentsMargins(8, 8, 8, 8)

        self.risk_pct_spin = _spin(0.01, 100.0, 2, suffix=" %", value=2.0)
        self.risk_pct_spin.setMaximumWidth(120)
        self.risk_dollar_label = QLabel("= $ --")
        self.risk_dollar_label.setObjectName("value_label")

        risk_row = QHBoxLayout()
        risk_row.addWidget(self.risk_pct_spin)
        risk_row.addWidget(self.risk_dollar_label)
        risk_row.addStretch()
        risk_form.addRow("Risk % of Portfolio:", risk_row)
        root.addWidget(risk_box)

        # ── CAGR Analysis ─────────────────────────────────────────────────────
        cagr_box = QGroupBox("CAGR ANALYSIS")
        cagr_vbox = QVBoxLayout(cagr_box)
        cagr_vbox.setSpacing(8)
        cagr_vbox.setContentsMargins(8, 8, 8, 8)

        period_row = QHBoxLayout()
        period_row.addWidget(QLabel("Historical period:"))
        self.period_combo = QComboBox()
        for label, _ in self._PERIODS:
            self.period_combo.addItem(label)
        self.period_combo.setCurrentIndex(2)
        self.period_combo.setFixedHeight(34)
        self.period_combo.setMaximumWidth(130)
        period_row.addWidget(self.period_combo)
        self.cagr_fetch_btn = QPushButton("Calculate CAGR")
        self.cagr_fetch_btn.setObjectName("fetch_btn")
        self.cagr_fetch_btn.setFixedHeight(34)
        self.cagr_status = QLabel("")
        self.cagr_status.setObjectName("fetched_label")
        period_row.addWidget(self.cagr_fetch_btn)
        period_row.addWidget(self.cagr_status)
        period_row.addStretch()
        cagr_vbox.addLayout(period_row)

        cagr_results = QVBoxLayout()
        cagr_results.setSpacing(2)
        self.r_start_price = _ResultRow(cagr_results, "Price N years ago")
        self.r_cagr        = _ResultRow(cagr_results, "Historical CAGR")
        self.r_time_target = _ResultRow(cagr_results, "Est. years to target")
        self.r_target_date = _ResultRow(cagr_results, "Implied target date")
        cagr_vbox.addLayout(cagr_results)
        root.addWidget(cagr_box)

        # ── Divider + Results ─────────────────────────────────────────────────
        root.addWidget(_divider())

        results_lbl = QLabel("POSITION SIZING RESULTS")
        results_lbl.setObjectName("section_title")
        root.addWidget(results_lbl)

        shares_row = QHBoxLayout()
        shares_row.setContentsMargins(0, 4, 0, 4)
        shares_title = QLabel("Recommended Shares")
        shares_title.setStyleSheet("color: #7488B8; font-size: 12px;")
        self.shares_big_label = QLabel("--")
        self.shares_big_label.setObjectName("result_shares")
        self.shares_big_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shares_row.addWidget(shares_title)
        shares_row.addStretch()
        shares_row.addWidget(self.shares_big_label)
        root.addLayout(shares_row)

        pos_results = QVBoxLayout()
        pos_results.setSpacing(2)
        self.r_position_value = _ResultRow(pos_results, "Position Value")
        self.r_max_affordable = _ResultRow(pos_results, "Max Affordable (liquid)")
        self.r_risk_dollar    = _ResultRow(pos_results, "Dollar Risk")
        self.r_reward_dollar  = _ResultRow(pos_results, "Reward (at target)")
        self.r_rr_ratio       = _ResultRow(pos_results, "Risk : Reward")
        self.r_pct_portfolio  = _ResultRow(pos_results, "% of Portfolio")
        self.r_pct_liquid     = _ResultRow(pos_results, "% of Liquid Cash")
        root.addLayout(pos_results)

        self.warn_label = QLabel("")
        self.warn_label.setObjectName("warn_label")
        self.warn_label.setWordWrap(True)
        self.warn_label.setVisible(False)
        root.addWidget(self.warn_label)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.fetch_btn.clicked.connect(self._fetch_price)
        self.ticker_edit.returnPressed.connect(self._fetch_price)
        self.cagr_fetch_btn.clicked.connect(self._fetch_cagr)
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)

        for spin in (self.equity_spin, self.liquid_spin, self.entry_spin,
                     self.stop_spin, self.target_spin, self.risk_pct_spin):
            spin.valueChanged.connect(self._recalculate)

        self.target_spin.valueChanged.connect(self._recalculate_cagr_results)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _prefill_equity(self):
        try:
            value = self.portfolio_service.get_portfolio_value()
            if value and value > 0:
                self.equity_spin.setValue(value)
        except Exception:
            pass

    def _fetch_price(self):
        ticker = self.ticker_edit.text().strip().upper()
        if not ticker:
            self.fetch_status.setText("Enter a ticker first")
            self.fetch_status.setStyleSheet(
                "color: #FF5068; font-size: 11px; font-weight: 600;")
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")
        self.fetch_status.setText("")
        self._ticker = ticker

        try:
            data = self.portfolio_service.market_data_service.get_stock_data(ticker)
            if data:
                price   = data.get("current_price", 0.0) or 0.0
                company = data.get("company_name", ticker) or ticker
            else:
                price   = 0.0
                company = ticker

            if price > 0:
                self._fetched_price = price
                self._company_name  = company
                self.company_label.setText(company)
                self.current_price_label.setText("$" + "{:,.4f}".format(price))
                self.entry_spin.setValue(price)
                self.fetch_status.setText("OK $" + "{:,.2f}".format(price))
                self.fetch_status.setStyleSheet(
                    "color: #38D88A; font-size: 12px; font-weight: 600;")
                self._fetch_cagr()
            else:
                self.fetch_status.setText("Price unavailable")
                self.fetch_status.setStyleSheet(
                    "color: #FF5068; font-size: 11px; font-weight: 600;")
        except Exception as exc:
            self.fetch_status.setText("Error: " + str(exc))
            self.fetch_status.setStyleSheet(
                "color: #FF5068; font-size: 11px; font-weight: 600;")
        finally:
            self.fetch_btn.setEnabled(True)
            self.fetch_btn.setText("Fetch Price")

        self._recalculate()

    def _fetch_cagr(self):
        ticker = self._ticker or self.ticker_edit.text().strip().upper()
        if not ticker:
            return

        period_idx = self.period_combo.currentIndex()
        _, years   = self._PERIODS[period_idx]

        self.cagr_fetch_btn.setEnabled(False)
        self.cagr_fetch_btn.setText("Fetching...")
        self.cagr_status.setText("")

        try:
            hist = self.portfolio_service.market_data_service.get_price_history(
                ticker, years)
            if hist:
                self._cagr = hist["cagr"]
                direction  = "+" if self._cagr >= 0 else "-"
                color      = "#38D88A" if self._cagr >= 0 else "#FF5068"
                self.r_start_price.set(
                    "${:,.2f}  ({:.1f} yrs ago)".format(
                        hist["start_price"], hist["actual_years"]))
                self.r_cagr.set(
                    "{}{:.2f}% / year".format(direction, abs(self._cagr) * 100),
                    color)
                self.cagr_status.setText(
                    "CAGR {:.1f}%".format(self._cagr * 100))
                self.cagr_status.setStyleSheet(
                    "color: " + color + "; font-size: 12px; font-weight: 600;")
            else:
                self._cagr = 0.0
                self.r_start_price.clear()
                self.r_cagr.clear()
                self.cagr_status.setText("Data unavailable")
                self.cagr_status.setStyleSheet(
                    "color: #FF5068; font-size: 11px; font-weight: 600;")
        except Exception as exc:
            self._cagr = 0.0
            self.cagr_status.setText("Error: " + str(exc))
            self.cagr_status.setStyleSheet(
                "color: #FF5068; font-size: 11px; font-weight: 600;")
        finally:
            self.cagr_fetch_btn.setEnabled(True)
            self.cagr_fetch_btn.setText("Calculate CAGR")

        self._recalculate_cagr_results()

    def _on_period_changed(self):
        if self._ticker:
            self._fetch_cagr()

    def _recalculate_cagr_results(self):
        """Update time-to-target rows from current CAGR + target price."""
        current = self.entry_spin.value()
        target  = self.target_spin.value()
        cagr    = self._cagr

        if cagr <= 0 or current <= 0 or target <= current:
            self.r_time_target.clear()
            self.r_target_date.clear()
            return

        years_needed = math.log(target / current) / math.log(1 + cagr)
        whole_years  = int(years_needed)
        frac_months  = round((years_needed - whole_years) * 12)

        if whole_years == 0:
            span = "{} month{}".format(frac_months, "s" if frac_months != 1 else "")
        elif frac_months == 0:
            span = "{} year{}".format(whole_years, "s" if whole_years != 1 else "")
        else:
            span = "{} year{} {} month{}".format(
                whole_years, "s" if whole_years != 1 else "",
                frac_months, "s" if frac_months != 1 else "")

        color = ("#38D88A" if years_needed <= 5
                 else "#FFD166" if years_needed <= 10
                 else "#DDE8FF")

        self.r_time_target.set(
            "approx. {}  ({:.1f} yrs)".format(span, years_needed), color)

        try:
            target_date = datetime.now() + timedelta(days=years_needed * 365.25)
            self.r_target_date.set(target_date.strftime("%B %Y"), color)
        except Exception:
            self.r_target_date.clear()

    def _recalculate(self):
        """Live-update all position-sizing result fields."""
        equity   = self.equity_spin.value()
        liquid   = self.liquid_spin.value()
        entry    = self.entry_spin.value()
        stop     = self.stop_spin.value()
        target   = self.target_spin.value()
        risk_pct = self.risk_pct_spin.value()

        risk_dollar = equity * (risk_pct / 100.0) if equity > 0 else 0.0
        self.risk_dollar_label.setText(
            "= ${:,.2f}".format(risk_dollar) if risk_dollar > 0 else "= $ --")

        self._recalculate_cagr_results()

        if entry <= 0:
            self._clear_results()
            return

        warnings = []

        risk_per_share = entry - stop
        if risk_per_share > 0 and risk_dollar > 0:
            shares = risk_dollar / risk_per_share
        else:
            shares = ((equity * (risk_pct / 100.0)) / entry
                      if equity > 0 and entry > 0 else 0.0)
            if stop >= entry and stop > 0:
                warnings.append("Stop loss must be below entry price.")

        shares = math.floor(shares)
        position_value = shares * entry

        max_shares = math.floor(liquid / entry) if liquid > 0 and entry > 0 else 0
        if shares > max_shares > 0:
            warnings.append(
                "Position (${:,.2f}) exceeds liquid cash. "
                "Max affordable: {:,} shares (${:,.2f}).".format(
                    position_value, max_shares, max_shares * entry))

        reward_dollar = 0.0
        rr_ratio      = 0.0
        if target > entry > 0 and shares > 0:
            reward_dollar = (target - entry) * shares
            if risk_dollar > 0:
                rr_ratio = reward_dollar / risk_dollar

        pct_portfolio = (position_value / equity * 100) if equity > 0 else 0.0
        pct_liquid    = (position_value / liquid * 100) if liquid > 0 else 0.0

        if shares > 0:
            self.shares_big_label.setText("{:,}".format(shares))
            self.shares_big_label.setStyleSheet(
                "color: #5295FF; font-size: 22px; font-weight: 700;")
        else:
            self.shares_big_label.setText("--")
            self.shares_big_label.setStyleSheet(
                "color: #4A5578; font-size: 22px; font-weight: 700;")

        if shares > 0:
            self.r_position_value.set("${:,.2f}".format(position_value))
        else:
            self.r_position_value.clear()

        if max_shares > 0:
            c = "#38D88A" if max_shares >= shares else "#FF5068"
            self.r_max_affordable.set(
                "{:,} shares  (${:,.2f})".format(max_shares, max_shares * entry), c)
        else:
            self.r_max_affordable.clear()

        if risk_dollar > 0:
            self.r_risk_dollar.set("${:,.2f}".format(risk_dollar), "#FF9B5E")
        else:
            self.r_risk_dollar.clear()

        if reward_dollar > 0:
            self.r_reward_dollar.set("${:,.2f}".format(reward_dollar), "#38D88A")
        else:
            self.r_reward_dollar.clear()

        if rr_ratio > 0:
            c = ("#38D88A" if rr_ratio >= 2.0
                 else "#FFD166" if rr_ratio >= 1.0
                 else "#FF5068")
            self.r_rr_ratio.set("1 : {:.2f}".format(rr_ratio), c)
        else:
            self.r_rr_ratio.clear()

        if pct_portfolio > 0:
            c = ("#38D88A" if pct_portfolio <= 10
                 else "#FFD166" if pct_portfolio <= 25
                 else "#FF5068")
            self.r_pct_portfolio.set("{:.1f}%".format(pct_portfolio), c)
        else:
            self.r_pct_portfolio.clear()

        if pct_liquid > 0:
            c = ("#38D88A" if pct_liquid <= 50
                 else "#FFD166" if pct_liquid <= 100
                 else "#FF5068")
            self.r_pct_liquid.set("{:.1f}%".format(pct_liquid), c)
        else:
            self.r_pct_liquid.clear()

        if warnings:
            self.warn_label.setText("  WARNING  " + "   WARNING  ".join(warnings))
            self.warn_label.setVisible(True)
        else:
            self.warn_label.setVisible(False)

    def _clear_results(self):
        self.shares_big_label.setText("--")
        self.shares_big_label.setStyleSheet(
            "color: #4A5578; font-size: 22px; font-weight: 700;")
        for row in (self.r_position_value, self.r_max_affordable, self.r_risk_dollar,
                    self.r_reward_dollar, self.r_rr_ratio, self.r_pct_portfolio,
                    self.r_pct_liquid):
            row.clear()
        self.warn_label.setVisible(False)
