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


def _current_window_or_none() -> arcade.Window | None:
    """The globally-current window, or None if none is set.

    Used to save/restore global window state around this module's window
    churn, so it doesn't leak a closed window into later tests that rely on
    ``arcade.get_window()`` returning the shared session window (e.g. the
    ``conftest.py`` ``window``/``ctx`` fixtures, or a background thread
    spawned by an earlier example test) — see research.md for the CI
    breakage this caused when that restoration was missing.
    """
    return arcade.get_window() if arcade.window_exists() else None


def test_window_draw_close_cycles_do_not_grow_ubo():
    original_window = _current_window_or_none()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            for i in range(WINDOW_CYCLES):
                window = arcade.Window(
                    width=200,
                    height=150,
                    title=f"stress-{i}",
                    vsync=False,
                    antialiasing=False,
                    visible=False,
                )
                arcade.set_window(window)
                window.clear(color=arcade.color.AMAZON)
                arcade.draw_rect_filled(LBWH(10, 10, 50, 50), arcade.color.BLUE)
                window.flip()
                window.close()
    finally:
        if original_window is not None:
            arcade.set_window(original_window)

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} window/draw/close cycles:\n"
        + "\n".join(growth_warnings)
    )


def test_window_draw_reset_cycles_do_not_grow_ubo():
    """Repeated ctx.reset() cycles on a single long-lived window (T011)."""
    original_window = _current_window_or_none()
    window = arcade.Window(
        width=200, height=150, title="stress-reset", vsync=False, antialiasing=False, visible=False
    )
    try:
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
    finally:
        window.close()
        if original_window is not None:
            arcade.set_window(original_window)

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} reset cycles:\n"
        + "\n".join(growth_warnings)
    )
