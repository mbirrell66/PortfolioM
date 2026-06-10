# PHASE 2 FEATURES

These features MUST NOT be started until Milestone 8 of the core application is complete and fully tested.

Complete Phase 1 first.

Only begin Phase 2 after all existing tests pass.

---

# FEATURE: DIVIDEND REINVESTMENT PLAN (DRIP)

## GOAL

Support automatic reinvestment of dividends.

---

## DATABASE

Create table:

dividend_events

Fields:

id
ticker
ex_dividend_date
payment_date
dividend_per_share
shares_owned
cash_received
shares_purchased
reinvestment_price
created_at

---

## CALCULATIONS

Formula:

cash_received =
shares_owned × dividend_per_share

shares_purchased =
cash_received / reinvestment_price

new_share_total =
old_shares + shares_purchased

---

## REQUIREMENTS

User can:

Add dividend manually

Edit dividend

Delete dividend

Enable automatic reinvestment

Disable automatic reinvestment

---

## TESTING

Verify:

Cash calculation

Share calculation

Portfolio updates

Performance updates

---

# FEATURE: STOCK SPLITS

## GOAL

Support stock split adjustments.

---

## DATABASE

Create table:

stock_splits

Fields:

id
ticker
split_date
old_ratio
new_ratio

Example:

2-for-1

old_ratio = 1

new_ratio = 2

---

## CALCULATIONS

Example:

100 shares

2-for-1 split

Result:

200 shares

Purchase price divided by 2

Portfolio value unchanged

---

## REQUIREMENTS

Automatic detection if available.

Manual entry always available.

User can edit split history.

---

## TESTING

Verify:

2-for-1

3-for-1

3-for-2

Reverse splits

Portfolio value unchanged

---

# FEATURE: ADVANCED BENCHMARK COMPARISON

## GOAL

Allow multiple benchmark selections.

---

## DEFAULTS

SPY

QQQ

DIA

IWM

VTI

---

## CHARTS

Show:

Portfolio

Benchmark

Relative outperformance

Rolling returns

Drawdown comparison

---

## CALCULATIONS

Portfolio Return

Benchmark Return

Excess Return

Tracking Difference

Maximum Drawdown

---

# FEATURE: CUSTOM REPORTS

## GOAL

Allow user-generated reports.

---

## EXPORT TYPES

PDF

Excel

CSV

---

## REPORT SECTIONS

Portfolio Summary

Holdings

Performance

Transactions

Dividends

Benchmark Comparison

---

## REPORT BUILDER

User can:

Select sections

Select date ranges

Save templates

Generate reports

---

# FEATURE: NEWS SYSTEM

## GOAL

Display news related to holdings.

---

## DATA SOURCE

Use free RSS feeds.

Do NOT use paid APIs.

---

## REQUIREMENTS

Show:

Headline

Source

Publication Date

Ticker

URL

---

## FILTERING

Only display news for portfolio holdings.

---

## NOTIFICATIONS

Notify for:

Earnings Releases

Dividend Announcements

Stock Splits

Major News

---

# FEATURE: ECONOMIC CALENDAR

## GOAL

Display major market-moving events.

---

## EVENTS

CPI

PPI

FOMC

GDP

Employment Data

Retail Sales

Consumer Sentiment

---

## DISPLAY

Calendar View

Upcoming Events

Historical Events

---

# FEATURE: PORTFOLIO OPTIMIZATION

## GOAL

Provide allocation suggestions.

This is advisory only.

Do NOT automatically trade.

---

## USER INPUTS

Risk Tolerance

Investment Horizon

Target Allocation

---

## OUTPUTS

Current Allocation

Target Allocation

Suggested Rebalancing

Risk Score

Concentration Risk

Sector Exposure

---

## VERSION 1

Use simple rules.

Do NOT implement advanced quantitative optimization initially.

---

# FEATURE: PERSONAL FINANCE TRACKING

## GOAL

Track overall finances.

Separate from investment portfolio.

---

## MODULES

Income

Expenses

Savings

Net Worth

Debt

Cash Flow

---

## REPORTING

Monthly Summary

Savings Rate

Net Worth Trend

Budget Analysis

---

# FEATURE: TAX MANAGEMENT

## GOAL

Estimate investment tax impact.

This feature is informational only.

Do NOT provide tax advice.

---

## TRACK

Capital Gains

Realized Gains

Unrealized Gains

Dividend Income

Holding Period

---

## REPORTS

Tax Lots

Realized Gains Report

Dividend Income Report

Estimated Tax Summary

---

## REQUIREMENT

Display:

"Consult a qualified tax professional."

on all tax reports.

---

# PHASE 2 RULE

Complete one feature at a time.

For every feature:

Build

Test

Verify

Commit

Only then begin the next feature.
