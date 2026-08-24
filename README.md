# Portfolio Manager

A desktop application for managing investment portfolios with real-time market data, personal finance tracking, options management, and a modern dark-themed GUI.

See my Web sites:

http://etfvaluer.com

http://optionsvaluer.com

## Features

### Portfolio
- Add, edit, and delete positions with full buy/sell tracking
- Record buy and sell commissions
- Closed positions history with realised P&L
- Stock split and dividend recording
- Real-time price updates via Yahoo Finance
- Position size calculator

### Options Tracking
- Track covered calls and cash-secured puts against portfolio tickers
- Expandable tree grouped by ticker, sorted by date
- Statuses: Open, Expired, Closed (bought back), Exercised
- Calculated fields: Total Premium, Net Premium, Net per Share, Capital Required, P&L
- Expiry warnings with colour coding
- Available Funds panel: Ledger Balance minus locked Put capital

### Personal Finance
- **Ledger**: unified view of all money flows — portfolio buys/sells, dividends, income, expenses, deposits, withdrawals, and option transactions. Running balance always visible.
- **Income & Expenses**: categorised tracking with date filtering
- **Financial Goals**: target amount and progress tracking
- **Budgets**: monthly spend limits per expense category

### Tax Management
- Capital gains event recording
- Tax event log with category assignment
- Tax return summaries

### Analytics & Tools
- Portfolio analytics dashboard: allocation, gain/loss, metrics
- Benchmark comparison tab
- Portfolio optimisation
- Performance tab
- News tab
- Reports

### Application
- Dark theme throughout (bg `#0F1117`, accent `#5295FF`)
- Database backup and restore (Settings tab)
- Persistent settings (theme, refresh interval, display preferences)

## Technology Stack

| Library | Purpose |
|---------|---------|
| Python 3.13 | Runtime |
| PySide6 | GUI framework |
| SQLite | Local database |
| SQLAlchemy | ORM |
| yfinance | Real-time market data |
| pandas / numpy | Analytics and calculations |
| pyqtgraph | Charts and visualisations |
| pytest | Testing |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
portfolio_manager/
├── main.py
├── config/
│   └── settings.json
├── data/
│   └── portfolio.db                  # Single SQLite file — all data
├── database/
│   ├── database.py                   # Engine, session, migrations
│   ├── models.py                     # Portfolio positions, dividends, splits
│   ├── personal_finance_models.py    # Income, expenses, goals, budgets, ledger
│   ├── tax_models.py                 # Tax events and returns
│   ├── watchlist_models.py           # Watchlist entries
│   └── options_models.py             # Options positions
├── gui/
│   ├── main_window.py
│   ├── portfolio_table.py
│   ├── dashboard_widget.py
│   ├── add_position_dialog.py
│   ├── edit_position_dialog.py
│   ├── position_size_calculator.py
│   ├── watchlist_tab.py
│   ├── add_watchlist_dialog.py
│   ├── edit_watchlist_dialog.py
│   ├── options_tab.py
│   ├── add_option_dialog.py
│   ├── personal_finance_tab.py
│   ├── tax_management_tab.py
│   ├── capital_gains_dialog.py
│   ├── tax_event_dialog.py
│   ├── benchmark_comparison_tab.py
│   ├── performance_tab.py
│   ├── portfolio_optimization_tab.py
│   ├── report_tab.py
│   ├── news_tab.py
│   ├── settings_tab.py
│   └── icons.py
└── services/
    ├── portfolio_service.py
    ├── market_data.py
    ├── portfolio_analytics.py
    ├── portfolio_optimizer.py
    ├── personal_finance_service.py
    ├── tax_service.py
    └── options_service.py
```

## Ledger — Source of Truth

All monetary transactions feed into a single running ledger:

| Source | Ledger type | Direction |
|--------|-------------|-----------|
| Portfolio buy | Buy | Debit |
| Portfolio sell | Sell | Credit |
| Dividend | Dividend | Credit |
| Income entry | Income | Credit |
| Expense entry | Expense | Debit |
| Manual deposit | Deposit | Credit |
| Manual withdrawal | Withdrawal | Debit |
| Option written | Option Premium | Credit |
| Option trading fees | Option Fees | Debit |
| Option bought back | Option Buyback | Debit |

Option ledger entries are managed automatically by the Options tab and are recreated whenever a position is saved or removed.

## Database Schema (key tables)

**positions** — portfolio holdings with buy/sell/commission fields  
**dividend_events** — per-ticker dividend records  
**stock_splits** — split history  
**ledger_transactions** — all manual and option-generated cash flows (`source_type`, `source_id` link option rows back to `options_positions`)  
**income / expenses** — personal finance entries with categories  
**financial_goals / budgets** — planning data  
**options_positions** — covered calls and puts with open/close dates and premiums  
**tax_events / capital_gains_events / tax_returns** — tax records  
**watchlist** — tracked tickers with hypothetical share counts  

## Backup & Restore

Settings → Database Management. Backup uses SQLite's native `.backup()` API to produce a portable `.db` file covering all tables.

## Testing

```bash
pytest tests/
```

## License

MIT
