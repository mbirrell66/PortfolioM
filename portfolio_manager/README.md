# Portfolio Manager

A desktop application for managing investment portfolios with real-time market data, analytics, and a modern dark-themed GUI.

## Features

- **Portfolio Management**: Add, edit, and remove positions
- **Real-time Market Data**: Integration with Yahoo Finance for current prices
- **Portfolio Analytics**: Detailed financial metrics and performance tracking
- **Interactive Charts**: Visualize portfolio performance using pyqtgraph
- **Dark-themed GUI**: Modern, responsive interface built with PySide6
- **Local Data Storage**: SQLite database for all portfolio data
- **Portfolio Value Tracking**: Real-time calculation of portfolio value, gain/loss

## Technology Stack

- **Python 3.13**
- **PySide6** - GUI framework
- **SQLite** - Local database
- **SQLAlchemy** - ORM for database operations
- **yfinance** - Market data integration
- **pandas & numpy** - Data analysis and calculations
- **pyqtgraph** - Charting and visualization
- **pytest** - Testing framework

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
portfolio_manager/
├── main.py                    # Application entry point
├── config/
│   └── settings.json         # Application configuration
├── data/
│   └── portfolio.db          # SQLite database file
├── database/
│   ├── models.py             # Database models
│   └── database.py           # Database connection and initialization
├── gui/
│   ├── main_window.py        # Main application window
│   ├── add_position_dialog.py # Dialog for adding positions
│   ├── edit_position_dialog.py # Dialog for editing positions
│   └── dashboard_widget.py   # Portfolio analytics dashboard
├── services/
│   ├── portfolio_service.py   # Portfolio management operations
│   ├── market_data_service.py # Market data integration
│   └── portfolio_analytics.py # Portfolio analytics and reporting
├── tests/
│   └── test_database.py      # Database tests
└── README.md                 # This file
```

## Key Functionality

### Portfolio Management
- Add new positions with ticker, company name, purchase date, price, and shares
- Edit existing positions (note: purchase price is immutable)
- Delete positions from the portfolio
- View all positions in a detailed table

### Market Data Integration
- Real-time price updates from Yahoo Finance
- Automatic refresh of current prices
- Display of current market values and performance metrics

### Portfolio Analytics
- Calculation of cost basis, market value, and gain/loss
- Percentage gain/loss calculations
- Portfolio summary with total value and performance metrics
- Portfolio distribution charts

### User Interface
- Dark-themed, modern GUI with PySide6
- Responsive dashboard with interactive charts
- Intuitive dialogs for adding/editing positions
- Real-time updates when data changes

## Database Schema

### Positions Table
- `id`: Primary key
- `ticker`: Stock ticker symbol
- `company_name`: Company name
- `purchase_date`: Date of purchase
- `purchase_price`: Purchase price (immutable)
- `shares`: Number of shares
- `notes`: Optional notes about the position
- `created_at`: Record creation timestamp
- `updated_at`: Record modification timestamp

## Testing

Run tests with:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License.