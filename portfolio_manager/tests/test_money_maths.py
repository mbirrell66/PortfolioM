"""Partial sells, options P&L, locked capital and the ledger balance."""
from datetime import date, datetime

import pytest


@pytest.fixture
def portfolio(session_factory):
    from services.portfolio_service import PortfolioService
    return PortfolioService()


@pytest.fixture
def options(session_factory):
    from services.options_service import OptionsService
    return OptionsService()


@pytest.fixture
def finance(session_factory):
    from services.personal_finance_service import PersonalFinanceService
    return PersonalFinanceService()


def buy(portfolio, shares=100, price=10.0, commission=20.0):
    return portfolio.add_position("ABC", "ABC Ltd", date(2025, 1, 2), price, shares,
                                  buy_commission=commission)


# ---- partial sells --------------------------------------------------------

def test_partial_sell_splits_shares_and_commission(portfolio):
    pos = buy(portfolio)
    assert portfolio.partial_close_position(pos.id, 40, date(2025, 6, 1), 15.0, 9.95)

    (open_pos,) = portfolio.get_open_positions()
    (closed,) = portfolio.get_closed_positions()
    assert (open_pos.shares, open_pos.buy_commission) == (60, 12.0)
    assert (closed.shares, closed.buy_commission) == (40, 8.0)
    assert (closed.sell_price, closed.sell_commission) == (15.0, 9.95)
    assert closed.purchase_date == date(2025, 1, 2)   # keeps the original buy date
    # nothing created or lost in the split
    assert open_pos.shares + closed.shares == 100
    assert open_pos.buy_commission + closed.buy_commission == pytest.approx(20.0)


def test_commission_split_still_adds_up_when_it_does_not_divide_evenly(portfolio):
    pos = buy(portfolio, shares=3, commission=10.0)
    portfolio.partial_close_position(pos.id, 1, date(2025, 6, 1), 15.0)
    (open_pos,) = portfolio.get_open_positions()
    (closed,) = portfolio.get_closed_positions()
    assert open_pos.buy_commission + closed.buy_commission == pytest.approx(10.0)


def test_selling_everything_closes_the_position_in_place(portfolio):
    pos = buy(portfolio)
    portfolio.partial_close_position(pos.id, 100, date(2025, 6, 1), 15.0, 9.95)
    assert portfolio.get_open_positions() == []
    (closed,) = portfolio.get_closed_positions()
    assert (closed.id, closed.shares, closed.buy_commission) == (pos.id, 100, 20.0)


@pytest.mark.parametrize("shares", [0, -5, 101])
def test_invalid_sell_quantity_is_rejected_and_changes_nothing(portfolio, shares):
    pos = buy(portfolio)
    with pytest.raises(ValueError):
        portfolio.partial_close_position(pos.id, shares, date(2025, 6, 1), 15.0)
    (open_pos,) = portfolio.get_open_positions()
    assert open_pos.shares == 100
    assert portfolio.get_closed_positions() == []


def test_unknown_position_returns_false(portfolio):
    assert portfolio.partial_close_position(999, 1, date(2025, 6, 1), 15.0) is False


def test_position_metrics(portfolio):
    pos = buy(portfolio)
    m = portfolio.calculate_position_metrics(pos, 12.5)
    assert (m["cost_basis"], m["market_value"], m["gain_loss"]) == (1000, 1250, 250)
    assert m["gain_percent"] == pytest.approx(25.0)


# ---- options --------------------------------------------------------------

def test_option_premium_maths():
    from services.options_service import OptionsService as O
    total = O.calc_total_premium(1.50, 100)
    net = O.calc_net_premium(total, 10.0)
    assert (total, net) == (150.0, 140.0)
    assert O.calc_net_per_share(net, 100) == pytest.approx(1.40)
    assert O.calc_net_per_share(net, 0) == 0.0
    assert O.calc_total_value(50.0, 100) == 5000.0


@pytest.mark.parametrize("status, close_premium, close_fees, expected", [
    ("Open", None, 0.0, None),          # not realised yet
    ("Expired", None, 0.0, 140.0),      # keep the lot
    ("Closed", 0.50, 5.0, 85.0),        # 140 - (0.50 x 100 + 5)
    ("Closed", 2.00, 5.0, -65.0),       # bought back at a loss
    ("Exercised", None, 0.0, 140.0),
])
def test_option_profit_loss(status, close_premium, close_fees, expected):
    from services.options_service import OptionsService as O
    assert O.calc_profit_loss(status, 140.0, close_premium, 100, close_fees) == expected


def test_only_open_puts_lock_capital(options):
    end = date(2026, 1, 16)
    options.add_position("ABC", "Put", 1.0, 50.0, end, 1, 100)                    # locks 5,000
    options.add_position("XYZ", "Put", 1.0, 20.0, end, 2, 200)                    # locks 4,000
    options.add_position("ABC", "Call", 1.0, 60.0, end, 1, 100)                   # calls lock nothing
    options.add_position("ABC", "Put", 1.0, 80.0, end, 1, 100, status="Expired")  # finished
    assert options.get_locked_capital() == 9000.0
    assert options.get_available_funds(10000.0) == 1000.0


# ---- ledger ---------------------------------------------------------------

def deposit(session_factory, amount, kind="Deposit"):
    from database.personal_finance_models import LedgerTransaction
    db = session_factory()
    db.add(LedgerTransaction(date=datetime(2025, 1, 1), transaction_type=kind, amount=amount))
    db.commit()
    db.close()


def test_empty_ledger_is_zero(finance, portfolio):
    assert finance.get_ledger_balance(portfolio) == 0.0


def test_ledger_balance_across_every_money_flow(session_factory, finance, portfolio, options):
    deposit(session_factory, 10000.0)
    deposit(session_factory, 500.0, "Withdrawal")

    pos = buy(portfolio)                                                   # -1,020.00
    portfolio.partial_close_position(pos.id, 40, date(2025, 6, 1), 15.0, 9.95)  # +590.05

    cat_in = finance.create_income_category("Wages")
    cat_out = finance.create_expense_category("Feed")
    finance.create_income(300.0, cat_in.id)
    finance.create_expense(120.0, cat_out.id)

    # sold put: +150 premium, -10 fees; bought back: -(0.50 x 100) - 5 fees
    options.add_position("ABC", "Put", 1.50, 50.0, date(2026, 1, 16), 1, 100,
                         fees=10.0, status="Closed", close_premium=0.50, close_fees=5.0)

    expected = 10000 - 500 - 1020 + 590.05 + 300 - 120 + 150 - 10 - 50 - 5
    assert finance.get_ledger_balance(portfolio) == pytest.approx(expected)
