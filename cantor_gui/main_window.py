from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSplitter, QWidget

from .canvas import Canvas
from .controller import Controller
from .panels import ControlsPanel
from .utils.colors import DEFAULT_BG_HEX, DEFAULT_FG_HEX, hex_to_qcolor


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cantor GUI")
        self.resize(1100, 720)

        self.canvas = Canvas(self)
        self.panels = ControlsPanel(self)
        self.controller = Controller(self.canvas, self.panels, self.statusBar())

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.panels)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self._build_menu()
        self._wire_shortcuts()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        export_png = QAction("Export &PNG…", self)
        export_png.setShortcut(QKeySequence.StandardKey.Save)
        export_png.triggered.connect(self.controller.export_png)
        export_svg = QAction("Export &SVG…", self)
        export_svg.setShortcut(QKeySequence("Ctrl+Shift+S"))
        export_svg.triggered.connect(self.controller.export_svg)
        quit_act = QAction("&Quit", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(export_png)
        file_menu.addAction(export_svg)
        file_menu.addSeparator()
        file_menu.addAction(quit_act)

        view_menu = self.menuBar().addMenu("&View")
        reset_zoom = QAction("Reset &Zoom", self)
        reset_zoom.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom.triggered.connect(self.canvas.reset_view)
        view_menu.addAction(reset_zoom)

        help_menu = self.menuBar().addMenu("&Help")
        about = QAction("&About", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _wire_shortcuts(self) -> None:
        reset_params = QAction("Reset Params", self)
        reset_params.setShortcut(QKeySequence("Ctrl+N"))
        reset_params.triggered.connect(self._reset_defaults)
        self.addAction(reset_params)

        toggle_anim = QAction("Toggle Animation", self)
        toggle_anim.setShortcut(QKeySequence(Qt.Key.Key_Space))
        toggle_anim.triggered.connect(lambda: self.panels.play_btn.toggle())
        self.addAction(toggle_anim)

    def _reset_defaults(self) -> None:
        # Reset panel widgets to default values
        self.panels.mode_combo.setCurrentText("Line")
        self.panels.depth_spin.setValue(6)
        self.panels.thickness_spin.setValue(4.0)
        self.panels.fg = hex_to_qcolor(DEFAULT_FG_HEX)
        self.panels.bg = hex_to_qcolor(DEFAULT_BG_HEX)
        self.panels._update_color_buttons()
        self.panels.show_all.setChecked(False)
        self.panels.spacing_spin.setValue(10)
        self.panels.loop_chk.setChecked(False)
        self.panels.speed_spin.setValue(200)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Cantor GUI",
            """<b>Cantor GUI</b><br>
            Visualize the Cantor set (line and dust).<br>
            PySide6 / Qt 6.<br><br>
            Shortcuts:<br>
            Ctrl+N reset, Space toggle animation, Ctrl+0 reset zoom, Ctrl+S PNG, Ctrl+Shift+S SVG.
            """,
        )

