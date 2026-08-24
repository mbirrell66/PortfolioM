#!/usr/bin/env python3
"""
Debug launcher for Portfolio Manager.

Same startup as run_app.py, but verbose: it reports each step and prints a
full traceback if anything fails. Use this when the app won't start and you
need to see why. The startup sequence itself lives in portfolio_manager/main.py
so there is only ever one copy of it.
"""

import sys
import traceback
from pathlib import Path

print("Starting debug launcher...")
print("Working directory:", Path.cwd())

APP_DIR = Path(__file__).resolve().parent / "portfolio_manager"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
print("Application directory:", APP_DIR)

try:
    print("Importing entry point...")
    from main import main
    print("Entry point imported.")

    print("Launching...")
    main()

except Exception as exc:
    print(f"Launch failed: {exc}")
    traceback.print_exc()
    sys.exit(1)
