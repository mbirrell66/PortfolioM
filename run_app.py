#!/usr/bin/env python3
"""
Portfolio Manager - convenience launcher.

The real entry point is portfolio_manager/main.py. This wrapper exists only so
that `python run_app.py` works from the repository root; it deliberately does
not duplicate the startup sequence, so the stylesheet, window icon, splash
screen and service wiring stay defined in exactly one place.
"""

import sys
from pathlib import Path

# portfolio_manager/ must be on sys.path before importing main, because the
# application uses top-level imports (`from gui.main_window import ...`).
APP_DIR = Path(__file__).resolve().parent / "portfolio_manager"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from main import main  # noqa: E402  - requires APP_DIR on sys.path first

if __name__ == "__main__":
    main()
