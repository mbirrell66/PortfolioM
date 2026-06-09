# Portfolio Manager API Documentation

## Overview

This documentation provides detailed information about the Portfolio Manager's API structure and available methods.

## Modules

### 1. database.models

#### Position Model
Represents a single investment position in the portfolio.

**Fields:**
- `id`: Primary key (Integer)
- `ticker`: Stock ticker symbol (String)
- `company_name`: Company name (String)
- `purchase_date`: Date of purchase (Date)
- `purchase_price`: Purchase price (Float)
- `shares`: Number of shares (Integer)
- `notes`: Optional notes (Text)
- `created_at`: Record creation timestamp (DateTime)
- `updated_at`: Record modification timestamp (DateTime)

### 2. services.portfolio_service

#### PortfolioService Class

**Methods:**

##### `__init__(self)`
Initialize the portfolio service with market data service.

##### `add_position(self, ticker: str, company_name: str, purchase_date: date, purchase_price: float, shares: int, notes: str = "") -> Position`
Add a new position to the portfolio.

**Parameters:**
- `ticker`: Stock ticker symbol
- `company_name`: Company name
- `purchase_date`: Date of purchase
- `purchase_price`: Purchase price
- `shares`: Number of shares
- `notes`: Optional notes

**Returns:** Position object

##### `get_positions(self) -> List[Position]`
Get all positions from the portfolio.

**Returns:** List of Position objects

##### `get_position(self, position_id: int) -> Optional[Position]`
Get a specific position by ID.

**Parameters:**
- `position_id`: The ID of the position to retrieve

**Returns:** Position object or None

##### `update_position(self, position_id: int, **kwargs) -> Optional[Position]`
Update a position with new data.

**Parameters:**
- `position_id`: The ID of the position to update
- `**kwargs`: Fields to update

**Returns:** Updated Position object or None

##### `delete_position(self, position_id: int) -> bool`
Delete a position from the portfolio.

**Parameters:**
- `position_id`: The ID of the position to delete

**Returns:** True if successful, False otherwise

##### `get_current_prices(self, positions: List[Position]) -> Dict[str, Dict]`
Get current prices for all positions.

**Parameters:**
- `positions`: List of Position objects

**Returns:** Dictionary mapping tickers to price data

##### `get_current_price(self, ticker: str) -> float`
Get current price for a single ticker.

**Parameters:**
- `ticker`: Stock ticker symbol

**Returns:** Current price as float

##### `calculate_position_metrics(self, position: Position, current_price: float) -> Dict`
Calculate financial metrics for a position.

**Parameters:**
- `position`: Position object
- `current_price`: Current market price

**Returns:** Dictionary with cost_basis, market_value, gain_loss, and gain_percent

### 3. services.market_data_service

#### MarketDataService Class

**Methods:**

##### `get_stock_data(self, ticker: str) -> Dict`
Get data for a single stock from Yahoo Finance.

**Parameters:**
- `ticker`: Stock ticker symbol

**Returns:** Dictionary with stock data including current_price

##### `get_multiple_stocks_data(self, tickers: List[str]) -> Dict[str, Dict]`
Get data for multiple stocks.

**Parameters:**
- `tickers`: List of stock ticker symbols

**Returns:** Dictionary mapping tickers to their data

### 4. gui.main_window

#### MainWindow Class

**Methods:**
- `__init__(self)`: Initialize main window
- `setup_ui(self)`: Create user interface
- `setup_connections(self)`: Connect signals and slots
- `load_positions(self)`: Load and display positions
- `add_position(self)`: Show add position dialog
- `edit_position(self)`: Show edit position dialog
- `delete_position(self)`: Delete selected position
- `refresh_prices(self)`: Refresh current prices
- `show_dashboard(self)`: Show dashboard widget

### 5. gui.edit_position_dialog

#### EditPositionDialog Class

**Methods:**
- `__init__(self, position_id, parent=None)`: Initialize dialog
- `create_ui(self)`: Create UI elements
- `create_layout(self)`: Create layout
- `populate_fields(self)`: Populate dialog with existing data
- `validate_input(self)`: Validate user input
- `get_position_data(self)`: Get position data from dialog
- `accept(self)`: Handle dialog acceptance

### 6. gui.add_position_dialog

#### AddPositionDialog Class

**Methods:**
- `__init__(self, parent=None)`: Initialize dialog
- `create_ui(self)`: Create UI elements
- `create_layout(self)`: Create layout
- `validate_input(self)`: Validate user input
- `get_position_data(self)`: Get position data from dialog
- `accept(self)`: Handle dialog acceptance

### 7. services.portfolio_analytics

#### PortfolioAnalytics Class

**Methods:**
- `format_currency(self, value: float) -> str`: Format currency value
- `format_percentage(self, value: float) -> str`: Format percentage value
- `calculate_portfolio_summary(self, positions: List[Position]) -> Dict`: Calculate portfolio summary
- `get_portfolio_distribution(self, positions: List[Position]) -> Dict`: Get portfolio distribution data

## Error Handling

All methods follow consistent error handling patterns:
- Database operations use proper transaction handling
- Market data operations handle connection errors gracefully
- Input validation prevents invalid data
- Exceptions are properly propagated to calling code