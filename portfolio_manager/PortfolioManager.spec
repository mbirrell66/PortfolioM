# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Portfolio Manager
# Run from the portfolio_manager/ directory:
#   pyinstaller PortfolioManager.spec

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('PortM.png', '.')],
    hiddenimports=[
        # PySide6 core
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtCore',
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'PySide6.QtPrintSupport',
        # pyqtgraph (charts)
        'pyqtgraph',
        'pyqtgraph.graphicsItems',
        'pyqtgraph.graphicsItems.BarGraphItem',
        'pyqtgraph.graphicsItems.PlotCurveItem',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.pool',
        # Data libraries
        'pandas',
        'numpy',
        'yfinance',
        # Optional (news tab) - guarded by try/except in the code
        'feedparser',
        'requests',
        # App modules - bare names because portfolio_manager/ is in pathex
        'database.models',
        'database.tax_models',
        'database.personal_finance_models',
        'database.database',
        'services.portfolio_service',
        'services.personal_finance_service',
        'services.tax_service',
        'services.market_data',
        'services.portfolio_analytics',
        'services.portfolio_optimizer',
        'gui.main_window',
        'gui.icons',
        'gui.tax_management_tab',
        'gui.tax_event_dialog',
        'gui.capital_gains_dialog',
        'gui.performance_tab',
        'gui.dashboard_widget',
        'gui.report_tab',
        'gui.settings_tab',
        'gui.benchmark_comparison_tab',
        'gui.portfolio_optimization_tab',
        'gui.personal_finance_tab',
        'gui.add_position_dialog',
        'gui.edit_position_dialog',
        'gui.dividend_dialog',
        'gui.stock_split_dialog',
        'gui.news_tab',
        'gui.portfolio_table',
        'gui.watchlist_tab',
        'gui.add_watchlist_dialog',
        'gui.edit_watchlist_dialog',
        'database.watchlist_models',
        'services.watchlist_service',
        'config.config_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'pytest',
        'black',
        'flake8',
        'mypy',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PortfolioManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    icon='PortM.png',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PortfolioManager',
)
