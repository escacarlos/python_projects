from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QScrollArea

from wifimap.model import MapModel
from wifimap.window import MainWindow, MapCanvas


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _event(x: int, y: int, *, button=None, buttons=Qt.MouseButton.NoButton):
    return SimpleNamespace(
        position=lambda: QPointF(x, y),
        button=lambda: button,
        buttons=lambda: buttons,
    )


def test_selection_survives_click_and_map_refresh() -> None:
    _app()
    model = MapModel(30, 30)
    point = model.add_access_point(10, 12, 2.4, 15)
    canvas = MapCanvas()
    canvas.set_map(model)
    selected = []
    canvas.element_selected.connect(selected.append)
    px, py = canvas._screen_point(point.x, point.y)

    canvas.mousePressEvent(_event(px, py, button=Qt.MouseButton.LeftButton))
    canvas.mouseReleaseEvent(_event(px, py, button=Qt.MouseButton.LeftButton))
    canvas.set_map(model)

    assert selected == [point]
    assert canvas.selected_id == point.id
    canvas.close()


def test_barrier_can_be_selected_from_its_drawn_line() -> None:
    _app()
    model = MapModel(30, 30)
    barrier = model.add_barrier(4, 8, 20, 8, 20, "Brick")
    canvas = MapCanvas()
    canvas.set_map(model)
    selected = []
    canvas.element_selected.connect(selected.append)
    px, py = canvas._screen_point(12, 8)

    canvas.mousePressEvent(_event(px, py, button=Qt.MouseButton.LeftButton))
    canvas.mouseReleaseEvent(_event(px, py, button=Qt.MouseButton.LeftButton))

    assert selected == [barrier]
    assert canvas.selected_id == barrier.id
    canvas.close()


def test_drag_shows_live_preview_and_emits_move_on_release() -> None:
    _app()
    model = MapModel(30, 30)
    point = model.add_access_point(10, 12, 2.4, 15)
    canvas = MapCanvas()
    canvas.set_map(model)
    moved = []
    canvas.point_clicked.connect(lambda x, y, is_move: moved.append((x, y, is_move)))
    start = canvas._screen_point(point.x, point.y)
    destination = canvas._screen_point(15, 17)

    canvas.mousePressEvent(_event(*start, button=Qt.MouseButton.LeftButton))
    canvas.mouseMoveEvent(_event(*destination, buttons=Qt.MouseButton.LeftButton))
    assert canvas._preview_point(point) == (15, 17)
    canvas.mouseReleaseEvent(_event(*destination, button=Qt.MouseButton.LeftButton))

    assert moved == [(15, 17, True)]
    assert canvas.drag_preview is None
    canvas.close()


def test_barrier_can_be_drawn_by_dragging() -> None:
    _app()
    canvas = MapCanvas()
    canvas.mode = "draw-barrier"
    drawn = []
    canvas.barrier_drawn.connect(lambda *coordinates: drawn.append(coordinates))
    start = canvas._screen_point(4, 8)
    end = canvas._screen_point(20, 12)

    canvas.mousePressEvent(_event(*start, button=Qt.MouseButton.LeftButton))
    canvas.mouseMoveEvent(_event(*end, buttons=Qt.MouseButton.LeftButton))
    assert canvas.barrier_preview == (20, 12)
    canvas.mouseReleaseEvent(_event(*end, button=Qt.MouseButton.LeftButton))

    assert drawn == [(4, 8, 20, 8)]
    assert canvas.barrier_start is None
    canvas.close()


def test_fit_to_view_shows_full_500_by_500_map() -> None:
    _app()
    scroll = QScrollArea()
    canvas = MapCanvas()
    canvas.set_map(MapModel(500, 500))
    scroll.setWidget(canvas)
    scroll.resize(900, 700)
    scroll.show()
    QApplication.processEvents()

    canvas.fit_to_view()
    QApplication.processEvents()

    assert canvas.width() <= scroll.viewport().width()
    assert canvas.height() <= scroll.viewport().height()
    assert canvas.cell_size < 2
    scroll.close()


def test_copy_paste_access_point_and_barrier_with_boundary_fallback() -> None:
    app = _app()
    window = MainWindow()
    window.model = MapModel(30, 30)
    point = window.model.add_access_point(10, 10, 5.0, 18)
    window.canvas.set_map(window.model)
    window.canvas.selected_id = point.id

    window._copy_selected()
    window._paste()

    pasted_point = next(item for item in window.model.access_points if item.id != point.id)
    assert (pasted_point.x, pasted_point.y) == (15, 15)
    assert (pasted_point.frequency, pasted_point.power) == (5.0, 18)
    assert window.canvas.selected_id == pasted_point.id

    barrier = window.model.add_barrier(20, 27, 28, 27, 14, "Brick")
    window.canvas.set_map(window.model)
    window.canvas.selected_id = barrier.id
    window._copy_selected()
    window._paste()

    pasted_barrier = next(item for item in window.model.barriers if item.id != barrier.id)
    assert (pasted_barrier.x1, pasted_barrier.y1) == (15, 22)
    assert (pasted_barrier.x2, pasted_barrier.y2) == (23, 22)
    assert (pasted_barrier.thickness, pasted_barrier.material) == (14, "Brick")
    assert window.canvas.selected_id == pasted_barrier.id
    window._thread_pool.waitForDone(3000)
    window.close()
    app.processEvents()


def test_paste_offset_uses_opposite_direction_or_rejects_too_small_map() -> None:
    _app()
    assert MainWindow._paste_offset(25, 29, 30) == -5
    assert MainWindow._paste_offset(0, 2, 8) == 5
    try:
        MainWindow._paste_offset(1, 3, 5)
    except ValueError as error:
        assert "5 m offset" in str(error)
    else:
        raise AssertionError("Expected map with insufficient offset room to be rejected")


def test_drag_recalculates_live_heatmap_without_mutating_map_until_drop() -> None:
    app = _app()
    window = MainWindow()
    window.model = MapModel(40, 30)
    point = window.model.add_access_point(8, 10, 2.4, 20)
    window.model.add_access_point(32, 20, 5.0, 15)
    window.canvas.set_map(window.model)
    window._recalculate()
    window._thread_pool.waitForDone(3000)
    app.processEvents()
    original_heatmap = window.canvas.heatmap_values.copy()

    window.canvas.drag_element = point
    window.canvas.drag_origin = (point.x, point.y)
    window._queue_live_preview((18, 12))
    QTest.qWait(250)
    window._thread_pool.waitForDone(3000)
    app.processEvents()

    expected = MapModel.from_dict(window.model.to_dict())
    expected.update_access_point(point.id, 18, 12, point.frequency, point.power)
    assert (point.x, point.y) == (8, 10)
    assert not np.array_equal(window.canvas.heatmap_values, original_heatmap)
    assert np.allclose(window.canvas.heatmap_values, expected.signal)

    window._queue_live_preview(None)
    window._thread_pool.waitForDone(3000)
    app.processEvents()
    assert np.allclose(window.canvas.heatmap_values, original_heatmap)
    window.close()
