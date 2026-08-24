"""Single source of truth for the application version.

Everything that reports a version reads it from here:
  - main.py            -> QApplication.setApplicationVersion()
  - __init__.py        -> portfolio_manager.__version__
  - setup.py           -> package metadata (parsed, not imported)
  - build_clean.ps1    -> installer filename and Inno Setup /DAppVersion

Bump this one string to cut a release.
"""

__version__ = "1.3.0"
