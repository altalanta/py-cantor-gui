from __future__ import annotations

from typing import Tuple

from PySide6.QtGui import QColor


DEFAULT_FG_HEX = "#1b1f23"
DEFAULT_BG_HEX = "#ffffff"


def hex_to_qcolor(hex_str: str) -> QColor:
    """Convert a hex color string like '#rrggbb' or 'rrggbb' to QColor.

    Raises ValueError if invalid.
    """
    s = hex_str.strip()
    if not s:
        raise ValueError("Empty color string")
    if not s.startswith("#"):
        s = "#" + s
    color = QColor(s)
    if not color.isValid():
        raise ValueError(f"Invalid color: {hex_str}")
    return color


def qcolor_to_hex(color: QColor) -> str:
    """Convert QColor to hex string '#rrggbb'."""
    return color.name(QColor.HexRgb)


def suitable_text_color(bg: QColor) -> QColor:
    """Return black or white depending on background luminance for contrast."""
    r, g, b, _ = bg.getRgb()
    # Perceived luminance
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return QColor("black") if luminance > 186 else QColor("white")


def parse_hex_pair(fg: str | None, bg: str | None) -> Tuple[QColor, QColor]:
    fg_q = hex_to_qcolor(fg or DEFAULT_FG_HEX)
    bg_q = hex_to_qcolor(bg or DEFAULT_BG_HEX)
    return fg_q, bg_q

