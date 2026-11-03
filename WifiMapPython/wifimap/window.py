from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QImage, QKeySequence, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .heatmap import signal_to_rgba
from .model import MATERIAL_ATTENUATION, MapModel


class _CalculationSignals(QObject):
    finished = Signal(int, object)
    failed = Signal(int, str)


class _CalculationTask(QRunnable):
    def __init__(self, generation: int, snapshot: dict) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.generation = generation
        self.snapshot = snapshot
        self.signals = _CalculationSignals()

    def run(self) -> None:
        try:
            signal = MapModel.from_dict(self.snapshot).signal
            self.signals.finished.emit(self.generation, signal)
        except Exception as error:
            self.signals.failed.emit(self.generation, str(error))


class MapCanvas(QWidget):
    point_clicked = Signal(int, int, bool)
    drag_preview_changed = Signal(object)
    element_selected = Signal(object)
    barrier_drawn = Signal(int, int, int, int)
    cell_hovered = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = MapModel()
        self.heatmap: QImage | None = None
        self.cell_size = 16
        self.show_grid = True
        self.snap_grid = False
        self.tooltips_enabled = True
        self.heatmap_values: np.ndarray | None = None
        self.mode = "select"
        self.selected_id: int | None = None
        self.drag_origin: tuple[int, int] | None = None
        self.drag_element: object | None = None
        self.barrier_start: tuple[int, int] | None = None
        self.barrier_preview: tuple[int, int] | None = None
        self.barrier_dragging = False
        self.drag_preview: tuple[int, int] | None = None
        self.setMouseTracking(True)
        self.setMinimumSize(720, 520)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._update_size()

    def _update_size(self) -> None:
        self.setMinimumSize(
            max(120, round(self.model.length * self.cell_size + 100)),
            max(100, round(self.model.width * self.cell_size + 80)),
        )
        self.resize(
            round(self.model.length * self.cell_size + 100),
            round(self.model.width * self.cell_size + 80),
        )
        self.update()

    def set_map(self, model: MapModel) -> None:
        self.model = model
        self.heatmap = None
        self.heatmap_values = None
        if self.selected_id is not None and not any(
            item.id == self.selected_id for item in model.access_points + model.barriers
        ):
            self.selected_id = None
        self._update_size()

    def set_heatmap(self, signal: np.ndarray) -> None:
        rgba = signal_to_rgba(signal)
        height, width, _ = rgba.shape
        self.heatmap_values = signal
        self.heatmap = QImage(
            rgba.data, width, height, width * 4, QImage.Format.Format_RGBA8888
        ).copy()
        self.update()

    def _map_point(self, position) -> tuple[int, int] | None:
        x = math.floor((position.x() - 70) / self.cell_size)
        screen_y = math.floor((position.y() - 35) / self.cell_size)
        y = self.model.width - 1 - screen_y
        if 0 <= x < self.model.length and 0 <= y < self.model.width:
            return x, y
        return None

    def _hit_test(self, x: int, y: int):
        for point in reversed(self.model.access_points):
            if abs(point.x - x) <= 1 and abs(point.y - y) <= 1:
                return point
        for barrier in reversed(self.model.barriers):
            tolerance = max(0, math.ceil((2 + barrier.thickness // 8) / self.cell_size))
            if barrier.horizontal and abs(barrier.y1 - y) <= tolerance and min(barrier.x1, barrier.x2) <= x <= max(barrier.x1, barrier.x2):
                return barrier
            if not barrier.horizontal and abs(barrier.x1 - x) <= tolerance and min(barrier.y1, barrier.y2) <= y <= max(barrier.y1, barrier.y2):
                return barrier
            if abs(barrier.x1 - x) <= 1 and abs(barrier.y1 - y) <= 1:
                return barrier
        return None

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        position = self._map_point(event.position())
        if position is None:
            return
        x, y = position
        if self.mode == "add-ap":
            self.point_clicked.emit(x, y, False)
        elif self.mode == "draw-barrier":
            if self.barrier_start is None:
                self.barrier_start = position
                self.cell_hovered.emit(f"Choose the barrier endpoint from ({x}, {y}).")
            self.barrier_dragging = True
            self.barrier_preview = position
            self.update()
        else:
            element = self._hit_test(x, y)
            self.drag_element = element
            self.drag_origin = (x, y)
            self.drag_preview = (x, y) if element is not None else None
            self.selected_id = element.id if element else None
            self.element_selected.emit(element)
            self.update()

    def mouseMoveEvent(self, event) -> None:
        position = self._map_point(event.position())
        if position is None:
            self.setToolTip("")
            return
        x, y = position
        if self.mode == "draw-barrier" and self.barrier_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.barrier_preview = position
            self.update()
            return
        if self.drag_element is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.drag_preview = position
            preview_position = position
            if self.snap_grid:
                preview_position = (
                    min(max(round(position[0] / 10) * 10, 0), self.model.length - 1),
                    min(max(round(position[1] / 10) * 10, 0), self.model.width - 1),
                )
                self.drag_preview = preview_position
            self.drag_preview_changed.emit(preview_position)
            self.update()
            return
        barrier = next(
            (b for b in self.model.barriers
             if (b.horizontal and b.y1 == y and min(b.x1, b.x2) <= x <= max(b.x1, b.x2))
             or (not b.horizontal and b.x1 == x and min(b.y1, b.y2) <= y <= max(b.y1, b.y2))),
            None,
        )
        point = next((p for p in self.model.access_points if abs(p.x - x) <= 1 and abs(p.y - y) <= 1), None)
        if barrier:
            text = f"Barrier · {barrier.material} · {barrier.thickness} cm · {MATERIAL_ATTENUATION[barrier.material]:.2f} dB/cm"
        elif point:
            text = f"Access point · ({point.x}, {point.y}) · {point.frequency:.1f} GHz · {point.power} dBm"
        else:
            value = float(self.heatmap_values[x, y]) if self.heatmap_values is not None else math.nan
            if math.isnan(value):
                self.setToolTip("Signal calculation in progress")
                self.cell_hovered.emit("Signal calculation in progress")
                return
            quality = (
                "Excellent" if value >= -60 else "Good" if value >= -70
                else "Weak" if value >= -80 else "Very weak" if value >= -90
                else "Out of range"
            )
            text = f"Cell ({x}, {y}) · {value:.2f} dBm · {quality}"
        self.setToolTip(text if self.tooltips_enabled else "")
        self.cell_hovered.emit(text)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        position = self._map_point(event.position())
        if self.mode == "draw-barrier" and self.barrier_dragging:
            start = self.barrier_start
            self.barrier_dragging = False
            self.barrier_preview = None
            if start is not None and position is not None and position != start:
                self._finish_barrier(start, position)
            self.update()
            return
        if self.drag_element is None:
            return
        element = self.drag_element
        origin = self.drag_origin
        self.drag_element = None
        self.drag_origin = None
        self.drag_preview = None
        if position is None or origin is None or position == origin:
            self.drag_preview_changed.emit(None)
            self.update()
            return
        x, y = position
        if self.snap_grid:
            x, y = round(x / 10) * 10, round(y / 10) * 10
            x = min(max(x, 0), self.model.length - 1)
            y = min(max(y, 0), self.model.width - 1)
        self.drag_origin = (x - origin[0], y - origin[1])
        self.point_clicked.emit(x, y, True)
        self.drag_origin = None
        self.drag_preview_changed.emit(None)
        self.update()

    def _finish_barrier(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        x1, y1 = start
        x2, y2 = end
        if abs(x2 - x1) >= abs(y2 - y1):
            y2 = y1
        else:
            x2 = x1
        if self.snap_grid:
            x1, y1, x2, y2 = (
                round(value / 10) * 10 for value in (x1, y1, x2, y2)
            )
            x1, x2 = min(max(x1, 0), self.model.length - 1), min(max(x2, 0), self.model.length - 1)
            y1, y2 = min(max(y1, 0), self.model.width - 1), min(max(y2, 0), self.model.width - 1)
        self.barrier_start = None
        if (x1, y1) != (x2, y2):
            self.barrier_drawn.emit(x1, y1, x2, y2)

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y()
        old_size = self.cell_size
        new_size = max(0.1, min(128.0, old_size * (1.2 if delta > 0 else 1 / 1.2)))
        if new_size == old_size:
            return
        cursor = event.position()
        scroll_area = self.parentWidget()
        while scroll_area is not None and not isinstance(scroll_area, QScrollArea):
            scroll_area = scroll_area.parentWidget()
        if scroll_area is not None:
            horizontal_value = scroll_area.horizontalScrollBar().value()
            vertical_value = scroll_area.verticalScrollBar().value()
        self.cell_size = new_size
        self._update_size()
        if scroll_area is not None:
            ratio = new_size / old_size
            scroll_area.horizontalScrollBar().setValue(
                round(horizontal_value + (cursor.x() - horizontal_value - 70) * (ratio - 1))
            )
            scroll_area.verticalScrollBar().setValue(
                round(vertical_value + (cursor.y() - vertical_value - 35) * (ratio - 1))
            )

    def fit_to_view(self) -> None:
        scroll_area = self.parentWidget()
        while scroll_area is not None and not isinstance(scroll_area, QScrollArea):
            scroll_area = scroll_area.parentWidget()
        if scroll_area is None:
            return
        viewport = scroll_area.viewport().size()
        available_width = max(1, viewport.width() - 100)
        available_height = max(1, viewport.height() - 80)
        self.cell_size = max(
            0.1,
            min(128.0, available_width / self.model.length, available_height / self.model.width),
        )
        self._update_size()
        scroll_area.horizontalScrollBar().setValue(0)
        scroll_area.verticalScrollBar().setValue(0)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f4f6f8"))
        origin_x, origin_y = 70, 35
        map_rect = (
            origin_x, origin_y,
            round(self.model.length * self.cell_size),
            round(self.model.width * self.cell_size),
        )
        painter.fillRect(*map_rect, QColor("#e6e9ed"))
        if self.heatmap:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            painter.drawImage(
                origin_x, origin_y,
                self.heatmap.scaled(
                    map_rect[2], map_rect[3],
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                ),
            )
        if self.show_grid and self.cell_size >= 9:
            painter.setPen(QPen(QColor(255, 255, 255, 45), 1))
            for x in range(self.model.length + 1):
                px = round(origin_x + x * self.cell_size)
                painter.drawLine(px, origin_y, px, origin_y + map_rect[3])
            for y in range(self.model.width + 1):
                py = round(origin_y + y * self.cell_size)
                painter.drawLine(origin_x, py, origin_x + map_rect[2], py)
        painter.setPen(QPen(QColor("#263238"), 1))
        painter.drawRect(*map_rect)
        painter.setPen(QColor("#37474f"))
        painter.drawText(8, 18, f"{self.model.length} × {self.model.width} m")
        for value in range(0, self.model.length, 10):
            px = round(origin_x + value * self.cell_size)
            painter.drawText(px, origin_y + map_rect[3] + 20, str(value))
        for value in range(0, self.model.width, 10):
            py = round(origin_y + map_rect[3] - value * self.cell_size)
            painter.drawText(38, py + 4, str(value))
        for barrier in self.model.barriers:
            preview = self._preview_barrier(barrier)
            start = self._screen_point(preview[0], preview[1])
            end = self._screen_point(preview[2], preview[3])
            colors = {
                "Plaster": "#ffc9d3", "Wood": "#98633b", "Brick": "#e87816",
                "Cement": "#888888", "Reinforced concrete": "#50545a", "Metal": "#1686bb",
            }
            thickness = max(3, min(16, 2 + barrier.thickness // 8))
            painter.setPen(QPen(QColor(colors[barrier.material]), thickness))
            painter.drawLine(*start, *end)
            if barrier.id == self.selected_id:
                painter.setPen(QPen(QColor("#ff1744"), max(2, thickness // 3)))
                painter.drawLine(*start, *end)
        if self.mode == "draw-barrier" and self.barrier_start is not None and self.barrier_preview is not None:
            x1, y1 = self.barrier_start
            x2, y2 = self.barrier_preview
            if abs(x2 - x1) >= abs(y2 - y1):
                y2 = y1
            else:
                x2 = x1
            painter.setPen(QPen(QColor("#d50000"), max(2, round(self.cell_size / 5))))
            painter.drawLine(*self._screen_point(x1, y1), *self._screen_point(x2, y2))
        for point in self.model.access_points:
            px, py = self._screen_point(*self._preview_point(point))
            radius = max(3, round(self.cell_size / 2))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.setBrush(QColor("#111827"))
            painter.drawEllipse(px - radius, py - radius, radius * 2, radius * 2)
            if point.id == self.selected_id:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(QColor("#ff1744"), 2))
                painter.drawEllipse(px - radius - 3, py - radius - 3, radius * 2 + 6, radius * 2 + 6)
        painter.end()

    def _preview_point(self, point) -> tuple[int, int]:
        if self.drag_element is point and self.drag_preview is not None:
            return self.drag_preview
        return point.x, point.y

    def _preview_barrier(self, barrier) -> tuple[int, int, int, int]:
        if self.drag_element is barrier and self.drag_preview is not None and self.drag_origin is not None:
            dx = self.drag_preview[0] - self.drag_origin[0]
            dy = self.drag_preview[1] - self.drag_origin[1]
            return barrier.x1 + dx, barrier.y1 + dy, barrier.x2 + dx, barrier.y2 + dy
        return barrier.x1, barrier.y1, barrier.x2, barrier.y2

    def _screen_point(self, x: int, y: int) -> tuple[int, int]:
        return (
            round(70 + x * self.cell_size + self.cell_size / 2),
            round(35 + (self.model.width - 1 - y) * self.cell_size + self.cell_size / 2),
        )

    def export_png(self, path: str) -> None:
        cell = 4
        width, height = self.model.length * cell + 100, self.model.width * cell + 80
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor("#f4f6f8"))
        painter = QPainter(image)
        if self.heatmap:
            painter.drawImage(
                55, 20,
                self.heatmap.scaled(
                    self.model.length * cell, self.model.width * cell,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                ),
            )
        for barrier in self.model.barriers:
            start = (round(55 + (barrier.x1 + 0.5) * cell), round(20 + (self.model.width - 1 - barrier.y1 + 0.5) * cell))
            end = (round(55 + (barrier.x2 + 0.5) * cell), round(20 + (self.model.width - 1 - barrier.y2 + 0.5) * cell))
            painter.setPen(QPen(QColor("#343a40"), 3))
            painter.drawLine(*start, *end)
        for point in self.model.access_points:
            px = round(55 + (point.x + 0.5) * cell)
            py = round(20 + (self.model.width - 1 - point.y + 0.5) * cell)
            painter.setBrush(QColor("#101820"))
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawEllipse(int(px - 4), int(py - 4), 8, 8)
        painter.end()
        if not image.save(path, "PNG"):
            raise OSError(f"Could not write PNG file: {path}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WifiMap")
        self.resize(1280, 820)
        self.model = MapModel()
        self._undo: list[dict] = []
        self._redo: list[dict] = []
        self._clipboard: dict | None = None
        self._generation = 0
        self._preview_revision = 0
        self._preview_running = False
        self._preview_pending: dict | None = None
        self._preview_active = False
        self._calculation_tasks: dict[tuple[str, int], _CalculationTask] = {}
        self._thread_pool = QThreadPool.globalInstance()
        self._preview_timer = QTimer(self)
        self._preview_timer.setInterval(120)
        self._preview_timer.timeout.connect(self._start_live_preview)
        self._build_ui()
        self._refresh_map()

    def _build_ui(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        self._action(file_menu, "&New map…", "Ctrl+N", self.new_map)
        self._action(file_menu, "&Open…", "Ctrl+O", self.open_map)
        self._action(file_menu, "&Save", "Ctrl+S", self.save_map)
        self._action(file_menu, "Export &PNG…", "Ctrl+E", self.export_png)
        file_menu.addSeparator()
        self._action(file_menu, "E&xit", "Ctrl+Q", self.close)
        edit_menu = self.menuBar().addMenu("&Edit")
        self._action(edit_menu, "&Undo", "Ctrl+Z", self.undo)
        self._action(edit_menu, "&Redo", "Ctrl+Y", self.redo)
        self._action(edit_menu, "Copy selected", "Ctrl+C", self._copy_selected)
        self._action(edit_menu, "Paste", "Ctrl+V", self._paste)
        self._action(edit_menu, "&Delete selected", "Delete", self._delete_selected)
        self._action(edit_menu, "&Fit map to view", "Ctrl+0", self._fit_map)

        splitter = QSplitter()
        self.canvas = MapCanvas()
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(False)
        splitter.addWidget(scroll)
        splitter.addWidget(self._build_controls())
        splitter.setStretchFactor(0, 1)
        splitter.setSizes([900, 340])
        self.setCentralWidget(splitter)
        self.setStatusBar(QStatusBar())
        self.canvas.element_selected.connect(self._selection_changed)
        self.canvas.point_clicked.connect(self._canvas_action)
        self.canvas.drag_preview_changed.connect(self._queue_live_preview)
        self.canvas.barrier_drawn.connect(self._create_drawn_barrier)
        self.canvas.cell_hovered.connect(self.statusBar().showMessage)

    def _build_controls(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(300)
        layout = QVBoxLayout(panel)
        map_group = QGroupBox("Map")
        map_form = QFormLayout(map_group)
        self.length_spin = self._spin(1, 500, 50)
        self.width_spin = self._spin(1, 500, 50)
        map_form.addRow("Length (m)", self.length_spin)
        map_form.addRow("Width (m)", self.width_spin)
        map_buttons = QHBoxLayout()
        resize_button = QPushButton("Resize (keep items)")
        resize_button.clicked.connect(self.resize_map)
        fit_button = QPushButton("Fit map to view")
        fit_button.clicked.connect(self._fit_map)
        clear_button = QPushButton("New / clear")
        clear_button.clicked.connect(self.new_map)
        map_buttons.addWidget(resize_button)
        map_buttons.addWidget(fit_button)
        map_buttons.addWidget(clear_button)
        map_form.addRow(map_buttons)
        layout.addWidget(map_group)

        tools = QGroupBox("Map tools")
        tool_layout = QVBoxLayout(tools)
        self.select_button = QPushButton("Select / move")
        self.add_mode_button = QPushButton("Place access point")
        self.barrier_mode_button = QPushButton("Draw barrier (drag or click)")
        self.select_button.clicked.connect(lambda: self._set_mode("select"))
        self.add_mode_button.clicked.connect(lambda: self._set_mode("add-ap"))
        self.barrier_mode_button.clicked.connect(lambda: self._set_mode("draw-barrier"))
        tool_layout.addWidget(self.select_button)
        tool_layout.addWidget(self.add_mode_button)
        tool_layout.addWidget(self.barrier_mode_button)
        self.grid_check = QCheckBox("Show grid")
        self.grid_check.setChecked(True)
        self.grid_check.toggled.connect(self._toggle_grid)
        self.snap_check = QCheckBox("Snap to 10 m")
        self.snap_check.toggled.connect(self._toggle_snap)
        self.tooltip_check = QCheckBox("Tooltips")
        self.tooltip_check.setChecked(True)
        self.tooltip_check.toggled.connect(self._toggle_tooltips)
        tool_layout.addWidget(self.grid_check)
        tool_layout.addWidget(self.snap_check)
        tool_layout.addWidget(self.tooltip_check)
        layout.addWidget(tools)

        tabs = QTabWidget()
        ap_tab = QWidget()
        ap_form = QFormLayout(ap_tab)
        self.ap_x = self._spin(0, 499, 10)
        self.ap_y = self._spin(0, 499, 10)
        self.ap_frequency = QComboBox()
        self.ap_frequency.addItems(["2.4 GHz", "5.0 GHz"])
        self.ap_power = self._spin(11, 20, 15)
        ap_form.addRow("X", self.ap_x)
        ap_form.addRow("Y", self.ap_y)
        ap_form.addRow("Frequency", self.ap_frequency)
        ap_form.addRow("Power (dBm)", self.ap_power)
        ap_buttons = QHBoxLayout()
        add_ap = QPushButton("Add")
        update_ap = QPushButton("Update selected")
        delete_ap = QPushButton("Delete selected")
        add_ap.clicked.connect(self._add_ap)
        update_ap.clicked.connect(self._update_ap)
        delete_ap.clicked.connect(self._delete_selected)
        ap_buttons.addWidget(add_ap)
        ap_buttons.addWidget(update_ap)
        ap_buttons.addWidget(delete_ap)
        ap_form.addRow(ap_buttons)
        tabs.addTab(ap_tab, "Access point")

        barrier_tab = QWidget()
        barrier_form = QFormLayout(barrier_tab)
        self.barrier_x = self._spin(0, 499, 5)
        self.barrier_y = self._spin(0, 499, 5)
        self.barrier_length = self._spin(1, 499, 10)
        self.barrier_orientation = QComboBox()
        self.barrier_orientation.addItems(["Horizontal", "Vertical"])
        self.barrier_thickness = self._spin(1, 60, 10)
        self.barrier_material = QComboBox()
        self.barrier_material.addItems(list(MATERIAL_ATTENUATION))
        barrier_form.addRow("Start X", self.barrier_x)
        barrier_form.addRow("Start Y", self.barrier_y)
        barrier_form.addRow("Length (m)", self.barrier_length)
        barrier_form.addRow("Orientation", self.barrier_orientation)
        barrier_form.addRow("Thickness (cm)", self.barrier_thickness)
        barrier_form.addRow("Material", self.barrier_material)
        barrier_buttons = QHBoxLayout()
        add_barrier = QPushButton("Add")
        update_barrier = QPushButton("Update selected")
        delete_barrier = QPushButton("Delete selected")
        add_barrier.clicked.connect(self._add_barrier)
        update_barrier.clicked.connect(self._update_barrier)
        delete_barrier.clicked.connect(self._delete_selected)
        barrier_buttons.addWidget(add_barrier)
        barrier_buttons.addWidget(update_barrier)
        barrier_buttons.addWidget(delete_barrier)
        barrier_form.addRow(barrier_buttons)
        tabs.addTab(barrier_tab, "Barrier")
        layout.addWidget(tabs)

        self.legend = QLabel("−100 dBm                                      −20 dBm")
        self.legend.setStyleSheet(
            "padding: 10px; font-weight: 600; "
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #000064,stop:0.2 blue,stop:0.4 #00ffff,"
            "stop:0.55 lime,stop:0.7 yellow,stop:0.85 orangered,stop:1 #930000);"
        )
        layout.addWidget(self.legend)
        self.progress_label = QLabel("Calculating signal…")
        layout.addWidget(self.progress_label)
        layout.addStretch(1)
        self.length_spin.valueChanged.connect(self._sync_canvas_spin_ranges)
        self.width_spin.valueChanged.connect(self._sync_canvas_spin_ranges)
        return panel

    @staticmethod
    def _spin(minimum: int, maximum: int, value: int) -> QSpinBox:
        control = QSpinBox()
        control.setRange(minimum, maximum)
        control.setValue(value)
        return control

    def _action(self, menu, text: str, shortcut: str, callback) -> None:
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)

    def _sync_canvas_spin_ranges(self) -> None:
        self.ap_x.setMaximum(max(0, self.length_spin.value() - 1))
        self.barrier_x.setMaximum(max(0, self.length_spin.value() - 1))
        self.ap_y.setMaximum(max(0, self.width_spin.value() - 1))
        self.barrier_y.setMaximum(max(0, self.width_spin.value() - 1))
        self.barrier_length.setMaximum(max(self.length_spin.value(), self.width_spin.value()) - 1)

    def _set_mode(self, mode: str) -> None:
        self.canvas.mode = mode
        self.canvas.barrier_start = None
        self.canvas.barrier_preview = None
        self.canvas.barrier_dragging = False
        labels = {"select": "Select / drag access points and barriers", "add-ap": "Click map to place access point", "draw-barrier": "Drag to draw a barrier, or click start and endpoint"}
        self.statusBar().showMessage(labels[mode])
        self.canvas.update()

    def _fit_map(self) -> None:
        self.canvas.fit_to_view()

    def _toggle_grid(self, enabled: bool) -> None:
        self.canvas.show_grid = enabled
        self.canvas.update()

    def _toggle_snap(self, enabled: bool) -> None:
        self.canvas.snap_grid = enabled

    def _toggle_tooltips(self, enabled: bool) -> None:
        self.canvas.tooltips_enabled = enabled

    def _refresh_map(self) -> None:
        self.canvas.set_map(self.model)
        self.length_spin.setValue(self.model.length)
        self.width_spin.setValue(self.model.width)
        self._sync_canvas_spin_ranges()
        self._recalculate()

    def _recalculate(self) -> None:
        self._cancel_live_preview()
        self._generation += 1
        generation = self._generation
        task = _CalculationTask(generation, self.model.to_dict())
        self._calculation_tasks[("map", generation)] = task
        task.signals.finished.connect(self._calculation_finished)
        task.signals.failed.connect(self._calculation_failed)
        self.progress_label.setText("Calculating signal…")
        self._thread_pool.start(task)

    def _cancel_live_preview(self) -> None:
        self._preview_timer.stop()
        self._preview_pending = None
        self._preview_revision += 1
        self._preview_active = False

    def _queue_live_preview(self, position) -> None:
        if position is None:
            if self._preview_pending is not None:
                self._preview_pending = None
            if self._preview_active:
                self._cancel_live_preview()
                self._recalculate()
            return
        element = self.canvas.drag_element
        origin = self.canvas.drag_origin
        if element is None or origin is None:
            return
        dx, dy = position[0] - origin[0], position[1] - origin[1]
        snapshot = self.model.to_dict()
        if hasattr(element, "frequency"):
            row = next(
                item for item in snapshot["access_points"] if item["id"] == element.id
            )
            row["x"], row["y"] = element.x + dx, element.y + dy
        else:
            row = next(item for item in snapshot["barriers"] if item["id"] == element.id)
            row["x1"], row["y1"] = element.x1 + dx, element.y1 + dy
            row["x2"], row["y2"] = element.x2 + dx, element.y2 + dy
        try:
            MapModel.from_dict(snapshot)
        except ValueError as error:
            self._preview_revision += 1
            self._preview_pending = None
            self._preview_timer.stop()
            self.statusBar().showMessage(f"Live heatmap paused: {error}", 1500)
            return
        self._preview_revision += 1
        self._preview_active = True
        self._preview_pending = snapshot
        if not self._preview_timer.isActive():
            self._preview_timer.start()

    def _start_live_preview(self) -> None:
        if self._preview_running:
            return
        if self._preview_pending is None or not self._preview_active:
            self._preview_timer.stop()
            return
        self._preview_running = True
        snapshot = self._preview_pending
        self._preview_pending = None
        revision = self._preview_revision
        task = _CalculationTask(revision, snapshot)
        self._calculation_tasks[("preview", revision)] = task
        task.signals.finished.connect(self._live_preview_finished)
        task.signals.failed.connect(self._live_preview_failed)
        self._thread_pool.start(task)

    def _live_preview_finished(self, revision: int, signal: object) -> None:
        self._calculation_tasks.pop(("preview", revision), None)
        self._preview_running = False
        if self._preview_active and revision == self._preview_revision:
            self.canvas.set_heatmap(signal)
            self.statusBar().showMessage("Live signal preview", 1000)
        if self._preview_pending is None or not self._preview_active:
            self._preview_timer.stop()

    def _live_preview_failed(self, revision: int, error: str) -> None:
        self._calculation_tasks.pop(("preview", revision), None)
        self._preview_running = False
        if self._preview_active and revision == self._preview_revision:
            self.statusBar().showMessage(f"Live heatmap preview failed: {error}", 3000)
        if self._preview_pending is None or not self._preview_active:
            self._preview_timer.stop()

    def _calculation_finished(self, generation: int, signal: object) -> None:
        if generation != self._generation:
            self._calculation_tasks.pop(("map", generation), None)
            return
        self._calculation_tasks.pop(("map", generation), None)
        self.model._signal_cache = signal
        self.canvas.set_heatmap(signal)
        self.progress_label.setText(f"Ready · {len(self.model.access_points)} access point(s)")

    def _calculation_failed(self, generation: int, error: str) -> None:
        self._calculation_tasks.pop(("map", generation), None)
        if generation == self._generation:
            self.progress_label.setText("Signal calculation failed")
            self._show_error(error)

    def _record_change(self, operation):
        before = self.model.to_dict()
        try:
            result = operation()
        except (ValueError, KeyError, TypeError) as error:
            self._show_error(str(error))
            return None
        self._undo.append(before)
        self._redo.clear()
        selected_id = self.canvas.selected_id
        self.canvas.set_map(self.model)
        if selected_id is not None and any(
            item.id == selected_id for item in self.model.access_points + self.model.barriers
        ):
            self.canvas.selected_id = selected_id
            self.canvas.update()
        self.length_spin.setValue(self.model.length)
        self.width_spin.setValue(self.model.width)
        self._sync_canvas_spin_ranges()
        self._recalculate()
        return result

    def _add_ap(self) -> None:
        self._record_change(lambda: self.model.add_access_point(
            self.ap_x.value(), self.ap_y.value(),
            2.4 if self.ap_frequency.currentIndex() == 0 else 5.0,
            self.ap_power.value(),
        ))

    def _update_ap(self) -> None:
        selected = self._selected_item()
        if not isinstance(selected, dict) or selected["kind"] != "access_point":
            self._show_error("Select an access point on the map first.")
            return
        self._record_change(lambda: self.model.update_access_point(
            selected["id"], self.ap_x.value(), self.ap_y.value(),
            2.4 if self.ap_frequency.currentIndex() == 0 else 5.0,
            self.ap_power.value(),
        ))

    def _barrier_values(self) -> tuple[int, int, int, int, int, str]:
        x1, y1 = self.barrier_x.value(), self.barrier_y.value()
        length = self.barrier_length.value()
        if self.barrier_orientation.currentIndex() == 0:
            x2, y2 = x1 + length, y1
        else:
            x2, y2 = x1, y1 + length
        return x1, y1, x2, y2, self.barrier_thickness.value(), self.barrier_material.currentText()

    def _add_barrier(self) -> None:
        self._record_change(lambda: self.model.add_barrier(*self._barrier_values()))

    def _update_barrier(self) -> None:
        selected = self._selected_item()
        if not isinstance(selected, dict) or selected["kind"] != "barrier":
            self._show_error("Select a barrier on the map first.")
            return
        self._record_change(lambda: self.model.update_barrier(selected["id"], *self._barrier_values()))

    def _delete_selected(self) -> None:
        if self.canvas.selected_id is None:
            self._show_error("Select an element on the map first.")
            return
        self._record_change(lambda: self.model.remove(self.canvas.selected_id))
        self._selection_changed(None)

    def _copy_selected(self) -> None:
        selected_id = self.canvas.selected_id
        if selected_id is None:
            self.statusBar().showMessage("Select one access point or barrier to copy.", 4000)
            return
        for point in self.model.access_points:
            if point.id == selected_id:
                self._clipboard = {"kind": "access_point", "item": asdict(point)}
                self.statusBar().showMessage("Access point copied.", 4000)
                return
        for barrier in self.model.barriers:
            if barrier.id == selected_id:
                self._clipboard = {"kind": "barrier", "item": asdict(barrier)}
                self.statusBar().showMessage("Barrier copied.", 4000)
                return
        self.canvas.selected_id = None
        self.canvas.update()
        self.statusBar().showMessage("The selected element no longer exists.", 4000)

    @staticmethod
    def _paste_offset(minimum: int, maximum: int, dimension: int) -> int:
        offset = 5
        if maximum + offset < dimension:
            return offset
        if minimum - offset >= 0:
            return -offset
        raise ValueError("There is not enough room to paste this element with a 5 m offset.")

    def _paste(self) -> None:
        if self._clipboard is None:
            self.statusBar().showMessage("Copy an access point or barrier before pasting.", 4000)
            return
        kind = self._clipboard["kind"]
        item = self._clipboard["item"]
        try:
            if kind == "access_point":
                x = item["x"] + self._paste_offset(item["x"], item["x"], self.model.length)
                y = item["y"] + self._paste_offset(item["y"], item["y"], self.model.width)
                pasted = self._record_change(lambda: self.model.add_access_point(
                    x, y, item["frequency"], item["power"]
                ))
            else:
                dx = self._paste_offset(
                    min(item["x1"], item["x2"]), max(item["x1"], item["x2"]), self.model.length
                )
                dy = self._paste_offset(
                    min(item["y1"], item["y2"]), max(item["y1"], item["y2"]), self.model.width
                )
                pasted = self._record_change(lambda: self.model.add_barrier(
                    item["x1"] + dx, item["y1"] + dy,
                    item["x2"] + dx, item["y2"] + dy,
                    item["thickness"], item["material"],
                ))
        except ValueError as error:
            self._show_error(str(error))
            return
        if pasted is None:
            return
        self.canvas.selected_id = pasted.id
        self.canvas.update()
        self._selection_changed(pasted)
        self.statusBar().showMessage(f"Pasted {kind.replace('_', ' ')} at a 5 m offset.", 4000)

    def _selected_item(self):
        if self.canvas.selected_id is None:
            return None
        for point in self.model.access_points:
            if point.id == self.canvas.selected_id:
                return {"kind": "access_point", "id": point.id}
        for barrier in self.model.barriers:
            if barrier.id == self.canvas.selected_id:
                return {"kind": "barrier", "id": barrier.id}
        return None

    def _selection_changed(self, item) -> None:
        if item is None:
            return
        if hasattr(item, "frequency"):
            self.ap_x.setValue(item.x)
            self.ap_y.setValue(item.y)
            self.ap_frequency.setCurrentIndex(0 if item.frequency == 2.4 else 1)
            self.ap_power.setValue(item.power)
            self.statusBar().showMessage(f"Selected access point #{item.id}")
        else:
            self.barrier_x.setValue(min(item.x1, item.x2))
            self.barrier_y.setValue(min(item.y1, item.y2))
            self.barrier_length.setValue(abs(item.x2 - item.x1) + abs(item.y2 - item.y1))
            self.barrier_orientation.setCurrentIndex(0 if item.horizontal else 1)
            self.barrier_thickness.setValue(item.thickness)
            self.barrier_material.setCurrentText(item.material)
            self.statusBar().showMessage(f"Selected barrier #{item.id}")

    def _canvas_action(self, x: int, y: int, moving: bool) -> None:
        if moving:
            selected = self._selected_item()
            if not selected:
                return
            dx, dy = self.canvas.drag_origin or (0, 0)
            if selected["kind"] == "access_point":
                point = next(p for p in self.model.access_points if p.id == selected["id"])
                self._record_change(lambda: self.model.update_access_point(
                    point.id, point.x + dx, point.y + dy, point.frequency, point.power
                ))
            else:
                barrier = next(b for b in self.model.barriers if b.id == selected["id"])
                self._record_change(lambda: self.model.update_barrier(
                    barrier.id, barrier.x1 + dx, barrier.y1 + dy,
                    barrier.x2 + dx, barrier.y2 + dy, barrier.thickness, barrier.material
                ))
            return
        self.ap_x.setValue(x)
        self.ap_y.setValue(y)
        if self.canvas.mode == "add-ap":
            self._add_ap()
            self._set_mode("select")

    def _create_drawn_barrier(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.barrier_x.setValue(x1)
        self.barrier_y.setValue(y1)
        self.barrier_orientation.setCurrentIndex(0 if y1 == y2 else 1)
        self.barrier_length.setValue(abs(x2 - x1) + abs(y2 - y1))
        self._record_change(lambda: self.model.add_barrier(
            x1, y1, x2, y2, self.barrier_thickness.value(), self.barrier_material.currentText()
        ))

    def resize_map(self) -> None:
        self._record_change(lambda: self.model.resize(self.length_spin.value(), self.width_spin.value()))

    def new_map(self) -> None:
        if (self.model.access_points or self.model.barriers) and QMessageBox.question(
            self, "New map", "Clear the current map and all its elements?"
        ) != QMessageBox.StandardButton.Yes:
            return
        length, width = self.length_spin.value(), self.width_spin.value()
        self._record_change(lambda: self.model.resize(length, width, preserve_elements=False))

    def save_map(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save map", "", "WifiMap JSON (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            Path(path).write_text(json.dumps(self.model.to_dict(), indent=2), encoding="utf-8")
            self.statusBar().showMessage(f"Saved {Path(path).name}", 5000)
        except OSError as error:
            self._show_error(f"Could not save map: {error}")

    def open_map(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open map", "", "WifiMap JSON (*.json)")
        if not path:
            return
        try:
            loaded = MapModel.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
            self._show_error(f"Could not open map: {error}")
            return
        self._undo.append(self.model.to_dict())
        self._redo.clear()
        self.model = loaded
        self._refresh_map()
        self.statusBar().showMessage(f"Opened {Path(path).name}", 5000)

    def export_png(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export map as PNG", "", "PNG image (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        try:
            self.canvas.export_png(path)
            self.statusBar().showMessage(f"Exported {Path(path).name}", 5000)
        except OSError as error:
            self._show_error(str(error))

    def undo(self) -> None:
        if not self._undo:
            return
        self._redo.append(self.model.to_dict())
        self.model = MapModel.from_dict(self._undo.pop())
        self._refresh_map()

    def redo(self) -> None:
        if not self._redo:
            return
        self._undo.append(self.model.to_dict())
        self.model = MapModel.from_dict(self._redo.pop())
        self._refresh_map()

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "WifiMap", message)


def run() -> int:
    app = QApplication([])
    app.setApplicationName("WifiMap")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
