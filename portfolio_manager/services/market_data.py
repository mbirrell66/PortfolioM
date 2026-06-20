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

    def get_price_history(self, ticker: str, years: int) -> Optional[Dict]:
        """Return start/end closing prices and CAGR over *years* of history.

        Keys in returned dict:
            start_price  - closing price approximately *years* ago
            end_price    - most recent closing price
            actual_years - actual span in fractional years
            cagr         - compound annual growth rate (e.g. 0.12 = 12 %)
        Returns None if data is unavailable or the span is too short.
        """
        try:
            period_map = {1: "1y", 2: "2y", 3: "5y", 5: "5y", 10: "10y"}
            period_str = period_map.get(years, str(years) + "y")
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period_str)
            if hist is None or len(hist) < 2:
                return None

            start_price = float(hist["Close"].iloc[0])
            end_price   = float(hist["Close"].iloc[-1])

            start_dt = hist.index[0].to_pydatetime()
            end_dt   = hist.index[-1].to_pydatetime()
            actual_years = (end_dt - start_dt).days / 365.25

            if actual_years <= 0 or start_price <= 0:
                return None

            cagr = (end_price / start_price) ** (1.0 / actual_years) - 1.0

            return {
                "start_price":  start_price,
                "end_price":    end_price,
                "actual_years": actual_years,
                "cagr":         cagr,
            }
        except Exception as e:
            logger.error(f"Error fetching price history for {ticker}: {e}")
            return None

    def get_sp500_data(self) -> Optional[Dict]:
        """Get S&P 500 ETF data (SPY)."""
        return self.get_stock_data("SPY")
