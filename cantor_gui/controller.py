from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import List, Tuple

from PySide6.QtCore import QRectF, QTimer
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QFileDialog, QGraphicsPathItem, QInputDialog

from .renderers.cantor_dust import cantor_dust_points, points_to_rects_path
from .renderers.cantor_line import (
    Segment,
    cantor_line_levels,
    cantor_line_segments,
    segments_to_path,
)


logger = logging.getLogger(__name__)


@dataclass
class Params:
    mode: str = "Line"  # or "Dust"
    depth: int = 6
    thickness: float = 4.0
    fg: QColor = QColor("#1b1f23")
    bg: QColor = QColor("#ffffff")
    show_all_levels: bool = False
    spacing: int = 10
    loop: bool = False
    speed_ms: int = 200


class Controller:
    """Mediator binding the controls and the canvas, managing rendering and export."""

    def __init__(self, canvas, panels, statusbar) -> None:
        self.canvas = canvas
        self.panels = panels
        self.statusbar = statusbar
        self.params = Params()

        # Rebuild debounce timer
        self._rebuild_timer = QTimer()
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self._rebuild_scene)

        # Animation
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._anim_step)
        self._anim_level = 0
        self._anim_start_time = 0.0
        self._frames = 0

        self._connect_signals()
        self._rebuild_scene()

    # Wiring
    def _connect_signals(self) -> None:
        p = self.panels
        p.modeChanged.connect(self._on_mode)
        p.depthChanged.connect(self._on_depth)
        p.thicknessChanged.connect(self._on_thickness)
        p.fgColorChanged.connect(self._on_fg)
        p.bgColorChanged.connect(self._on_bg)
        p.showAllLevelsChanged.connect(self._on_show_all)
        p.spacingChanged.connect(self._on_spacing)
        p.playPauseToggled.connect(self._on_play_pause)
        p.loopChanged.connect(self._on_loop)
        p.speedChanged.connect(self._on_speed)
        p.exportPngRequested.connect(self.export_png)
        p.exportSvgRequested.connect(self.export_svg)

    # Panel handlers
    def _request_rebuild(self) -> None:
        self._rebuild_timer.start(60)

    def _on_mode(self, mode: str) -> None:
        self.params.mode = mode
        self._request_rebuild()

    def _on_depth(self, depth: int) -> None:
        self.params.depth = int(depth)
        self._request_rebuild()

    def _on_thickness(self, value: float) -> None:
        self.params.thickness = float(value)
        self._request_rebuild()

    def _on_fg(self, color: QColor) -> None:
        self.params.fg = color
        self._request_rebuild()

    def _on_bg(self, color: QColor) -> None:
        self.params.bg = color
        self._request_rebuild()

    def _on_show_all(self, show: bool) -> None:
        self.params.show_all_levels = bool(show)
        self._request_rebuild()

    def _on_spacing(self, spacing: int) -> None:
        self.params.spacing = int(spacing)
        self._request_rebuild()

    def _on_speed(self, ms: int) -> None:
        self.params.speed_ms = int(ms)
        if self._anim_timer.isActive():
            self._anim_timer.start(self.params.speed_ms)

    def _on_loop(self, loop: bool) -> None:
        self.params.loop = bool(loop)

    # Animation
    def _on_play_pause(self, playing: bool) -> None:
        if playing:
            self._start_anim()
        else:
            self._stop_anim()

    def _start_anim(self) -> None:
        self._anim_level = 0
        self._frames = 0
        self._anim_start_time = time.monotonic()
        self._anim_timer.start(self.params.speed_ms)

    def _stop_anim(self) -> None:
        self._anim_timer.stop()
        self._update_status(extra="")

    def _anim_step(self) -> None:
        max_depth = self.params.depth
        level = self._anim_level
        self._render_at_level(level)
        self._anim_level += 1
        self._frames += 1
        if self._anim_level > max_depth:
            if self.params.loop:
                self._anim_level = 0
            else:
                self._stop_anim()
        # FPS update
        elapsed = max(time.monotonic() - self._anim_start_time, 1e-6)
        fps = self._frames / elapsed
        self._update_status(extra=f" | FPS: {fps:.1f}")

    # Rendering
    def _rebuild_scene(self) -> None:
        if self._anim_timer.isActive():
            # defer rebuild during animation; current frame controls rebuild
            return
        self._render_at_level(self.params.depth)

    def _render_at_level(self, level: int) -> None:
        p = self.params
        width = 1000.0
        path_items: List[QGraphicsPathItem] = []
        if p.mode == "Line":
            if p.show_all_levels:
                levels = cantor_line_levels(level)
                # Compute vertical layout: each level is a row with spacing
                total_h = len(levels) * (p.thickness + p.spacing) + p.spacing
                y = p.spacing + p.thickness / 2.0
                for segs in levels:
                    path = segments_to_path(segs, 0.0, width, y, p.thickness)
                    item = QGraphicsPathItem(path)
                    pen = QPen(p.fg)
                    pen.setWidthF(p.thickness)
                    item.setPen(pen)
                    path_items.append(item)
                    y += p.thickness + p.spacing
                self.canvas.setSceneRect(0.0, 0.0, width, max(total_h, 1.0))
            else:
                segs = cantor_line_segments(level)
                height = max(p.thickness + 2 * p.spacing, 1.0)
                y = height / 2.0
                path = segments_to_path(segs, 0.0, width, y, p.thickness)
                item = QGraphicsPathItem(path)
                pen = QPen(p.fg)
                pen.setWidthF(p.thickness)
                item.setPen(pen)
                path_items.append(item)
                self.canvas.setSceneRect(0.0, 0.0, width, height)
            count = 2 ** level
        else:  # Dust
            size = max(p.thickness, 1.0)
            height = width  # square
            pts = cantor_dust_points(level)
            path = points_to_rects_path(pts, 0.0, width, 0.0, height, size)
            item = QGraphicsPathItem(path)
            item.setBrush(p.fg)
            item.setPen(QColor(Qt.GlobalColor.transparent))
            path_items.append(item)
            self.canvas.setSceneRect(0.0, 0.0, width, height)
            count = 4 ** level

        self.canvas.set_scene_items(path_items, p.bg)
        self._update_status(count=count, depth=level)

    # Status bar
    def _update_status(self, count: int | None = None, depth: int | None = None, extra: str = "") -> None:
        if count is None:
            if self.params.mode == "Line":
                count = 2 ** self.params.depth
            else:
                count = 4 ** self.params.depth
        if depth is None:
            depth = self.params.depth
        self.statusbar.showMessage(f"Depth: {depth} | Items: {count}{extra}")

    # Export
    def export_png(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            None, "Export PNG", "cantor.png", "PNG Images (*.png)"
        )
        if not filename:
            return
        scene_rect = self.canvas.scene().itemsBoundingRect()
        # Ask for width, maintain aspect ratio
        default_w = int(max(scene_rect.width(), 1.0))
        width, ok = QInputDialog.getInt(None, "Image Width", "Width (px):", default_w, 64, 10000, 1)
        if not ok:
            return
        aspect = scene_rect.height() / max(scene_rect.width(), 1.0)
        height = int(max(round(width * aspect), 1))
        img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(self.params.bg)
        painter = QPainter(img)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            # Transform to map scene to image
            scale_x = width / scene_rect.width() if scene_rect.width() else 1.0
            scale_y = height / scene_rect.height() if scene_rect.height() else 1.0
            painter.translate(-scene_rect.left(), -scene_rect.top())
            painter.scale(scale_x, scale_y)
            self.canvas.scene().render(painter)
        finally:
            painter.end()
        img.save(filename)
        logger.info("Exported PNG to %s", filename)

    def export_svg(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            None, "Export SVG", "cantor.svg", "SVG (*.svg)"
        )
        if not filename:
            return
        scene_rect = self.canvas.scene().itemsBoundingRect()
        # Ask width, maintain aspect ratio
        default_w = int(max(scene_rect.width(), 1.0))
        width, ok = QInputDialog.getInt(None, "SVG Width", "Width (px):", default_w, 64, 20000, 1)
        if not ok:
            return
        aspect = scene_rect.height() / max(scene_rect.width(), 1.0)
        height = int(max(round(width * aspect), 1))
        gen = QSvgGenerator()
        gen.setFileName(filename)
        gen.setSize(QRectF(0, 0, width, height).size().toSize())
        gen.setViewBox(QRectF(0, 0, scene_rect.width(), scene_rect.height()).toRect())
        gen.setTitle("Cantor Set")
        gen.setDescription("Generated by Cantor GUI")
        painter = QPainter(gen)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            # Background
            painter.fillRect(0, 0, scene_rect.width(), scene_rect.height(), self.params.bg)
            self.canvas.scene().render(painter)
        finally:
            painter.end()
        logger.info("Exported SVG to %s", filename)
