cd D:\Projects\PortfolioM\portfolio_manager
pyinstaller --onefile --windowed --name PortfolioManager ^
  --add-data "gui;gui" ^
  --add-data "database;database" ^
  --add-data "services;services" ^
  --add-data "utils;utils" ^
  --hidden-import "yfinance" ^
  --hidden-import "pyqtgraph" ^
  --hidden-import "sqlalchemy" ^
  --hidden-import "pandas" ^
  --hidden-import "numpy" ^
  --hidden-import "dateutil" ^
  --hidden-import "dateutil.parser ^
  --hidden-import "feedparser" ^
  main.py
