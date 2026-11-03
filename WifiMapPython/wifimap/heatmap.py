import numpy as np


_LEVELS = np.array([-100, -90, -80, -70, -60, -50, -40, -30, -20], dtype=float)
_COLORS = np.array(
    [
        [0, 0, 100],
        [0, 0, 255],
        [0, 125, 255],
        [0, 255, 255],
        [0, 255, 0],
        [254, 252, 0],
        [254, 130, 0],
        [255, 5, 2],
        [147, 0, 0],
    ],
    dtype=np.uint8,
)


def signal_to_rgba(signal: np.ndarray) -> np.ndarray:
    """Interpolate the Java heatmap palette and return a top-down RGBA image."""
    clipped = np.clip(signal, _LEVELS[0], _LEVELS[-1])
    lower = np.clip(np.searchsorted(_LEVELS, clipped, side="right") - 1, 0, len(_LEVELS) - 2)
    fraction = (clipped - _LEVELS[lower]) / (_LEVELS[lower + 1] - _LEVELS[lower])
    rgb = _COLORS[lower] * (1.0 - fraction[..., None]) + _COLORS[lower + 1] * fraction[..., None]
    rgba = np.empty((*signal.shape, 4), dtype=np.uint8)
    rgba[..., :3] = rgb.astype(np.uint8)
    rgba[..., 3] = 255
    return np.flip(rgba.transpose(1, 0, 2), axis=0).copy()
