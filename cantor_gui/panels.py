from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QColorDialog,
)

from .utils.colors import DEFAULT_BG_HEX, DEFAULT_FG_HEX, hex_to_qcolor, qcolor_to_hex, suitable_text_color


class ControlsPanel(QWidget):
    # Signals for controller
    modeChanged = Signal(str)
    depthChanged = Signal(int)
    thicknessChanged = Signal(float)
    fgColorChanged = Signal(QColor)
    bgColorChanged = Signal(QColor)
    showAllLevelsChanged = Signal(bool)
    spacingChanged = Signal(int)
    playPauseToggled = Signal(bool)
    loopChanged = Signal(bool)
    speedChanged = Signal(int)
    exportPngRequested = Signal()
    exportSvgRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Mode
        mode_box = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Line", "Dust"])
        self.mode_combo.currentTextChanged.connect(self._on_mode)
        mode_layout.addWidget(self.mode_combo)
        mode_box.setLayout(mode_layout)
        layout.addWidget(mode_box)

        # Depth
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_slider.setRange(0, 12)
        self.depth_slider.setValue(6)
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 12)
        self.depth_spin.setValue(6)
        self.depth_slider.valueChanged.connect(self.depth_spin.setValue)
        self.depth_spin.valueChanged.connect(self.depth_slider.setValue)
        self.depth_spin.valueChanged.connect(self._on_depth)

        depth_box = QGroupBox("Depth")
        depth_form = QFormLayout()
        depth_form.addRow(self.depth_slider, self.depth_spin)
        depth_box.setLayout(depth_form)
        layout.addWidget(depth_box)

        # Thickness
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 40)
        self.thickness_slider.setValue(4)
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(1.0, 100.0)
        self.thickness_spin.setDecimals(1)
        self.thickness_spin.setSingleStep(0.5)
        self.thickness_spin.setValue(4.0)
        self.thickness_slider.valueChanged.connect(
            lambda v: self.thickness_spin.setValue(float(v))
        )
        self.thickness_spin.valueChanged.connect(
            lambda v: self.thickness_slider.setValue(int(round(v)))
        )
        self.thickness_spin.valueChanged.connect(self._on_thickness)

        thick_box = QGroupBox("Thickness / Point Size")
        thick_form = QFormLayout()
        thick_form.addRow(self.thickness_slider, self.thickness_spin)
        thick_box.setLayout(thick_form)
        layout.addWidget(thick_box)

        # Colors
        self.fg = hex_to_qcolor(DEFAULT_FG_HEX)
        self.bg = hex_to_qcolor(DEFAULT_BG_HEX)
        color_box = QGroupBox("Colors")
        color_layout = QHBoxLayout()
        self.fg_btn = QPushButton("Foreground")
        self.fg_btn.clicked.connect(self._pick_fg)
        self.bg_btn = QPushButton("Background")
        self.bg_btn.clicked.connect(self._pick_bg)
        self._update_color_buttons()
        color_layout.addWidget(self.fg_btn)
        color_layout.addWidget(self.bg_btn)
        color_box.setLayout(color_layout)
        layout.addWidget(color_box)

        # Line layout options
        line_box = QGroupBox("Line Layout")
        line_layout = QFormLayout()
        self.show_all = QCheckBox("Show all levels")
        self.show_all.stateChanged.connect(lambda s: self.showAllLevelsChanged.emit(s == Qt.CheckState.Checked))
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 80)
        self.spacing_spin.setValue(10)
        self.spacing_spin.valueChanged.connect(self.spacingChanged)
        line_layout.addRow(self.show_all)
        line_layout.addRow(QLabel("Spacing (px)"), self.spacing_spin)
        line_box.setLayout(line_layout)
        layout.addWidget(line_box)

        # Animation
        anim_box = QGroupBox("Animation")
        anim_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.setCheckable(True)
        self.play_btn.toggled.connect(self._on_play_pause)
        self.loop_chk = QCheckBox("Loop")
        self.loop_chk.stateChanged.connect(lambda s: self.loopChanged.emit(s == Qt.CheckState.Checked))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(50, 2000)
        self.speed_spin.setValue(200)
        self.speed_spin.setSuffix(" ms")
        self.speed_spin.valueChanged.connect(self.speedChanged)
        anim_layout.addWidget(self.play_btn)
        anim_layout.addWidget(self.loop_chk)
        anim_layout.addWidget(QLabel("Speed:"))
        anim_layout.addWidget(self.speed_spin)
        anim_box.setLayout(anim_layout)
        layout.addWidget(anim_box)

        # Export
        export_box = QGroupBox("Export")
        export_layout = QHBoxLayout()
        self.export_png_btn = QPushButton("Export PNG…")
        self.export_png_btn.clicked.connect(self.exportPngRequested)
        self.export_svg_btn = QPushButton("Export SVG…")
        self.export_svg_btn.clicked.connect(self.exportSvgRequested)
        export_layout.addWidget(self.export_png_btn)
        export_layout.addWidget(self.export_svg_btn)
        export_box.setLayout(export_layout)
        layout.addWidget(export_box)

        layout.addStretch(1)

    # Handlers
    def _on_mode(self, text: str) -> None:
        self.modeChanged.emit(text)

    def _on_depth(self, value: int) -> None:
        self.depthChanged.emit(int(value))

    def _on_thickness(self, value: float) -> None:
        self.thicknessChanged.emit(float(value))

    def _update_color_buttons(self) -> None:
        def style_for(color: QColor) -> str:
            text = suitable_text_color(color)
            return (
                f"background-color: {qcolor_to_hex(color)};"
                f"color: {qcolor_to_hex(text)};"
            )

        self.fg_btn.setStyleSheet(style_for(self.fg))
        self.bg_btn.setStyleSheet(style_for(self.bg))

    def _pick_fg(self) -> None:
        color = QColorDialog.getColor(self.fg, self, "Select Foreground Color")
        if color.isValid():
            self.fg = color
            self._update_color_buttons()
            self.fgColorChanged.emit(self.fg)

    def _pick_bg(self) -> None:
        color = QColorDialog.getColor(self.bg, self, "Select Background Color")
        if color.isValid():
            self.bg = color
            self._update_color_buttons()
            self.bgColorChanged.emit(self.bg)

    def _on_play_pause(self, playing: bool) -> None:
        self.play_btn.setText("Pause" if playing else "Play")
        self.playPauseToggled.emit(playing)

