"""Monotone SVG icon library for Portfolio Manager.

All icons are 24×24 stroke-based paths rendered in #BECCE8 (light slate),
which reads cleanly on the dark #0F1117 background.
"""
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray

_C = "#BECCE8"  # icon stroke colour

_SVGS: dict[str, str] = {
    # ── Tab icons ────────────────────────────────────────────────────────────
    "PORTFOLIO": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="2" y="7" width="20" height="14" rx="2"/>'
        f'<path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'
        f'</svg>'
    ),
    "DASHBOARD": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="3" y="3" width="7" height="7" rx="1"/>'
        f'<rect x="14" y="3" width="7" height="7" rx="1"/>'
        f'<rect x="3" y="14" width="7" height="7" rx="1"/>'
        f'<rect x="14" y="14" width="7" height="7" rx="1"/>'
        f'</svg>'
    ),
    "PERFORMANCE": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        f'<polyline points="16 7 22 7 22 13"/>'
        f'</svg>'
    ),
    "BENCHMARK": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="2" y="12" width="5" height="8" rx="1"/>'
        f'<rect x="9.5" y="7" width="5" height="13" rx="1"/>'
        f'<rect x="17" y="4" width="5" height="16" rx="1"/>'
        f'<line x1="2" y1="22" x2="22" y2="22"/>'
        f'</svg>'
    ),
    "REPORTS": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        f'<polyline points="14 2 14 8 20 8"/>'
        f'<line x1="8" y1="12" x2="16" y2="12"/>'
        f'<line x1="8" y1="16" x2="16" y2="16"/>'
        f'</svg>'
    ),
    "NEWS": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="4" y="2" width="16" height="20" rx="2"/>'
        f'<line x1="8" y1="7" x2="16" y2="7"/>'
        f'<line x1="8" y1="11" x2="16" y2="11"/>'
        f'<line x1="8" y1="15" x2="13" y2="15"/>'
        f'</svg>'
    ),
    "FINANCE": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="12" cy="12" r="10"/>'
        f'<line x1="12" y1="6" x2="12" y2="18"/>'
        f'<path d="M15 9H10.5a2.5 2.5 0 0 0 0 5h3a2.5 2.5 0 0 1 0 5H9"/>'
        f'</svg>'
    ),
    "TAX": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1z"/>'
        f'<line x1="8" y1="10" x2="16" y2="10"/>'
        f'<line x1="8" y1="14" x2="14" y2="14"/>'
        f'</svg>'
    ),
    "SETTINGS": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="12" cy="12" r="3"/>'
        f'<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83'
        f' 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21'
        f' a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06'
        f' a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15'
        f' a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9'
        f' a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06'
        f' A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09'
        f' a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0'
        f' 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21'
        f' a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
        f'</svg>'
    ),

    # ── Toolbar / action icons ────────────────────────────────────────────────
    "ACT_ADD": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="12" cy="12" r="10"/>'
        f'<line x1="12" y1="8" x2="12" y2="16"/>'
        f'<line x1="8" y1="12" x2="16" y2="12"/>'
        f'</svg>'
    ),
    "ACT_DIVIDEND": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<line x1="12" y1="1" x2="12" y2="23"/>'
        f'<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
        f'</svg>'
    ),
    "ACT_SPLIT": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="6" cy="6" r="3"/>'
        f'<circle cx="6" cy="18" r="3"/>'
        f'<line x1="20" y1="4" x2="8.12" y2="15.88"/>'
        f'<line x1="14.47" y1="14.48" x2="20" y2="20"/>'
        f'<line x1="8.12" y1="8.12" x2="12" y2="12"/>'
        f'</svg>'
    ),
    "ACT_EDIT": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>'
        f'<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>'
        f'</svg>'
    ),
    "ACT_DELETE": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="3 6 5 6 21 6"/>'
        f'<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'
        f'<line x1="10" y1="11" x2="10" y2="17"/>'
        f'<line x1="14" y1="11" x2="14" y2="17"/>'
        f'</svg>'
    ),
    "ACT_REFRESH": (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{_C}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="23 4 23 10 17 10"/>'
        f'<polyline points="1 20 1 14 7 14"/>'
        f'<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'
        f'</svg>'
    ),
}


def get_icon(name: str) -> QIcon:
    """Return a QIcon for *name*; returns an empty QIcon if unknown or if Qt
    SVG support is unavailable."""
    svg = _SVGS.get(name, "")
    if not svg:
        return QIcon()
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(svg.encode()), "SVG")
    if pixmap.isNull():
        return QIcon()
    return QIcon(pixmap)
