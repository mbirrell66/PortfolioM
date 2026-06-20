"""
Portfolio table models and views for Portfolio Manager.
Provides separate models for open (active) and closed (sold) positions.
"""

from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor
from database.models import Position
from database.database import SessionLocal
from services.portfolio_service import PortfolioService

_TABLE_SS = """
    QTableView {
        background-color: #0F1117;
        alternate-background-color: #161928;
        color: #DDE8FF;
        gridline-color: transparent;
        border: none;
        selection-background-color: rgba(74, 158, 255, 0.25);
        selection-color: #DDE8FF;
        outline: none;
    }
    QTableView::item { padding: 6px 10px; border: none; }
    QTableView::item:hover { background-color: rgba(74, 158, 255, 0.12); }
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
"""


# ---------------------------------------------------------------------------
# Open Positions Model
# ---------------------------------------------------------------------------

class PortfolioTableModel(QAbstractTableModel):
    """Table model for open (unsold) portfolio positions."""

    HEADERS = [
        "Ticker", "Company", "Shares", "Buy Date",
        "Buy Price", "Commission", "Cost Basis", "Dollar Cost Avg",
        "Current Price", "Market Value", "Unrealised G/L", "G/L %",
    ]

    def __init__(self):
        super().__init__()
        self.positions = []
        self.portfolio_service = PortfolioService()
        self._price_cache = {}
        self._dca_cache = {}

    # -- data loading -------------------------------------------------------
    def load_data(self):
        db = SessionLocal()
        try:
            self.positions = (
                db.query(Position)
                .filter(Position.sell_date.is_(None))
                .all()
            )
        finally:
            db.close()
        self._price_cache = {}
        self._dca_cache = {}
        self.layoutChanged.emit()

    def refresh_data(self):
        self.load_data()

    def _prices(self):
        if not self._price_cache:
            for pos in self.positions:
                self._price_cache[pos.ticker] = (
                    self.portfolio_service.get_current_price(pos.ticker)
                )
        return self._price_cache

    def _dca(self):
        """Weighted-average cost per share (incl. buy commission) per ticker.

        Aggregates every open lot of a ticker, so when additional shares of an
        already-held stock are bought, this reflects the blended cost. Display
        only -- it does not alter stored positions or any other calculation.
        """
        if not self._dca_cache:
            agg = {}
            for pos in self.positions:
                cost, shares = agg.get(pos.ticker, (0.0, 0))
                cost += pos.purchase_price * pos.shares + (pos.buy_commission or 0.0)
                shares += pos.shares
                agg[pos.ticker] = (cost, shares)
            self._dca_cache = {
                ticker: (cost / shares if shares else 0.0)
                for ticker, (cost, shares) in agg.items()
            }
        return self._dca_cache

    # -- Qt overrides -------------------------------------------------------
    def rowCount(self, parent=QModelIndex()):
        return len(self.positions)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.positions):
            return None

        pos = self.positions[index.row()]
        col = index.column()
        prices = self._prices()
        cur_price = prices.get(pos.ticker, 0.0)
        buy_comm = pos.buy_commission or 0.0
        cost_basis = pos.purchase_price * pos.shares + buy_comm
        dca = self._dca().get(pos.ticker, 0.0)
        market_val = cur_price * pos.shares
        gl = market_val - cost_basis
        gl_pct = (gl / cost_basis * 100) if cost_basis else 0.0

        if role == Qt.DisplayRole:
            if col == 0:  return pos.ticker
            if col == 1:  return pos.company_name or ""
            if col == 2:  return str(pos.shares)
            if col == 3:  return pos.purchase_date.strftime("%Y-%m-%d") if pos.purchase_date else ""
            if col == 4:  return f"${pos.purchase_price:.2f}"
            if col == 5:  return f"${buy_comm:.2f}"
            if col == 6:  return f"${cost_basis:.2f}"
            if col == 7:  return f"${dca:.2f}"
            if col == 8:  return f"${cur_price:.2f}" if cur_price else "N/A"
            if col == 9:  return f"${market_val:.2f}" if cur_price else "N/A"
            if col == 10: return f"${gl:.2f}" if cur_price else "N/A"
            if col == 11: return f"{gl_pct:.2f}%" if cur_price else "N/A"

        elif role == Qt.ForegroundRole:
            if col in (10, 11) and cur_price:
                return QColor("#38D88A") if gl >= 0 else QColor("#FF5068")

        elif role == Qt.TextAlignmentRole:
            if col in (2, 4, 5, 6, 7, 8, 9, 10, 11):
                return int(Qt.AlignRight | Qt.AlignVCenter)

        return None


# ---------------------------------------------------------------------------
# Closed Positions Model
# ---------------------------------------------------------------------------

class ClosedPositionsTableModel(QAbstractTableModel):
    """Table model for closed (sold) positions."""

    HEADERS = [
        "Ticker", "Company", "Shares",
        "Buy Date", "Buy Price", "Buy Comm",
        "Sell Date", "Sell Price", "Sell Comm",
        "Cost Basis", "Proceeds", "Realised P&L", "Realised %",
    ]

    def __init__(self):
        super().__init__()
        self.positions = []

    def load_data(self):
        db = SessionLocal()
        try:
            self.positions = (
                db.query(Position)
                .filter(Position.sell_date.isnot(None))
                .all()
            )
        finally:
            db.close()
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return len(self.positions)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.positions):
            return None

        pos = self.positions[index.row()]
        col = index.column()
        buy_comm  = pos.buy_commission or 0.0
        sell_comm = pos.sell_commission or 0.0
        cost_basis = pos.purchase_price * pos.shares + buy_comm
        proceeds   = (pos.sell_price or 0.0) * pos.shares - sell_comm
        pnl        = proceeds - cost_basis
        pnl_pct    = (pnl / cost_basis * 100) if cost_basis else 0.0

        if role == Qt.DisplayRole:
            if col == 0:  return pos.ticker
            if col == 1:  return pos.company_name or ""
            if col == 2:  return str(pos.shares)
            if col == 3:  return pos.purchase_date.strftime("%Y-%m-%d") if pos.purchase_date else ""
            if col == 4:  return f"${pos.purchase_price:.2f}"
            if col == 5:  return f"${buy_comm:.2f}"
            if col == 6:  return pos.sell_date.strftime("%Y-%m-%d") if pos.sell_date else ""
            if col == 7:  return f"${pos.sell_price:.2f}" if pos.sell_price else ""
            if col == 8:  return f"${sell_comm:.2f}"
            if col == 9:  return f"${cost_basis:.2f}"
            if col == 10: return f"${proceeds:.2f}"
            if col == 11: return f"${pnl:.2f}"
            if col == 12: return f"{pnl_pct:.2f}%"

        elif role == Qt.ForegroundRole:
            if col in (11, 12):
                return QColor("#38D88A") if pnl >= 0 else QColor("#FF5068")

        elif role == Qt.TextAlignmentRole:
            if col in (2, 4, 5, 7, 8, 9, 10, 11, 12):
                return int(Qt.AlignRight | Qt.AlignVCenter)

        return None


# ---------------------------------------------------------------------------
# Shared view factory
# ---------------------------------------------------------------------------

def _make_table_view(model) -> QTableView:
    view = QTableView()
    view.setModel(model)
    view.setSortingEnabled(True)
    view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    view.horizontalHeader().setStretchLastSection(True)
    view.verticalHeader().setVisible(False)
    view.setSelectionBehavior(QTableView.SelectRows)
    view.setAlternatingRowColors(True)
    view.setShowGrid(False)
    view.setStyleSheet(_TABLE_SS)
    return view


class PortfolioTableView(QTableView):
    """View for open positions."""

    def __init__(self):
        super().__init__()
        self._model = PortfolioTableModel()
        self.setModel(self._model)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setStyleSheet(_TABLE_SS)
        self.load_data()

    def load_data(self):
        self._model.load_data()

    def get_selected_position_id(self):
        rows = self.selectionModel().selectedRows()
        if rows:
            return self._model.positions[rows[0].row()].id
        return None


class ClosedPositionsTableView(QTableView):
    """View for closed (sold) positions."""

    def __init__(self):
        super().__init__()
        self._model = ClosedPositionsTableModel()
        self.setModel(self._model)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setStyleSheet(_TABLE_SS)
        self.load_data()

    def load_data(self):
        self._model.load_data()

    def get_selected_position_id(self):
        rows = self.selectionModel().selectedRows()
        if rows:
            return self._model.positions[rows[0].row()].id
        return None
