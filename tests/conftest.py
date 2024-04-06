import gc
import os
import sys
from contextlib import contextmanager
from pathlib import Path

if os.environ.get("ARCADE_PYTEST_USE_RUST"):
    import arcade_accelerate  # pyright: ignore [reportMissingImports]
    arcade_accelerate.bootstrap()

import pytest

import arcade

PROJECT_ROOT = (Path(__file__).parent.parent).resolve()
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures"
arcade.resources.add_resource_handle("fixtures", FIXTURE_ROOT)
REAL_WINDOW_CLASS = arcade.Window
WINDOW = None


def create_window(width=800, height=600, caption="Testing", **kwargs):
    global WINDOW
    if not WINDOW:
        WINDOW = REAL_WINDOW_CLASS(title="Testing", vsync=False, antialiasing=False)
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
    if window.get_size() < (800, 600):
        window.set_size(800, 600)

    ctx = window.ctx
    ctx._atlas = None  # Clear the global atlas
    arcade.cleanup_texture_cache()  # Clear the global texture cache
    window.hide_view()  # Disable views if any is active
    window.dispatch_pending_events()
    try:
        arcade.disable_timings()
    except Exception:
        pass

    # Reset context (various states)
    ctx.reset()
    window.set_vsync(False)
    window.flip()
    window.clear()
    window.default_camera.use()
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


class WindowProxy:
    """Fake window extended by integration tests"""

    def __init__(self, width=800, height=600, caption="Test Window", *args, **kwargs):
        self.window = create_window()
        arcade.set_window(self)
        prepare_window(self.window)
        if caption:
            self.window.set_caption(caption)
        if width and height:
            self.window.set_size(width, height)
            self.window.default_camera.use()

        self._update_rate = 60

    @property
    def ctx(self):
        return self.window.ctx

    @property
    def width(self):
        return self.window.width

    @property
    def height(self):
        return self.window.height

    @property
    def size(self):
        return self.window.size

    @property
    def aspect_ratio(self):
        return self.window.aspect_ratio

    @property
    def mouse(self):
        return self.window.mouse
    
    @property
    def keyboard(self):
        return self.window.keyboard

    def current_view(self):
        return self.window.current_view

    @property
    def background_color(self):
        return self.window.background_color

    @background_color.setter
    def background_color(self, color):
        self.window.background_color = color

    def clear(self, *args, **kwargs):
        return self.window.clear(*args, **kwargs)

    def flip(self):
        if self.window.has_exit:
            return
        return self.window.flip()

    def on_draw(self):
        return self.window.on_draw()
    
    def on_update(self, dt):
        return self.window.on_update(dt)

    def show_view(self, view):
        return self.window.show_view(view)

    def hide_view(self):
        return self.window.hide_view()

    def get_size(self):
        return self.window.get_size()

    def set_size(self, width, height):
        self.window.set_size(width, height)

    def get_pixel_ratio(self):
        return self.window.get_pixel_ratio()

    def set_mouse_visible(self, visible):
        self.window.set_mouse_visible(visible)

    def center_window(self):
        self.window.center_window()

    def set_vsync(self, vsync):
        self.window.set_vsync(vsync)

    @property
    def default_camera(self):
        """
        Provides a reference to the default arcade camera.
        Automatically sets projection and view to the size
        of the screen. Good for resetting the screen.
        """
        return self.window.default_camera

    def use(self):
        self.window.use()

    def push_handlers(self, *handlers):
        self.window.push_handlers(*handlers)

    def remove_handlers(self, *handlers):
        self.window.remove_handlers(*handlers)

    def run(self):
        self.window.run()


@pytest.fixture(scope="function")
def window_proxy():
    """Monkey patch the open_window function and return a WindowTools instance."""
    _window = arcade.Window
    arcade.Window = WindowProxy

    _open_window = arcade.open_window
    def open_window(*args, **kwargs):
        return create_window(*args, **kwargs)
    arcade.open_window = open_window

    yield None
    arcade.Window = _window
    arcade.open_window = _open_window
