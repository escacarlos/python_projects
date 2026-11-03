import argparse
from pathlib import Path

from python_engine.engine import Game


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Python 2D game engine")
    parser.add_argument(
        "--scene",
        type=Path,
        default=Path("assets/levels/level1.json"),
        help="Path to a JSON scene file",
    )
    args = parser.parse_args()
    Game(args.scene.resolve()).run()


if __name__ == "__main__":
    main()
