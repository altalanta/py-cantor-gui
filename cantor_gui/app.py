from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .utils.colors import hex_to_qcolor


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cantor GUI - visualize the Cantor set")
    parser.add_argument("--mode", choices=["line", "dust"], default="line")
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--bg", type=str, default=None, help="Background color hex, e.g. #ffffff")
    parser.add_argument("--fg", type=str, default=None, help="Foreground color hex, e.g. #1b1f23")
    parser.add_argument("--show-all-levels", action="store_true", help="Line mode: show all levels")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    if args.depth < 0:
        print("Error: depth must be >= 0", file=sys.stderr)
        return 2
    try:
        fg = hex_to_qcolor(args.fg) if args.fg else None
        bg = hex_to_qcolor(args.bg) if args.bg else None
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv[:1])
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    win = MainWindow()
    # Apply CLI options onto the UI
    win.panels.mode_combo.setCurrentText("Line" if args.mode == "line" else "Dust")
    win.panels.depth_spin.setValue(int(args.depth))
    if fg is not None:
        win.panels.fg = fg
    if bg is not None:
        win.panels.bg = bg
    win.panels._update_color_buttons()
    win.panels.show_all.setChecked(bool(args.show_all_levels))

    win.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

