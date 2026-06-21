"""
Options Tracking Tab — covered calls and cash-secured puts.

Tree layout:  one top-level row per ticker (collapsible),
              child rows = individual option positions,
              sorted by ticker asc, end_date desc (most recent first).
"""
from __future__ import annotations
from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QSizePolicy, QToolBar, QMessageBox, QFrame,
)
from PySide6.QtGui import QAction, QColor, QFont, QBrush, QTextCharFormat
from PySide6.QtCore import Qt, QSize

from gui.icons import get_icon
from services.options_service import OptionsService
from services.portfolio_service import PortfolioService
from gui.add_option_dialog import AddOptionDialog

# ── Column indices ────────────────────────────────────────────────────────────
C_SHARE      = 0
C_OWNED      = 1
C_TYPE       = 2
C_PREMIUM    = 3
C_STRIKE     = 4
C_EXPIRY     = 5
C_SHARES     = 6
C_TOTAL_PREM = 7
C_FEES       = 8
C_NET_PREM   = 9
C_NET_SHARE  = 10
C_CONTRACTS  = 11
C_TOTAL_VAL  = 12
C_PL         = 13
C_STATUS     = 14
C_NOTES      = 15
_NUM_COLS    = 16

HEADERS = [
    "Share", "No. Owned", "Put/Call", "Premium", "Strike", "Expiry",
    "No. Shares", "Total Premium", "Fees", "Net Premium", "Net/Share",
    "Contracts", "Total Value", "P&L", "Status", "Notes",
]

# ── Colours ───────────────────────────────────────────────────────────────────
_GREEN  = QColor("#38D88A")
_RED    = QColor("#FF5068")
_MUTED  = QColor("#7488B8")
_TEXT   = QColor("#DDE8FF")
_YELLOW = QColor("#F5C842")
_BLUE   = QColor("#5295FF")
_BG_PAR = QColor("#191D2E")   # parent row background

_SS = """
    QWidget { background-color: #0F1117; color: #DDE8FF; }
    QTreeWidget {
        background-color: #0F1117;
        alternate-background-color: #161928;
        color: #DDE8FF;
        border: none;
        outline: none;
        gridline-color: transparent;
        selection-background-color: rgba(74, 158, 255, 0.25);
        selection-color: #DDE8FF;
    }
    QTreeWidget::item { padding: 5px 8px; border: none; }
    QTreeWidget::item:hover { background-color: rgba(74, 158, 255, 0.12); }
    QTreeWidget::branch {
        background-color: transparent;
    }
    QTreeWidget::branch:has-children:!has-siblings:closed,
    QTreeWidget::branch:closed:has-children:has-siblings {
        image: url(none);
    }
    QHeaderView::section {
        background-color: #191D2E; color: #7488B8;
        padding: 8px 8px; font-size: 11px; font-weight: 600;
        border: none; border-right: 1px solid #222844;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    QHeaderView::section:last { border-right: none; }
    QToolBar {
        background-color: #191D2E; border: none;
        border-bottom: 1px solid #222844; padding: 5px 12px; spacing: 2px;
    }
    QToolButton {
        background-color: transparent; color: #BECCE8; border: none;
        border-radius: 6px; padding: 5px 10px; font-size: 12px; font-weight: 500;
    }
    QToolButton:hover { background-color: rgba(74, 158, 255, 0.15); color: #5295FF; }
    QToolButton:pressed { background-color: rgba(74, 158, 255, 0.28); }
    QToolBar::separator { background-color: #222844; width: 1px; margin: 4px 6px; }
    QDoubleSpinBox {
        background-color: #191D2E; color: #DDE8FF;
        border: 1px solid #222844; border-radius: 6px;
        padding: 4px 8px; font-size: 13px;
    }
    QDoubleSpinBox:focus { border-color: #5295FF; }
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button
        { background-color: #222844; border: none; }
    QFrame#divider { background-color: #222844; }
    QLabel#funds_label { color: #7488B8; font-size: 12px; }
    QLabel#funds_value { color: #DDE8FF; font-size: 14px; font-weight: 700; }
    QLabel#funds_avail { color: #38D88A; font-size: 14px; font-weight: 700; }
    QLabel#funds_avail_neg { color: #FF5068; font-size: 14px; font-weight: 700; }
    QLabel#funds_locked { color: #F5C842; font-size: 14px; font-weight: 700; }
"""


def _money(v: float | None) -> str:
    if v is None:
        return "—"
    return f"${v:,.2f}"


def _right(item: QTreeWidgetItem, col: int, text: str,
           fg: QColor | None = None):
    item.setText(col, text)
    item.setTextAlignment(col, int(Qt.AlignRight | Qt.AlignVCenter))
    if fg:
        item.setForeground(col, QBrush(fg))


def _left(item: QTreeWidgetItem, col: int, text: str,
          fg: QColor | None = None):
    item.setText(col, text)
    item.setTextAlignment(col, int(Qt.AlignLeft | Qt.AlignVCenter))
    if fg:
        item.setForeground(col, QBrush(fg))


class OptionsTab(QWidget):
    """Main options-tracking widget."""

    def __init__(self, options_service: OptionsService,
                 portfolio_service: PortfolioService,
                 personal_finance_service=None, parent=None):
        super().__init__(parent)
        self._svc   = options_service
        self._port  = portfolio_service
        self._pf    = personal_finance_service
        self._setup_ui()
        self.refresh()

    # ------------------------------------------------------------------ UI --

    def _setup_ui(self):
        self.setStyleSheet(_SS)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ───────────────────────────────────────────────────────
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        add_act = QAction(get_icon("ACT_ADD"), "Add Option", self)
        add_act.setToolTip("Add a new covered call or cash-secured put")
        add_act.triggered.connect(self._on_add)
        toolbar.addAction(add_act)

        toolbar.addSeparator()

        edit_act = QAction(get_icon("ACT_EDIT"), "Edit", self)
        edit_act.setToolTip("Edit selected option")
        edit_act.triggered.connect(self._on_edit)
        toolbar.addAction(edit_act)

        toolbar.addSeparator()

        del_act = QAction(get_icon("ACT_DELETE"), "Remove", self)
        del_act.setToolTip("Delete selected option")
        del_act.triggered.connect(self._on_delete)
        toolbar.addAction(del_act)

        toolbar.addSeparator()

        ref_act = QAction(get_icon("ACT_REFRESH"), "Refresh", self)
        ref_act.setToolTip("Refresh display")
        ref_act.triggered.connect(self.refresh)
        toolbar.addAction(ref_act)

        root.addWidget(toolbar)

        # ── Funds panel ───────────────────────────────────────────────────
        funds_frame = QFrame()
        funds_frame.setStyleSheet(
            "QFrame { background-color: #111520; border-bottom: 1px solid #222844; }"
        )
        funds_row = QHBoxLayout(funds_frame)
        funds_row.setContentsMargins(16, 10, 16, 10)
        funds_row.setSpacing(0)

        def _funds_cell(label_text: str) -> QLabel:
            lbl = QLabel(label_text)
            lbl.setObjectName("funds_label")
            return lbl

        # Ledger balance (read-only — sourced from Personal Finance ledger)
        cash_lbl         = _funds_cell("Ledger Balance")
        self._cash_val   = QLabel("$0.00")
        self._cash_val.setObjectName("funds_value")

        sep1 = self._vline()
        sep2 = self._vline()

        locked_lbl        = _funds_cell("Locked Capital (Puts)")
        self._locked_val  = QLabel("$0.00")
        self._locked_val.setObjectName("funds_locked")

        avail_lbl         = _funds_cell("Available Funds")
        self._avail_val   = QLabel("$0.00")
        self._avail_val.setObjectName("funds_avail")

        for w in (cash_lbl, self._cash_val, sep1,
                  locked_lbl, self._locked_val, sep2,
                  avail_lbl, self._avail_val):
            funds_row.addWidget(w)
            if w not in (sep1, sep2):
                funds_row.addSpacing(12)

        funds_row.addStretch()
        root.addWidget(funds_frame)

        # ── Tree ──────────────────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setColumnCount(_NUM_COLS)
        self._tree.setHeaderLabels(HEADERS)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self._tree.setSortingEnabled(False)
        self._tree.setAnimated(True)
        self._tree.setIndentation(20)
        self._tree.doubleClicked.connect(self._on_edit)

        hdr = self._tree.header()
        hdr.setStretchLastSection(True)
        hdr.setDefaultSectionSize(100)
        self._tree.setColumnWidth(C_SHARE,      120)
        self._tree.setColumnWidth(C_OWNED,       80)
        self._tree.setColumnWidth(C_TYPE,        90)
        self._tree.setColumnWidth(C_EXPIRY,      90)
        self._tree.setColumnWidth(C_STATUS,      90)
        self._tree.setColumnWidth(C_NOTES,      160)

        root.addWidget(self._tree)

    @staticmethod
    def _vline() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.VLine)
        f.setObjectName("divider")
        f.setFixedWidth(1)
        f.setFixedHeight(32)
        return f

    # ---------------------------------------------------------------- data --

    def refresh(self):
        """Reload all option positions into the tree."""
        # Remember which tickers were expanded
        expanded = set()
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if item.isExpanded():
                expanded.add(item.text(C_SHARE))

        self._tree.clear()

        positions = self._svc.get_all_positions()
        portfolio_shares = self._owned_map()

        # Group by ticker (already sorted by ticker asc, date desc from service)
        grouped: dict[str, list] = {}
        for pos in positions:
            grouped.setdefault(pos.ticker, []).append(pos)

        for ticker, pos_list in sorted(grouped.items()):
            owned = portfolio_shares.get(ticker, 0)
            parent = self._make_parent_row(ticker, owned, pos_list)
            self._tree.addTopLevelItem(parent)

            for pos in pos_list:   # already date-desc from service query
                child = self._make_child_row(pos)
                parent.addChild(child)

            # Expand: always expand by default (most recent visible)
            parent.setExpanded(ticker in expanded or True)

        self._update_funds_panel()

    def _owned_map(self) -> dict[str, int]:
        """Map ticker → total open shares from portfolio."""
        try:
            positions = self._port.get_positions()
            result: dict[str, int] = {}
            for p in positions:
                if not p.sell_date:
                    result[p.ticker] = result.get(p.ticker, 0) + p.shares
            return result
        except Exception:
            return {}

    def _make_parent_row(self, ticker: str, owned: int,
                         pos_list: list) -> QTreeWidgetItem:
        item = QTreeWidgetItem()
        bold = QFont(); bold.setBold(True); bold.setPointSize(11)
        item.setFont(C_SHARE, bold)
        _left(item, C_SHARE, ticker, _BLUE)

        owned_font = QFont(); owned_font.setBold(True)
        item.setFont(C_OWNED, owned_font)
        _right(item, C_OWNED, f"{owned:,}" if owned else "—", _MUTED)

        # Summary: count open vs closed
        open_cnt   = sum(1 for p in pos_list if p.status == "Open")
        closed_cnt = len(pos_list) - open_cnt
        summary = f"{open_cnt} open"
        if closed_cnt:
            summary += f"  ·  {closed_cnt} closed"
        item.setText(C_TYPE, summary)
        item.setForeground(C_TYPE, QBrush(_MUTED))

        for col in range(_NUM_COLS):
            item.setBackground(col, QBrush(_BG_PAR))

        item.setData(0, Qt.UserRole, None)   # no position id on parent
        return item

    def _make_child_row(self, pos) -> QTreeWidgetItem:
        svc = OptionsService
        item = QTreeWidgetItem()

        # Calculated values
        total_prem = svc.calc_total_premium(pos.premium, pos.num_shares)
        net_prem   = svc.calc_net_premium(total_prem, pos.fees)
        net_share  = svc.calc_net_per_share(net_prem, pos.num_shares)
        total_val  = svc.calc_total_value(pos.strike_price, pos.num_shares)
        pl         = svc.calc_profit_loss(
            pos.status, net_prem, pos.close_premium, pos.num_shares,
            pos.close_fees or 0.0
        )

        # Colour for type
        type_color = _BLUE if pos.option_type == "Call" else _YELLOW

        # Expiry colour: red if past, yellow if within 7 days, green otherwise
        today = date.today()
        days_left = (pos.end_date - today).days
        if pos.status == "Open":
            if days_left < 0:
                expiry_col = _RED
            elif days_left <= 7:
                expiry_col = _YELLOW
            else:
                expiry_col = _TEXT
        else:
            expiry_col = _MUTED

        # Status colour
        status_col = {
            "Open":      _GREEN,
            "Expired":   _MUTED,
            "Closed":    _MUTED,
            "Exercised": _YELLOW,
        }.get(pos.status, _TEXT)

        _left(item,  C_SHARE,      "")
        _right(item, C_OWNED,      "")
        _left(item,  C_TYPE,       pos.option_type,                    type_color)
        _right(item, C_PREMIUM,    f"${pos.premium:,.4f}",             _TEXT)
        _right(item, C_STRIKE,     f"${pos.strike_price:,.2f}",        _TEXT)
        _left(item,  C_EXPIRY,     pos.end_date.strftime("%d/%m/%Y"),  expiry_col)
        _right(item, C_SHARES,     f"{pos.num_shares:,}",              _TEXT)
        _right(item, C_TOTAL_PREM, _money(total_prem),                 _TEXT)
        _right(item, C_FEES,       _money(pos.fees),                   _MUTED)
        _right(item, C_NET_PREM,   _money(net_prem),                   _TEXT)
        _right(item, C_NET_SHARE,  f"${net_share:,.4f}",               _TEXT)
        _right(item, C_CONTRACTS,  str(pos.num_contracts),             _TEXT)
        _right(item, C_TOTAL_VAL,  _money(total_val),
               _YELLOW if pos.option_type == "Put" and pos.status == "Open" else _TEXT)
        # P&L
        if pl is None:
            _right(item, C_PL, "—", _MUTED)
        elif pl >= 0:
            _right(item, C_PL, _money(pl), _GREEN)
        else:
            _right(item, C_PL, f"−${abs(pl):,.2f}", _RED)

        _left(item, C_STATUS, pos.status, status_col)
        _left(item, C_NOTES,  pos.notes or "", _MUTED)

        item.setData(0, Qt.UserRole, pos.id)
        return item

    def _ledger_balance(self) -> float:
        if self._pf is None:
            return 0.0
        try:
            return self._pf.get_ledger_balance(self._port)
        except Exception:
            return 0.0

    def _update_funds_panel(self):
        cash      = self._ledger_balance()
        locked    = self._svc.get_locked_capital()
        available = cash - locked

        self._cash_val.setText(f"${cash:,.2f}")
        self._locked_val.setText(f"${locked:,.2f}")
        self._avail_val.setText(f"${available:,.2f}")

        new_obj = "funds_avail" if available >= 0 else "funds_avail_neg"
        if self._avail_val.objectName() != new_obj:
            self._avail_val.setObjectName(new_obj)
            self._avail_val.style().unpolish(self._avail_val)
            self._avail_val.style().polish(self._avail_val)

    # --------------------------------------------------------------- actions -

    def _on_add(self):
        dlg = AddOptionDialog(self._svc, self._port, parent=self)
        if dlg.exec():
            self.refresh()

    def _on_edit(self):
        pos_id = self._selected_position_id()
        if pos_id is None:
            QMessageBox.information(self, "Edit", "Select an option row to edit.")
            return
        dlg = AddOptionDialog(self._svc, self._port, position_id=pos_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _on_delete(self):
        pos_id = self._selected_position_id()
        if pos_id is None:
            QMessageBox.information(self, "Delete", "Select an option row to delete.")
            return
        reply = QMessageBox.question(
            self, "Delete Option",
            "Permanently delete this option position?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._svc.delete_position(pos_id)
            self.refresh()

    def _selected_position_id(self) -> int | None:
        items = self._tree.selectedItems()
        if not items:
            return None
        return items[0].data(0, Qt.UserRole)
