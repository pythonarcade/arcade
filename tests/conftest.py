import gc
import os
from pathlib import Path

if os.environ.get("ARCADE_PYTEST_USE_RUST"):
    import arcade_accelerate  # pyright: ignore [reportMissingImports]
    arcade_accelerate.bootstrap()

import pytest

import arcade
from arcade.texture import default_texture_cache

PROJECT_ROOT = (Path(__file__).parent.parent).resolve()
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures"
arcade.resources.add_resource_handle("fixtures", FIXTURE_ROOT)
WINDOW = None


def create_window():
    global WINDOW
    if not WINDOW:
        WINDOW = arcade.Window(title="Testing", vsync=False, antialiasing=False)
        WINDOW.set_vsync(False)
        # This value is being monkey-patched into the Window class so that tests can identify if we are using
        # arcade-accelerate easily in case they need to disable something when it is enabled.
        WINDOW.using_accelerate = os.environ.get("ARCADE_PYTEST_USE_RUST")  # pyright: ignore
    return WINDOW


def prepare_window(window: arcade.Window):
    # Check if someone has been naughty
    if window.has_exit:
        raise RuntimeError("Please do not close the global test window :D")

    window.switch_to()
    ctx = window.ctx
    ctx._atlas = None  # Clear the global atlas
    default_texture_cache.flush()  # Clear the global/default texture cache
    window.hide_view()  # Disable views if any is active
    window.dispatch_pending_events()

    # Reset context (various states)
    ctx.reset()
    window.set_vsync(False)
    window.flip()
    window.clear()
    ctx.gc_mode = "context_gc"
    ctx.gc()
    gc.collect()

    # Ensure no old functions are lingering
    window.on_draw = lambda: None
    window.on_update = lambda dt: None


@pytest.fixture(scope="function")
def ctx():
    """
    Per function context.

    The main purpose of this is to ensure that the context is reset
    between each test function and the window is flipped.
    """
    window = create_window()
    arcade.set_window(window)
    prepare_window(window)
    return window.ctx


@pytest.fixture(scope="session")
def ctx_static():
    """
    Context that is shared between tests
    This is the same global context.
    Module scoped fixtures can inject this context.
    """
    window = create_window()
    arcade.set_window(window)
    prepare_window(window)
    return window.ctx


@pytest.fixture(scope="function")
def window():
    """
    Global window that is shared between tests.

    This just returns the global window, but ensures that the context
    is reset between each test function and the window is flipped
    between each test function.
    """
    window = create_window()
    arcade.set_window(window)
    prepare_window(window)
    return window
