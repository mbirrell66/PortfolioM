"""Price cache and batching. The network call is replaced with a counter."""
import pytest

import services.market_data as md


@pytest.fixture
def svc(monkeypatch):
    md.clear_cache()
    calls = []

    def fake_fetch(self, ticker):
        calls.append(ticker)
        if ticker == "BAD":
            return None
        return {"ticker": ticker, "current_price": 10.0 + len(calls)}

    monkeypatch.setattr(md.MarketDataService, "_fetch_one", fake_fetch)
    service = md.MarketDataService()
    service.calls = calls
    yield service
    md.clear_cache()


def test_each_ticker_is_fetched_once_and_duplicates_collapse(svc):
    data = svc.get_multiple_stocks_data(["AAA", "BBB", "AAA", "CCC"])
    assert sorted(data) == ["AAA", "BBB", "CCC"]
    assert sorted(svc.calls) == ["AAA", "BBB", "CCC"]


def test_second_request_comes_from_the_cache(svc):
    first = svc.get_stock_data("AAA")
    again = svc.get_stock_data("AAA")
    assert again == first
    assert svc.calls == ["AAA"]


def test_cache_is_shared_between_service_instances(svc):
    svc.get_stock_data("AAA")
    assert md.MarketDataService().get_stock_data("AAA") is not None
    assert svc.calls == ["AAA"]


def test_only_uncached_tickers_are_fetched(svc):
    svc.get_stock_data("AAA")
    svc.get_multiple_stocks_data(["AAA", "BBB"])
    assert svc.calls == ["AAA", "BBB"]


def test_refresh_ignores_the_cache(svc):
    old = svc.get_stock_data("AAA")["current_price"]
    new = svc.refresh(["AAA"])["AAA"]["current_price"]
    assert svc.calls == ["AAA", "AAA"]
    assert new != old
    assert svc.get_stock_data("AAA")["current_price"] == new   # cache now holds the fresh one


def test_cached_price_expires(svc, monkeypatch):
    svc.get_stock_data("AAA")
    real = md.time.monotonic()
    monkeypatch.setattr(md.time, "monotonic", lambda: real + md.CACHE_SECONDS + 1)
    svc.get_stock_data("AAA")
    assert svc.calls == ["AAA", "AAA"]


def test_failed_ticker_is_left_out_and_not_hammered(svc):
    assert svc.get_multiple_stocks_data(["AAA", "BAD"]).keys() == {"AAA"}
    assert svc.get_stock_data("BAD") is None
    assert svc.calls.count("BAD") == 1   # second ask did not hit the network again


def test_empty_and_blank_tickers(svc):
    assert svc.get_multiple_stocks_data([]) == {}
    assert svc.get_multiple_stocks_data(["", None]) == {}
    assert svc.calls == []


def test_portfolio_totals_use_one_fetch_per_ticker(session_factory, svc):
    from datetime import date
    from services.portfolio_service import PortfolioService
    p = PortfolioService()
    p.add_position("AAA", "A", date(2025, 1, 2), 5.0, 10)
    p.add_position("AAA", "A", date(2025, 2, 2), 6.0, 10)
    p.add_position("BBB", "B", date(2025, 1, 2), 5.0, 10)
    value = p.get_portfolio_value()
    p.get_total_gain_loss()
    p.get_total_gain_loss_percent()
    assert sorted(svc.calls) == ["AAA", "BBB"]
    assert value > 0
