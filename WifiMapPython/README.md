# WifiMap (Python)

Cross-platform desktop rewrite of the Java WifiMap assignment. It models Wi-Fi
access points and axis-aligned barriers, calculates and displays a signal
heatmap, supports direct map editing, and saves maps as JSON.

## Requirements

- Python 3.11 or newer
- Linux or Windows

The GUI uses PySide6 (Qt for Python); NumPy vectorizes signal calculations.
There is no Java or Maven dependency for this version.

## Install and run

### Linux

```bash
cd WifiMapPython
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
wifimap
```

### Windows (PowerShell)

```powershell
cd WifiMapPython
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
wifimap
```

You can also launch from the source directory with `python -m wifimap.window`.

## Features

- Create, resize, and clear maps up to 500 × 500 cells.
- Add, edit, move, and delete access points (2.4/5 GHz, 11–20 dBm).
- Add, edit, move, and delete horizontal or vertical barriers with a material
  and thickness. Barriers cannot pass through an access point.
- Display the heatmap, coordinate grid, signal legend, and contextual tooltips.
- Draw barriers by dragging or by clicking start and endpoint; move access
  points and barriers directly on the map with a live drag preview.
- Recalculate the signal heatmap during a drag at a throttled rate; outdated
  preview calculations are discarded, and the final full map is calculated
  after the move is committed.
- Zoom with the mouse wheel from a full-map overview to close detail, or use
  **Fit map to view** (`Ctrl+0`) to show the entire map, including 500 × 500.
- Optionally snap editing to a 10 m grid.
- Undo/redo edits; save and load versioned JSON map files; export a PNG image.
- Copy and paste one selected access point or barrier with **Ctrl+C**/**Ctrl+V**;
  paste offsets the source by 5 m on each axis, reversing an axis offset when
  needed to keep the duplicate inside the map.

Signal computation and Qt rendering are separated. NumPy computes an entire
map per access point using broadcast array operations, and recalculation runs
in a worker thread so the window remains responsive.

## Tests

```bash
python -m pytest
```
