# Python runtime

Create and activate a project-local virtual environment, then install
Pygame Community Edition (the `pygame`-compatible package with current Python
support) and start the current JSON scene:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

To start the Desert level instead:

```sh
python main.py --scene assets/levels/level2.json
```

The `.venv` directory is ignored by Git. Packages installed after activation
belong to this project environment, not the OS Python installation. Run
`deactivate` to leave the environment.

Use the arrow keys to move, Space to fire, F1 to show collision/debug
information, and Escape to quit.

`assets/levels/level1.json` contains the scene's assets, tilemap grid, entities,
and component values. Tile cells are two-digit atlas coordinates: the first
digit is the atlas row and the second is its column. Entity behavior is selected
by a Python behavior name, rather than executable code stored in the scene.
Random numeric values can be expressed as `{"random": [minimum, maximum]}`.

The scene is ordinary JSON data that can be edited with a text editor today.
When an editor is added, it can load this same structure, update the tile grid
and entity/component values, and write the result back to JSON when the user
saves. The editor does not exist yet, so scene changes are not currently saved
by the runtime.
