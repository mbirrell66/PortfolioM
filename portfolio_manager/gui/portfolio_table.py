"""
Portfolio table model and view for Portfolio Manager
"""

from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor, QFont
from database.models import Position
from database.database import SessionLocal
from services.portfolio_service import PortfolioService
from datetime import datetime

class PortfolioTableModel(QAbstractTableModel):
    """Table model for portfolio positions."""
    
    def __init__(self):
        """Initialize table model."""
        super().__init__()
        self.positions = []
        self.headers = [
            "Ticker", "Shares", "Purchase Price", "Current Price", "Cost Basis",
            "Market Value", "Gain/Loss", "Gain %", "Purchase Date"
        ]
        self.portfolio_service = PortfolioService()
        self._current_prices = {}  # Cache for current prices
    
    def load_data(self):
        """Load positions from database."""
        db = SessionLocal()
        try:
            self.positions = db.query(Position).all()
        finally:
            db.close()
        self.layoutChanged.emit()
    
    def refresh_data(self):
        """Refresh data in the model."""
        self._current_prices = {}  # Clear cache
        self.load_data()
    
    def _get_current_prices(self):
        """Get current prices for all positions efficiently."""
        if not self._current_prices:
            # Get all unique tickers
            tickers = [position.ticker for position in self.positions]
            # Remove duplicates
            unique_tickers = list(set(tickers))
            
            # Fetch all current prices at once
            self._current_prices = {}
            for ticker in unique_tickers:
                self._current_prices[ticker] = self.portfolio_service.get_current_price(ticker)
        
        return self._current_prices
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self.positions)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for a specific cell."""
        if not index.isValid() or index.row() >= len(self.positions):
            return None
        
        position = self.positions[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:  # Ticker
                return position.ticker
            elif index.column() == 1:  # Shares
                return str(position.shares)
            elif index.column() == 2:  # Purchase Price
                return f"${position.purchase_price:.2f}"
            elif index.column() == 3:  # Current Price
                # Get current price for this position
                current_prices = self._get_current_prices()
                current_price = current_prices.get(position.ticker, 0)
                return f"${current_price:.2f}" if current_price > 0 else "N/A"
            elif index.column() == 4:  # Cost Basis
                cost_basis = position.purchase_price * position.shares
                return f"${cost_basis:.2f}"
            elif index.column() == 5:  # Market Value
                current_prices = self._get_current_prices()
                current_price = current_prices.get(position.ticker, 0)
                market_value = current_price * position.shares
                return f"${market_value:.2f}" if current_price > 0 else "N/A"
            elif index.column() == 6:  # Gain/Loss
                current_prices = self._get_current_prices()
                current_price = current_prices.get(position.ticker, 0)
                if current_price > 0:
                    cost_basis = position.purchase_price * position.shares
                    market_value = current_price * position.shares
                    gain_loss = market_value - cost_basis
                    return f"${gain_loss:.2f}"
                else:
                    return "N/A"
            elif index.column() == 7:  # Gain %
                current_prices = self._get_current_prices()
                current_price = current_prices.get(position.ticker, 0)
                if current_price > 0:
                    cost_basis = position.purchase_price * position.shares
                    market_value = current_price * position.shares
                    gain_loss = market_value - cost_basis
                    gain_percent = (gain_loss / cost_basis) * 100 if cost_basis != 0 else 0
                    return f"{gain_percent:.2f}%"
                else:
                    return "N/A"
            elif index.column() == 8:  # Purchase Date
                return position.purchase_date.strftime("%Y-%m-%d")

        elif role == Qt.ForegroundRole:
            if index.column() in (6, 7):  # Gain/Loss and Gain %
                current_prices = self._get_current_prices()
                current_price = current_prices.get(position.ticker, 0)
                if current_price > 0:
                    gain_loss = (current_price - position.purchase_price) * position.shares
                    return QColor("#38D88A") if gain_loss >= 0 else QColor("#FF5068")

        elif role == Qt.TextAlignmentRole:
            if index.column() in (1, 2, 3, 4, 5, 6, 7):
                return int(Qt.AlignRight | Qt.AlignVCenter)

        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None
    
    def flags(self, index):
        """Return item flags."""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class PortfolioTableView(QTableView):
    """Table view for portfolio positions."""
    
    def __init__(self):
        """Initialize table view."""
        super().__init__()
        self.setModel(PortfolioTableModel())
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setStyleSheet("""
            QTableView {
                background-color: #0F1117;
                alternate-background-color: #161928;
                color: #DDE8FF;
                gridline-color: transparent;
                border: none;
                border-radius: 8px;
                selection-background-color: rgba(74, 158, 255, 0.25);
                selection-color: #DDE8FF;
                outline: none;
            }
            QTableView::item {
                padding: 6px 10px;
                border: none;
            }
            QTableView::item:hover {
                background-color: rgba(74, 158, 255, 0.12);
            }
            QHeaderView::section {
                background-color: #191D2E;
                color: #7488B8;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 600;
                border: none;
                border-right: 1px solid #222844;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

        # Load initial data
        self.load_data()
    
    def load_data(self):
        """Load data into the table."""
        model = self.model()
        if isinstance(model, PortfolioTableModel):
            model.load_data()
    
    def get_selected_position_id(self):
        """Get the ID of the selected position."""
        selection = self.selectedIndexes()
        if selection:
            row = selection[0].row()
            model = self.model()
            if isinstance(model, PortfolioTableModel):
                return model.positions[row].id
        return None