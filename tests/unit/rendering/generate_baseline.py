"""One-off script: capture pre-migration (pyglet 3.0.dev3) baseline PNGs for
the reference-image comparison harness (SC-003, FR-011, T001).

This MUST be run before the pyglet dependency pin is bumped to 3.0.dev6 —
it captures the "known-good" ground truth that
``test_dev6_reference_images.py`` compares dev6's output against.

Usage (from the repository root, with pyglet 3.0.dev3 still installed):

    python tests/unit/rendering/generate_baseline.py

Re-run identically after the migration by importing the same
``tests.unit.rendering.scenes`` module used here — see
``test_dev6_reference_images.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ["ARCADE_TEST"] = "True"

import arcade  # noqa: E402

from tests.unit.rendering.scenes import SCENE_HEIGHT, SCENE_WIDTH, SCENES  # noqa: E402

BASELINE_DIR = Path(__file__).parent / "baseline"


def main() -> None:
    arcade.resources.load_kenney_fonts()
    window = arcade.Window(
        width=SCENE_WIDTH,
        height=SCENE_HEIGHT,
        title="Baseline capture",
        vsync=False,
        antialiasing=False,
    )
    arcade.set_window(window)

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    for name, render in SCENES.items():
        render(window)
        image = arcade.get_image()
        out_path = BASELINE_DIR / f"{name}.png"
        image.save(out_path)
        print(f"Saved {out_path}")

    window.close()


if __name__ == "__main__":
    main()
