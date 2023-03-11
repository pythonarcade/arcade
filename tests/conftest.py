from pathlib import Path

import arcade
import pytest

PROJECT_ROOT = (Path(__file__).parent.parent).resolve()
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures"
WINDOW = None


def create_window():
    global WINDOW
    if not WINDOW:
        WINDOW = arcade.Window(title="Testing", vsync=False, antialiasing=False)
        WINDOW.set_vsync(False)
    return WINDOW


def prepare_window(window: arcade.Window):
    # Check if someone has been naughty
    if window.has_exit:
        raise RuntimeError("Please do not close the global test window :D")

    window.switch_to()
    ctx = window.ctx
    ctx._atlas = None  # Clear the global atlas
    arcade.cleanup_texture_cache()  # Clear the global texture cache
    window.hide_view()  # Disable views if any is active
    window.dispatch_pending_events()

    # Reset context (various states)
    ctx.reset()
    window.set_vsync(False)
    window.flip()
    window.clear()
    ctx.gc_mode = "context_gc"
    ctx.gc()

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


class Fixtures:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.fixtures_root = FIXTURE_ROOT

    def path(self, path):
        """Get absolute path to a fixture"""
        return self.fixtures_root / Path(path)


@pytest.fixture(scope="session")
def fixtures():
    return Fixtures()
