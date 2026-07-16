"""Reference-image comparison harness (SC-003, FR-011, T013).

Re-renders the same scenes captured pre-migration in
``baseline/*.png`` (see ``generate_baseline.py``) and asserts the rendered
output is within the SC-003 tolerance of the pre-migration (pyglet
3.0.dev3) baseline.
"""

from __future__ import annotations

from pathlib import Path

import PIL.Image
import pytest

import arcade
from tests.unit.rendering.image_compare import compare_images
from tests.unit.rendering.scenes import SCENES

BASELINE_DIR = Path(__file__).parent / "baseline"


@pytest.mark.parametrize("scene_name", sorted(SCENES.keys()))
def test_scene_matches_baseline(window: arcade.Window, scene_name: str):
    baseline_path = BASELINE_DIR / f"{scene_name}.png"
    if not baseline_path.exists():
        pytest.skip(
            f"No baseline image for scene {scene_name!r} at {baseline_path} — "
            "run tests/unit/rendering/generate_baseline.py on a known-good "
            "pyglet build to (re)create it."
        )

    render = SCENES[scene_name]
    render(window)
    actual = arcade.get_image()
    expected = PIL.Image.open(baseline_path)

    result = compare_images(actual, expected)
    assert result.within_tolerance, (
        f"Scene {scene_name!r} deviates from its pre-migration baseline "
        f"beyond the SC-003 tolerance: {result}. Per FR-011, investigate "
        "before regenerating the baseline — only regenerate for a confirmed "
        "benign, pyglet-driven, documented difference."
    )

    window.default_camera.use()
