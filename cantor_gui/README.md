# Cantor GUI

[![CI](https://github.com/yourname/cantor-gui/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/cantor-gui/actions/workflows/ci.yml)

Interactive visualization of the Cantor set using PySide6 / Qt 6. Supports the classic 1D line construction and the 2D Cantor dust, with live controls, zoom, pan, animation, and export to PNG/SVG.

Screenshots: placeholders – they will appear here in a future update.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run

```bash
python -m cantor_gui
# or
cantor-gui
```

CLI flags:

```bash
python -m cantor_gui --mode {line,dust} --depth 6 --bg #ffffff --fg #1b1f23 --show-all-levels
```

## Controls

- Mode: Line or Dust
- Depth: 0–12 (line), 0–9 recommended (dust)
- Thickness: line thickness or point size
- Colors: foreground/background
- Line mode: Show all levels + spacing
- Animation: Play/Pause, Loop, Speed (ms per level)
- Export: PNG or SVG (select size; aspect maintained)

## Shortcuts

- Ctrl+N: Reset parameters to defaults
- Space+Drag or Middle-Drag: Pan
- Mouse Wheel: Zoom (centered on cursor)
- Ctrl+0: Reset zoom
- Ctrl+S: Export PNG
- Ctrl+Shift+S: Export SVG
- Space: Toggle animation

## Notes on Performance

- Line mode is fast up to depth 12.
- Dust mode creates 4^n points; practical up to 8–9 on typical laptops.
- Rendering uses batched QPainterPath items to keep the UI responsive.

## Testing

Unit tests cover the pure math functions only (no Qt required to run them). CI runs on Python 3.10–3.12 and checks formatting with ruff/black.

## License

MIT
