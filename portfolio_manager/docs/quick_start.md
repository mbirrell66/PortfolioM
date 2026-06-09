# Quick Start Guide

## Getting Started with Portfolio Manager

This guide will help you quickly set up and start using Portfolio Manager.

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio_manager
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Basic Usage

### 1. Adding Your First Position
1. Click the "Add Position" button
2. Enter the following details:
   - Ticker: e.g., AAPL
   - Company Name: e.g., Apple Inc.
   - Purchase Date: Date of purchase
   - Purchase Price: Your buying price
   - Shares: Number of shares purchased
   - Notes: Optional notes about the investment

### 2. Viewing Your Portfolio
- All positions are displayed in the main table
- Current prices, gain/loss, and metrics update automatically

### 3. Refreshing Prices
- Click "Refresh Prices" to update current market values
- Gain/loss calculations will be updated automatically

### 4. Editing Positions
- Select a position in the table
- Click "Edit Position"
- Modify shares or notes (purchase price is immutable)
- Save changes

### 5. Deleting Positions
- Select a position
- Click "Delete Position"
- Confirm deletion

## Key Features

### Portfolio Analytics
- Real-time portfolio value calculation
- Gain/loss tracking
- Performance metrics
- Portfolio distribution charts

### Market Data Integration
- Yahoo Finance integration
- Real-time price updates
- Historical data access

### User Interface
- Modern dark-themed GUI
- Responsive design
- Intuitive navigation
- Detailed reporting

## Troubleshooting

### Common Issues
- **No market data**: Check internet connection
- **Database errors**: Verify file permissions
- **Application won't start**: Check Python version and dependencies

## Next Steps

1. Add several positions to see full functionality
2. Try different combinations of stocks
3. Use the dashboard to analyze performance
4. Experiment with various date ranges and metrics

For complete documentation, see the docs/ directory.