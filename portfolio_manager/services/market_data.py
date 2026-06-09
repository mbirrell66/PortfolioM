"""
Market data service for Portfolio Manager
"""

import yfinance as yf
from datetime import datetime, date
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for fetching market data from Yahoo Finance."""
    
    def __init__(self):
        """Initialize market data service."""
        pass
    
    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """Fetch current stock data for a ticker."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current price data
            hist = stock.history(period="1d")
            
            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return None
            
            current_data = hist.iloc[-1]
            
            return {
                'ticker': ticker,
                'current_price': current_data['Close'],
                'open': current_data['Open'],
                'high': current_data['High'],
                'low': current_data['Low'],
                'volume': current_data['Volume'],
                'company_name': info.get('longName', ticker),
                'last_updated': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_multiple_stocks_data(self, tickers: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple stocks."""
        data = {}
        for ticker in tickers:
            stock_data = self.get_stock_data(ticker)
            if stock_data:
                data[ticker] = stock_data
        return data
    
    def get_sp500_data(self) -> Optional[Dict]:
        """Get S&P 500 ETF data (SPY)."""
        return self.get_stock_data("SPY")