# Portfolio Manager Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Guide](#user-guide)
5. [API Documentation](#api-documentation)
6. [Database Schema](#database-schema)
7. [Troubleshooting](#troubleshooting)

## Introduction

Portfolio Manager is a desktop application designed to help investors track and manage their investment portfolios. With real-time market data integration, comprehensive analytics, and an intuitive user interface, it provides a complete solution for portfolio management.

## Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager

### Installation Steps
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Getting Started

1. **Launch the Application**: Run `python main.py`
2. **Add Your First Position**: Click "Add Position" to enter your investment details
3. **View Portfolio**: See all your positions in the main table
4. **Refresh Prices**: Click "Refresh Prices" to update current market values
5. **Analyze Performance**: Check the dashboard for portfolio analytics

## User Guide

### Main Interface
The main window displays:
- Portfolio table with all positions
- Dashboard with analytics and charts
- Navigation controls

### Adding Positions
1. Click "Add Position" button
2. Fill in:
   - Ticker symbol (e.g., AAPL)
   - Company name
   - Purchase date
   - Purchase price (immutable)
   - Number of shares
   - Optional notes

### Editing Positions
1. Select a position in the table
2. Click "Edit Position"
3. Modify editable fields (shares, notes)
4. Note: Purchase price cannot be changed (historical record)

### Refreshing Prices
1. Click "Refresh Prices" button
2. Current market prices will update automatically
3. Gain/loss calculations will be recalculated

### Dashboard
The dashboard shows:
- Portfolio summary (total value, gain/loss)
- Performance tables with actual data
- Portfolio distribution charts

## API Documentation

### PortfolioService
The core service for portfolio management operations.

#### Methods:
- `add_position()`: Add a new position to the portfolio
- `get_positions()`: Retrieve all positions
- `get_position()`: Get a specific position by ID
- `update_position()`: Update existing position
- `delete_position()`: Remove a position
- `get_current_prices()`: Get current prices for all positions
- `get_current_price()`: Get current price for a ticker
- `calculate_position_metrics()`: Calculate financial metrics for a position

### MarketDataService
Handles market data integration with Yahoo Finance.

#### Methods:
- `get_stock_data()`: Get data for a single stock
- `get_multiple_stocks_data()`: Get data for multiple stocks

## Database Schema

### Positions Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| ticker | String | Stock ticker symbol |
| company_name | String | Company name |
| purchase_date | Date | Date of purchase |
| purchase_price | Float | Purchase price (immutable) |
| shares | Integer | Number of shares |
| notes | Text | Optional notes |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record modification timestamp |

## Troubleshooting

### Common Issues

**Issue**: Application fails to start
- **Solution**: Ensure all dependencies are installed (`pip install -r requirements.txt`)

**Issue**: Market data not loading
- **Solution**: Check internet connection and ensure yfinance is working

**Issue**: Database connection errors
- **Solution**: Verify database file permissions and location

**Issue**: Prices not updating
- **Solution**: Try refreshing prices manually or check network connectivity

### Reporting Issues

If you encounter issues:
1. Check the application logs
2. Verify your internet connection
3. Report bugs to the issue tracker