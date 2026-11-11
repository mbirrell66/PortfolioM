"""
Market data service for fetching stock prices and financial data.

Prices are cached for a short time and shared by every MarketDataService in
the process, so the many tabs that ask for the same ticker cause one network
call instead of one each. Several tickers are fetched at the same time.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date
from typing import Dict, List, Optional

import yfinance as yf

logger = logging.getLogger(__name__)

CACHE_SECONDS = 120          # how long a fetched price is reused
FAILED_CACHE_SECONDS = 30    # how long before a ticker that returned nothing is retried
MAX_WORKERS = 8              # tickers fetched at once

_lock = threading.Lock()
_cache: Dict[str, tuple] = {}   # ticker -> (time fetched, data dict or None)
_names: Dict[str, str] = {}     # ticker -> company name, kept for the session


def clear_cache() -> None:
    """Forget every cached price."""
    with _lock:
        _cache.clear()


class MarketDataService:
    """Service for fetching market data from Yahoo Finance."""

    def __init__(self):
        """Initialize market data service."""
        pass

    # ------------------------------------------------------------- fetching

    def _fetch_one(self, ticker: str) -> Optional[Dict]:
        """One network request for one ticker. Never raises."""
        try:
            hist = yf.Ticker(ticker).history(period="5d")
            if hist is not None and not hist.empty:
                hist = hist.dropna(subset=["Close"])
            if hist is None or hist.empty:
                logger.warning("No price data for %s", ticker)
                return None

            latest = hist.iloc[-1]
            return {
                'ticker': ticker,
                'current_price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': latest['Volume'],
                'company_name': _names.get(ticker, ticker),
                'last_updated': datetime.now()
            }
        except Exception as e:
            logger.error("Error fetching data for %s: %s", ticker, e)
            return None

    def get_multiple_stocks_data(self, tickers: List[str], force: bool = False) -> Dict[str, Dict]:
        """Fetch data for several tickers. Tickers with no data are left out.

        Cached prices are reused unless *force* is True. Anything not cached
        is fetched concurrently.
        """
        wanted = list(dict.fromkeys(t for t in tickers if t))
        result: Dict[str, Dict] = {}
        missing: List[str] = []

        now = time.monotonic()
        with _lock:
            for ticker in wanted:
                hit = _cache.get(ticker)
                if hit and not force:
                    fetched_at, data = hit
                    max_age = CACHE_SECONDS if data else FAILED_CACHE_SECONDS
                    if now - fetched_at < max_age:
                        if data:
                            result[ticker] = data
                        continue
                missing.append(ticker)

        if missing:
            if len(missing) == 1:
                fetched = [self._fetch_one(missing[0])]
            else:
                with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(missing))) as pool:
                    fetched = list(pool.map(self._fetch_one, missing))
            stamp = time.monotonic()
            with _lock:
                for ticker, data in zip(missing, fetched):
                    _cache[ticker] = (stamp, data)
                    if data:
                        result[ticker] = data
        return result

    def get_stock_data(self, ticker: str, force: bool = False) -> Optional[Dict]:
        """Fetch current stock data for a ticker (None if unavailable)."""
        return self.get_multiple_stocks_data([ticker], force=force).get(ticker)

    def refresh(self, tickers: List[str]) -> Dict[str, Dict]:
        """Fetch fresh prices now, ignoring the cache. Safe to call from a worker thread."""
        return self.get_multiple_stocks_data(tickers, force=True)

    def get_company_name(self, ticker: str) -> str:
        """Company long name. Slow the first time (separate Yahoo request), then remembered."""
        with _lock:
            if ticker in _names:
                return _names[ticker]
        try:
            name = yf.Ticker(ticker).info.get('longName') or ticker
        except Exception as e:
            logger.warning("Could not get company name for %s: %s", ticker, e)
            return ticker
        with _lock:
            _names[ticker] = name
        return name

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
