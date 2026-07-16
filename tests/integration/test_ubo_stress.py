"""UBO growth stress test (SC-002, T014).

Creates, draws to, and closes many windows in a single process — the
scenario that triggers unbounded matrix UBO growth under a naive pyglet
dev5+ bump (see spec.md Edge Cases, research.md §1-3). Arcade now owns a
single fixed-size window-block UBO per context (FR-005), so growth should
be impossible by construction; this test is the empirical check.
"""

from __future__ import annotations

import os
import warnings

os.environ.setdefault("ARCADE_TEST", "True")

import arcade  # noqa: E402
from arcade.types import LBWH  # noqa: E402

WINDOW_CYCLES = 100


def test_window_draw_close_cycles_do_not_grow_ubo():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        for i in range(WINDOW_CYCLES):
            window = arcade.Window(
                width=200, height=150, title=f"stress-{i}", vsync=False, antialiasing=False
            )
            arcade.set_window(window)
            window.clear(color=arcade.color.AMAZON)
            arcade.draw_rect_filled(LBWH(10, 10, 50, 50), arcade.color.BLUE)
            window.flip()
            window.close()

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} window/draw/close cycles:\n"
        + "\n".join(growth_warnings)
    )


def test_window_draw_reset_cycles_do_not_grow_ubo():
    """Repeated ctx.reset() cycles on a single long-lived window (T011)."""
    window = arcade.Window(width=200, height=150, title="stress-reset", vsync=False, antialiasing=False)
    arcade.set_window(window)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        buffer_ids = set()
        for _ in range(WINDOW_CYCLES):
            window.ctx.reset()
            window.clear(color=arcade.color.AMAZON)
            arcade.draw_rect_filled(LBWH(10, 10, 50, 50), arcade.color.BLUE)
            window.flip()
            buffer_ids.add(window.ctx._window_block.glo.value)

        assert len(buffer_ids) == 1, (
            f"Expected the window-block UBO to keep a stable identity across "
            f"{WINDOW_CYCLES} reset cycles (no reallocation), but saw "
            f"{len(buffer_ids)} distinct buffer ids: {buffer_ids}"
        )

    window.close()

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} reset cycles:\n"
        + "\n".join(growth_warnings)
    )
