"""UBO growth stress test (SC-002, T014).

Creates, draws to, and closes many windows in a single process — the
scenario that triggers unbounded matrix UBO growth under a naive pyglet
dev5+ bump (see spec.md Edge Cases, research.md §1-3). Arcade now owns a
single fixed-size window-block UBO per context (FR-005), so growth should
be impossible by construction; this test is the empirical check.
"""

from __future__ import annotations

import array
import os
import threading
import warnings

os.environ.setdefault("ARCADE_TEST", "True")

import arcade  # noqa: E402
from arcade.gl import Context  # noqa: E402
from arcade.types import Color, LBWH  # noqa: E402

WINDOW_CYCLES = 100


def _current_window_or_none() -> arcade.Window | None:
    """The globally-current window, or None if none is set.

    Used to save/restore global window state around this module's window
    churn, so it doesn't leak a closed window into later tests that rely on
    ``arcade.get_window()`` returning the shared session window (e.g. the
    ``conftest.py`` ``window``/``ctx`` fixtures) — see research.md for the CI
    breakage this caused when that restoration was missing.
    """
    return arcade.get_window() if arcade.window_exists() else None


def _restore_global_state(window: arcade.Window | None) -> None:
    """Restore both pieces of global state this module's window churn can
    leave dangling.

    ``arcade.get_window()``/``set_window()`` is one global (the "current
    window" convenience API). Separately, ``arcade.gl.Context.__init__``
    *unconditionally* calls ``Context.activate(self)`` — a completely
    different, class-level "currently active context" tracker that code like
    ``arcade.gl.geometry.quad_2d()`` reads directly via
    ``Context.active`` (see ``arcade/gl/geometry.py``'s
    ``_get_active_context()``), bypassing ``get_window()`` entirely. Every
    window this module creates overwrites *both* globals; restoring only the
    first one (what an earlier version of this fix did) left ``Context.active``
    pointed at the last, now-closed, stress window for the rest of the test
    session — see research.md for the CI breakage this caused
    (``test_gl_geometry.py``'s ``geo.ctx == ctx`` failures).
    """
    if window is None:
        return
    arcade.set_window(window)
    Context.activate(window.ctx)


def _join_stray_background_threads(timeout: float = 10.0) -> None:
    """Wait for any non-main threads left over from earlier tests.

    At least one example in this suite (``arcade/examples/threaded_loading.py``)
    spawns a non-daemon background thread that calls ``get_window()`` and is
    never joined by ``test_examples.py``. If that straggler is still alive
    when this module's window churn starts, it can call GL functions
    concurrently with — or on the same context as — this test or ones that
    run after it (undefined behavior in OpenGL), corrupting shared state.
    Joining stragglers first, before adding our own churn, makes that
    overlap far less likely, without touching the pre-existing thread-hygiene
    bug in ``threaded_loading.py`` itself (out of scope for this migration).
    """
    for thread in threading.enumerate():
        if thread is not threading.current_thread() and not thread.daemon:
            thread.join(timeout=timeout)


def _draw_rect_on(window: arcade.Window) -> None:
    """Draw a filled rect using ``window``'s own ctx explicitly.

    Deliberately does not use ``arcade.draw_rect_filled()``, which calls the
    module-level ``get_window()`` — this keeps the draw step from depending
    on (or needing to touch) global window state at all, since this module
    already creates and tears down many windows in quick succession.
    """
    rect = LBWH(10, 10, 50, 50)
    ctx = window.ctx
    program = ctx.shape_rectangle_filled_unbuffered_program
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer
    with ctx.enabled(ctx.BLEND):
        program["color"] = Color.from_iterable(arcade.color.BLUE).normalized
        program["shape"] = rect.width, rect.height, 0
        buffer.orphan()
        buffer.write(data=array.array("f", (rect.x, rect.y)))
        geometry.render(program, instances=1)


def test_window_draw_close_cycles_do_not_grow_ubo():
    _join_stray_background_threads()
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
                # arcade.Window.__init__ (and, transitively, ArcadeContext's
                # own __init__) overwrites both of this module's tracked
                # globals internally before this line runs — restore them
                # immediately, so they're only pointed at this iteration's
                # window for as short a time as possible instead of for the
                # whole clear/draw/flip/close sequence.
                _restore_global_state(original_window)

                window.clear(color=arcade.color.AMAZON)
                _draw_rect_on(window)
                window.flip()
                window.close()
    finally:
        _restore_global_state(original_window)

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} window/draw/close cycles:\n"
        + "\n".join(growth_warnings)
    )


def test_window_draw_reset_cycles_do_not_grow_ubo():
    """Repeated ctx.reset() cycles on a single long-lived window (T011)."""
    _join_stray_background_threads()
    original_window = _current_window_or_none()
    window = arcade.Window(
        width=200, height=150, title="stress-reset", vsync=False, antialiasing=False, visible=False
    )
    # Restore both tracked globals immediately (see _restore_global_state) —
    # this test only ever touches its own `window`/`window.ctx` variables
    # directly afterward.
    _restore_global_state(original_window)

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            buffer_ids = set()
            for _ in range(WINDOW_CYCLES):
                window.ctx.reset()
                window.clear(color=arcade.color.AMAZON)
                _draw_rect_on(window)
                window.flip()
                buffer_ids.add(window.ctx._window_block.glo.value)

            assert len(buffer_ids) == 1, (
                f"Expected the window-block UBO to keep a stable identity across "
                f"{WINDOW_CYCLES} reset cycles (no reallocation), but saw "
                f"{len(buffer_ids)} distinct buffer ids: {buffer_ids}"
            )
    finally:
        window.close()
        _restore_global_state(original_window)

    growth_warnings = [
        str(w.message) for w in caught if "Growing UniformBufferObject" in str(w.message)
    ]
    assert not growth_warnings, (
        f"UBO grew unboundedly across {WINDOW_CYCLES} reset cycles:\n"
        + "\n".join(growth_warnings)
    )
