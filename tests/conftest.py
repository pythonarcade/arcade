import arcade
import pytest

# Reduce the atlas size
arcade.ArcadeContext.atlas_size = 2048, 2048

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
    ctx._default_atlas = None  # Clear the global atlas
    arcade.Texture.cache.clear()
    arcade.Texture.hit_box_cache.clear()

    window.hide_view()  # Disable views if any is active

    # Reset context (various states)
    ctx.reset()
    window.set_vsync(False)
    window.flip()
    window.clear()
    ctx.gc_mode = "context_gc"

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
    try:
        prepare_window(window)
        yield window.ctx
    finally:
        window.flip()


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
    yield window.ctx


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
    try:
        prepare_window(window)
        yield window
    finally:
        window.flip()
