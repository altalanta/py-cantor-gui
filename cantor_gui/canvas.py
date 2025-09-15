from __future__ import annotations

from typing import List

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QMouseEvent, QWheelEvent, QPainter
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsScene, QGraphicsView


class Canvas(QGraphicsView):
    """Interactive canvas with zoom and pan.

    - Mouse wheel zoom centered on cursor
    - Middle-drag or space+drag to pan
    - Ctrl+0 to reset zoom
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHints(
            self.renderHints()
            | QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._panning = False
        self._last_mouse_pos = QPoint()
        self._space_pressed = False
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

    def set_scene_items(self, path_items: List[QGraphicsPathItem], bg: QColor) -> None:
        self._scene.clear()
        self._scene.setBackgroundBrush(bg)
        for item in path_items:
            self._scene.addItem(item)
        self.fit_to_scene()

    def fit_to_scene(self) -> None:
        rect = self._scene.itemsBoundingRect()
        if rect.isNull():
            return
        self.setSceneRect(rect)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def reset_view(self) -> None:
        self.resetTransform()
        self.fit_to_scene()

    # Interaction
    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if self._scene is None:
            return
        angle = event.angleDelta().y()
        if angle == 0:
            return
        factor = 1.0015 ** angle
        pos = event.position()
        scene_pos_before = self.mapToScene(QPoint(int(pos.x()), int(pos.y())))
        self.scale(factor, factor)
        scene_pos_after = self.mapToScene(QPoint(int(pos.x()), int(pos.y())))
        delta = scene_pos_after - scene_pos_before
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and self._space_pressed
        ):
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._panning:
            delta: QPoint = event.position().toPoint() - self._last_mouse_pos
            self._last_mouse_pos = event.position().toPoint()
            self.translate(delta.x(), delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            if self._panning:
                self._panning = False
                self.setCursor(Qt.CursorShape.ArrowCursor)
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            self._space_pressed = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_0:
            self.reset_view()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            self._space_pressed = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().keyReleaseEvent(event)
