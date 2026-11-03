import numpy as np
import pytest

from wifimap.model import MapModel


def test_signal_is_vectorized_cached_and_invalidated() -> None:
    model = MapModel(40, 30)
    point = model.add_access_point(10, 12, 2.4, 20)
    first = model.signal
    assert first.shape == (40, 30)
    assert first[10, 12] > first[20, 12]
    assert model.signal is first

    model.update_access_point(point.id, 12, 12, 2.4, 20)
    assert model.signal is not first
    assert model.signal[12, 12] > model.signal[10, 12]


def test_barrier_attenuates_signal_behind_it() -> None:
    clear = MapModel(30, 20)
    blocked = MapModel(30, 20)
    clear.add_access_point(5, 10, 2.4, 20)
    blocked.add_access_point(5, 10, 2.4, 20)
    blocked.add_barrier(10, 0, 10, 19, 20, "Brick")

    assert blocked.signal[20, 10] < clear.signal[20, 10]
    assert blocked.signal[8, 10] == pytest.approx(clear.signal[8, 10])


def test_map_round_trip_and_resize_validation() -> None:
    model = MapModel(60, 40)
    model.add_access_point(15, 20, 5.0, 13)
    model.add_barrier(20, 10, 28, 10, 12, "Wood")

    loaded = MapModel.from_dict(model.to_dict())
    assert loaded.length == 60
    assert loaded.width == 40
    assert loaded.access_points[0].id == model.access_points[0].id
    assert [(p.x, p.y, p.frequency, p.power) for p in loaded.access_points] == [
        (15, 20, 5.0, 13)
    ]
    assert loaded.barriers[0].id == model.barriers[0].id
    assert [(b.x1, b.y1, b.x2, b.y2, b.material) for b in loaded.barriers] == [
        (20, 10, 28, 10, "Wood")
    ]
    with pytest.raises(ValueError, match="outside"):
        loaded.resize(10, 10)


def test_invalid_elements_and_duplicate_occupancy_are_rejected() -> None:
    model = MapModel(20, 20)
    model.add_access_point(4, 4, 2.4, 15)
    with pytest.raises(ValueError, match="occupied"):
        model.add_access_point(4, 4, 5.0, 15)
    with pytest.raises(ValueError, match="pass through"):
        model.add_barrier(4, 0, 4, 10, 10, "Brick")
    with pytest.raises(ValueError, match="horizontal or vertical"):
        model.add_barrier(1, 1, 4, 5, 10, "Brick")
    with pytest.raises(ValueError, match="11 and 20"):
        model.add_access_point(8, 8, 2.4, 25)


def test_heatmap_image_dimensions_and_opposite_y_axis() -> None:
    from wifimap.heatmap import signal_to_rgba

    signal = np.full((2, 3), -100.0)
    signal[0, 0] = -20
    rgba = signal_to_rgba(signal)
    assert rgba.shape == (3, 2, 4)
    assert tuple(rgba[2, 0]) == (147, 0, 0, 255)
