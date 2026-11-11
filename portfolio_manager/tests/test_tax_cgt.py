"""Capital gains: holding-period test, loss netting, discount."""
from datetime import date
from types import SimpleNamespace

import pytest

from portfolio_manager.services.tax_service import (
    calculate_net_capital_gain, held_over_12_months,
)


def ev(acquired, disposed, cost, proceeds, exempt=False):
    return SimpleNamespace(acquisition_date=acquired, disposal_date=disposed,
                           acquisition_cost=cost, proceeds=proceeds, is_exempt=exempt)


LONG = (date(2024, 1, 10), date(2025, 6, 1))    # held well over 12 months
SHORT = (date(2025, 1, 10), date(2025, 6, 1))   # held under 5 months


# ---- holding period -------------------------------------------------------

@pytest.mark.parametrize("acquired, disposed, expected", [
    (date(2025, 1, 1), date(2025, 12, 31), False),
    (date(2025, 1, 1), date(2026, 1, 1), False),   # exactly a year: one day short
    (date(2025, 1, 1), date(2026, 1, 2), True),
    (date(2024, 2, 29), date(2025, 2, 28), False),  # leap-day purchase
    (date(2024, 2, 29), date(2025, 3, 1), True),
    (date(2025, 6, 1), date(2025, 6, 1), False),    # same-day trade
])
def test_holding_period(acquired, disposed, expected):
    assert held_over_12_months(acquired, disposed) is expected


# ---- netting --------------------------------------------------------------

def test_short_term_gain_gets_no_discount():
    r = calculate_net_capital_gain([ev(*SHORT, 5000, 6000)])
    assert r["cgt_discount"] == 0
    assert r["net_capital_gain"] == 1000


def test_long_term_gain_is_halved():
    r = calculate_net_capital_gain([ev(*LONG, 5000, 6000)])
    assert r["cgt_discount"] == 500
    assert r["net_capital_gain"] == 500


def test_losses_come_off_before_the_discount():
    # 10,000 long-term gain, 4,000 loss -> (10,000 - 4,000) x 50% = 3,000.
    # Discounting first would wrongly give 5,000 - 4,000 = 1,000.
    r = calculate_net_capital_gain([ev(*LONG, 20000, 30000), ev(*SHORT, 9000, 5000)])
    assert r["losses_applied"] == 4000
    assert r["net_capital_gain"] == 3000


def test_losses_hit_non_discount_gains_first():
    # short gain 2,000 + long gain 10,000, loss 3,000:
    # loss wipes the 2,000, then 1,000 off the long gain -> 9,000 x 50% = 4,500
    r = calculate_net_capital_gain([
        ev(*SHORT, 1000, 3000), ev(*LONG, 10000, 20000), ev(*SHORT, 8000, 5000),
    ])
    assert r["net_capital_gain"] == 4500
    assert r["losses_carried_forward"] == 0


def test_excess_losses_carry_forward_and_net_gain_is_never_negative():
    r = calculate_net_capital_gain([ev(*LONG, 1000, 2000), ev(*SHORT, 9000, 4000)])
    assert r["net_capital_gain"] == 0
    assert r["losses_carried_forward"] == 4000


def test_prior_year_losses_are_used_after_current_losses():
    r = calculate_net_capital_gain([ev(*LONG, 0, 10000)], prior_year_losses=2000)
    assert r["net_capital_gain"] == 4000


def test_exempt_events_are_ignored_both_ways():
    r = calculate_net_capital_gain([
        ev(*LONG, 1000, 9000, exempt=True), ev(*SHORT, 9000, 1000, exempt=True),
    ])
    assert r["total_capital_gains"] == 0
    assert r["capital_losses"] == 0
    assert r["net_capital_gain"] == 0


def test_nothing_recorded():
    assert calculate_net_capital_gain([])["net_capital_gain"] == 0


# ---- service + database ---------------------------------------------------

def test_event_records_discount_flag_and_no_invented_tax(tax_service):
    short = tax_service.create_capital_gains_event("shares", *SHORT, 5000, 6000)
    long_ = tax_service.create_capital_gains_event("shares", *LONG, 5000, 6000)
    loss = tax_service.create_capital_gains_event("shares", *LONG, 6000, 5000)
    assert (short.capital_gain, short.tax_rate, short.tax_liability) == (1000, 0, 0)
    assert (long_.capital_gain, long_.tax_rate, long_.tax_liability) == (1000, 50, 0)
    assert (loss.capital_gain, loss.tax_rate) == (-1000, 0)


def test_disposal_before_acquisition_is_rejected(tax_service):
    with pytest.raises(ValueError):
        tax_service.create_capital_gains_event(
            "shares", date(2025, 6, 1), date(2025, 5, 1), 100, 200)
    assert tax_service.get_capital_gains_events() == []


def test_summary_nets_only_events_in_the_date_range(tax_service):
    fy_start, fy_end = date(2025, 7, 1), date(2026, 6, 30)
    tax_service.create_capital_gains_event("shares", date(2023, 1, 1), date(2025, 8, 1), 20000, 30000)
    tax_service.create_capital_gains_event("shares", date(2025, 7, 5), date(2025, 9, 1), 9000, 5000)
    # previous financial year - must not be counted
    tax_service.create_capital_gains_event("shares", date(2023, 1, 1), date(2025, 6, 30), 0, 50000)

    s = tax_service.calculate_tax_summary(fy_start, fy_end)
    assert s["capital_gains_count"] == 2
    assert s["net_capital_gain"] == 3000
    assert "total_capital_gains_tax" not in s
