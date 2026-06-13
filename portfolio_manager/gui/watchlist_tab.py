"""
Watchlist tab for Portfolio Manager.

Columns (in order):
  Ticker | Company | Entry Date | Days | Entry Price | Current Price |
  Change $ | Change % | Ann. Return | Hypo Shares | Hypo Cost | Hypo Value |
  Hypo P&L | Target Price | To Target % | Notes
"""

import sys
import os
from datetime import date, datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame, QMessageBox, QAbstractItemView,
    QToolBar, QSizePolicy,
)
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtCore import Qt, QSize

from gui.icons import get_icon
from services.watchlist_service import WatchlistService
from services.portfolio_service import PortfolioService
from gui.add_watchlist_dialog import AddWatchlistItemDialog
from gui.edit_watchlist_dialog import EditWatchlistItemDialog

# Column indices — keep in sync with HEADERS below
COL_TICKER    = 0
COL_COMPANY   = 1
COL_ENTRY_DATE= 2
COL_DAYS      = 3
COL_ENTRY_PX  = 4
COL_CUR_PX    = 5
COL_CHG_D     = 6   # change in $
COL_CHG_PCT   = 7   # change in %
COL_ANN_RET   = 8   # annualised return
COL_HYPO_SH   = 9   # hypothetical shares
COL_HYPO_COST = 10  # hypothetical cost basis
COL_HYPO_VAL  = 11  # hypothetical market value
COL_HYPO_PL   = 12  # hypothetical P&L
COL_TARGET    = 13  # target price
COL_TO_TGT    = 14  # distance to target %
COL_NOTES     = 15

HEADERS = [
    "Ticker", "Company", "Entry Date", "Days",
    "Entry Price", "Current Price", "Change $", "Change %",
    "Ann. Return", "Hypo Shares", "Hypo Cost", "Hypo Value",
    "Hypo P&L", "Target Price", "To Target %", "Notes",
]

_GREEN  = QColor("#38D88A")
_RED    = QColor("#FF5068")
_MUTED  = QColor("#7488B8")
_TEXT   = QColor("#DDE8FF")
_YELLOW = QColor("#F5C842")


def _right_item(text: str, fg: QColor | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
    if fg:
        item.setForeground(fg)
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    return item


def _left_item(text: str, fg: QColor | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(int(Qt.AlignLeft | Qt.AlignVCenter))
    if fg:
        item.setForeground(fg)
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    return item


def _annualised_return(entry_price: float, current_price: float, days: int) -> float | None:
    """CAGR from entry to today. Returns None when period < 1 day."""
    if days < 1 or entry_price <= 0:
        return None
    years = days / 365.25
    return ((current_price / entry_price) ** (1.0 / years) - 1.0) * 100.0


class WatchlistTab(QWidget):
    """Tab widget showing the user's stock watchlist with live performance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._watchlist_service = WatchlistService()
        self._portfolio_service = PortfolioService()
        # item_id stored per row for delete operations
        self._row_ids: list[int] = []
        self._setup_ui()
        self.load_data()

    # ---------------------------------------------------------------- UI --

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── toolbar ──────────────────────────────────────────────────────
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #191D2E;
                border: none;
                border-bottom: 1px solid #222844;
                padding: 5px 12px;
                spacing: 2px;
            }
            QToolButton {
                background-color: transparent;
                color: #BECCE8;
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QToolButton:hover {
                background-color: rgba(74, 158, 255, 0.15);
                color: #5295FF;
            }
            QToolButton:pressed { background-color: rgba(74, 158, 255, 0.28); }
            QToolBar::separator {
                background-color: #222844;
                width: 1px;
                margin: 4px 6px;
            }
        """)

        add_action = QAction(get_icon("ACT_ADD"), "Add Stock", self)
        add_action.setToolTip("Add a stock to the watchlist")
        add_action.triggered.connect(self._on_add)
        toolbar.addAction(add_action)

        toolbar.addSeparator()

        edit_action = QAction(get_icon("ACT_EDIT"), "Edit", self)
        edit_action.setToolTip("Edit selected watchlist item")
        edit_action.triggered.connect(self._on_edit)
        toolbar.addAction(edit_action)

        toolbar.addSeparator()

        delete_action = QAction(get_icon("ACT_DELETE"), "Remove", self)
        delete_action.setToolTip("Remove selected stock from watchlist")
        delete_action.triggered.connect(self._on_remove)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        refresh_action = QAction(get_icon("ACT_REFRESH"), "Refresh", self)
        refresh_action.setToolTip("Refresh current prices")
        refresh_action.triggered.connect(self.load_data)
        toolbar.addAction(refresh_action)

        # spacer to push any right-side items over
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self._status_label = QLabel("  ")
        self._status_label.setStyleSheet("color: #7488B8; font-size: 12px; padding-right: 8px;")
        toolbar.addWidget(self._status_label)

        layout.addWidget(toolbar)

        # ── table ─────────────────────────────────────────────────────────
        self._table = QTableWidget(0, len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setSortingEnabled(True)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(COL_TICKER,    QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_COMPANY,   QHeaderView.Stretch)
        header.setSectionResizeMode(COL_NOTES,     QHeaderView.Stretch)
        for col in range(len(HEADERS)):
            if col not in (COL_COMPANY, COL_NOTES):
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #0F1117;
                alternate-background-color: #161928;
                color: #DDE8FF;
                gridline-color: transparent;
                border: none;
                selection-background-color: rgba(74, 158, 255, 0.25);
                selection-color: #DDE8FF;
                outline: none;
            }
            QTableWidget::item {
                padding: 6px 10px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: rgba(74, 158, 255, 0.12);
            }
            QHeaderView::section {
                background-color: #191D2E;
                color: #7488B8;
                padding: 8px 10px;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-right: 1px solid #222844;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last { border-right: none; }
        """)

        self._table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self._table)

    # ---------------------------------------------------------- data -----

    def load_data(self):
        """Reload all watchlist items and refresh current prices."""
        self._status_label.setText("Fetching prices…")
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        self._row_ids = []

        items = self._watchlist_service.get_items()
        today = date.today()

        for item in items:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._row_ids.append(item.id)

            # Current price from portfolio service (yfinance-backed)
            try:
                cur_px = self._portfolio_service.get_current_price(item.ticker)
            except Exception:
                cur_px = None

            entry_px = item.entry_price
            days = (today - item.entry_date).days if item.entry_date else 0

            # ── computed metrics ─────────────────────────────────────────
            if cur_px and cur_px > 0:
                chg_d   = cur_px - entry_px
                chg_pct = (chg_d / entry_px) * 100.0 if entry_px else 0.0
                ann_ret = _annualised_return(entry_px, cur_px, days)
                price_color = _GREEN if chg_d >= 0 else _RED
            else:
                chg_d = chg_pct = ann_ret = None
                price_color = _MUTED

            # Hypothetical P&L
            shares = item.shares_hypothetical
            if shares and shares > 0 and cur_px and cur_px > 0:
                hypo_cost = entry_px * shares
                hypo_val  = cur_px  * shares
                hypo_pl   = hypo_val - hypo_cost
                hypo_color = _GREEN if hypo_pl >= 0 else _RED
            else:
                hypo_cost = hypo_val = hypo_pl = None
                hypo_color = _MUTED

            # Target distance
            if item.target_price and item.target_price > 0 and cur_px and cur_px > 0:
                to_tgt_pct = ((item.target_price - cur_px) / cur_px) * 100.0
                tgt_color  = _GREEN if to_tgt_pct >= 0 else _RED
            else:
                to_tgt_pct = None
                tgt_color  = _MUTED

            # ── populate cells ────────────────────────────────────────────
            ticker_item = QTableWidgetItem(item.ticker)
            ticker_item.setTextAlignment(int(Qt.AlignLeft | Qt.AlignVCenter))
            ticker_item.setFont(QFont("", -1, QFont.Bold))
            ticker_item.setForeground(_TEXT)
            ticker_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._table.setItem(row, COL_TICKER, ticker_item)

            self._table.setItem(row, COL_COMPANY,
                _left_item(item.company_name or ""))

            self._table.setItem(row, COL_ENTRY_DATE,
                _left_item(item.entry_date.strftime("%Y-%m-%d") if item.entry_date else ""))

            self._table.setItem(row, COL_DAYS,
                _right_item(str(days)))

            self._table.setItem(row, COL_ENTRY_PX,
                _right_item(f"${entry_px:,.2f}"))

            self._table.setItem(row, COL_CUR_PX,
                _right_item(f"${cur_px:,.2f}" if cur_px else "N/A", price_color))

            self._table.setItem(row, COL_CHG_D,
                _right_item(
                    f"${chg_d:+,.2f}" if chg_d is not None else "N/A",
                    _GREEN if (chg_d or 0) >= 0 else _RED if chg_d is not None else _MUTED,
                ))

            self._table.setItem(row, COL_CHG_PCT,
                _right_item(
                    f"{chg_pct:+.2f}%" if chg_pct is not None else "N/A",
                    _GREEN if (chg_pct or 0) >= 0 else _RED if chg_pct is not None else _MUTED,
                ))

            self._table.setItem(row, COL_ANN_RET,
                _right_item(
                    f"{ann_ret:+.2f}%" if ann_ret is not None else "N/A",
                    _GREEN if (ann_ret or 0) >= 0 else _RED if ann_ret is not None else _MUTED,
                ))

            self._table.setItem(row, COL_HYPO_SH,
                _right_item(f"{shares:,.4f}" if shares else "—"))

            self._table.setItem(row, COL_HYPO_COST,
                _right_item(f"${hypo_cost:,.2f}" if hypo_cost is not None else "—"))

            self._table.setItem(row, COL_HYPO_VAL,
                _right_item(f"${hypo_val:,.2f}" if hypo_val is not None else "—"))

            self._table.setItem(row, COL_HYPO_PL,
                _right_item(
                    f"${hypo_pl:+,.2f}" if hypo_pl is not None else "—",
                    hypo_color if hypo_pl is not None else _MUTED,
                ))

            self._table.setItem(row, COL_TARGET,
                _right_item(
                    f"${item.target_price:,.2f}" if item.target_price else "—"))

            self._table.setItem(row, COL_TO_TGT,
                _right_item(
                    f"{to_tgt_pct:+.2f}%" if to_tgt_pct is not None else "—",
                    tgt_color if to_tgt_pct is not None else _MUTED,
                ))

            self._table.setItem(row, COL_NOTES,
                _left_item(item.notes or ""))

        self._table.setSortingEnabled(True)
        count = len(items)
        self._status_label.setText(
            f"{count} stock{'s' if count != 1 else ''} watched"
        )

    # --------------------------------------------------------------- actions

    def _on_add(self):
        dialog = AddWatchlistItemDialog(self)
        if dialog.exec():
            self.load_data()

    def _on_edit(self, *_):
        item_id = self._selected_item_id()
        if item_id is None:
            QMessageBox.warning(self, "Edit", "Select a stock to edit.")
            return
        dialog = EditWatchlistItemDialog(item_id, self)
        if dialog.exec():
            self.load_data()

    def _on_remove(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Remove", "Select a stock to remove.")
            return

        row_idx = rows[0].row()
        ticker = self._table.item(row_idx, COL_TICKER)
        ticker_text = ticker.text() if ticker else "this stock"

        reply = QMessageBo