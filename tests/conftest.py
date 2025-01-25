from __future__ import annotations

import os
from pathlib import Path

os.environ["ARCADE_TEST"] = "True"


if os.environ.get("ARCADE_PYTEST_USE_RUST"):
    import arcade_accelerate  # pyright: ignore [reportMissingImports]

    arcade_accelerate.bootstrap()

import pytest
import PIL.Image
from pyglet.math import Mat4

import arcade
from arcade.clock import GLOBAL_CLOCK, GLOBAL_FIXED_CLOCK
from arcade import Rect, LBWH
from arcade import gl
# from arcade.texture import default_texture_cache

PROJECT_ROOT = (Path(__file__).parent.parent).resolve()
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures"
arcade.resources.add_resource_handle("fixtures", FIXTURE_ROOT)
REAL_WINDOW_CLASS = arcade.Window
WINDOW = None
OFFSCREEN = None

arcade.resources.load_kenney_fonts()


def make_window_caption(request=None, prefix="Testing", sep=" - ") -> str:
    """Centralizes test name customization.

    It helps with:

    1. Tests scoped as something other than function (can't use test_name fixture)
    2. Local (non-CI) temp modifications of inter-test behavior
    """
    parts = [prefix]
    if request is not None:
        parts.append(request.node.name)

    return sep.join(parts)


def create_window(width=1280, height=720, caption="Testing", **kwargs):
    global WINDOW
    if not WINDOW:
        WINDOW = REAL_WINDOW_CLASS(
            width=width, height=height, title=caption, vsync=False, antialiasing=False
        )
        WINDOW.set_vsync(False)
        # This value is being monkey-patched into the Window class so that tests can identify if we are using
        # arcade-accelerate easily in case they need to disable something when it is enabled.
        WINDOW.using_accelerate = os.environ.get("ARCADE_PYTEST_USE_RUST")  # pyright: ignore
    return WINDOW


def prepare_window(window: arcade.Window, caption: str | None = None):
    # Check if someone has been naughty
    if window.has_exit:
        raise RuntimeError("Please do not close the global test window :D")

    window.switch_to()
    if window.get_size() < (800, 600):
        window.set_size(800, 600)
    if caption:
        window.set_caption(caption)

    ctx = window.ctx
    # ctx._atlas = None  # Clear the global atlas
    # default_texture_cache.flush()  # Clear the global/default texture cache
    arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.LINEAR, gl.LINEAR
    window._start_finish_render_data = None
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
    # gc.collect(1)

    # Ensure no old functions are lingering
    window.on_draw = lambda: None
    window.on_update = lambda dt: None


@pytest.fixture
def test_name(request):
    return make_window_caption(request)


@pytest.fixture(scope="function")
def ctx(test_name):
    """
    Per function context.

    The main purpose of this is to ensure that the context is reset
    between each test function and the window is flipped.
    """
    window = create_window()
    arcade.set_window(window)
    prepare_window(window, caption=test_name)
    return window.ctx


@pytest.fixture(scope="session")
def ctx_static(request):
    """
    Context that is shared between tests
    This is the same global context.
    Module scoped fixtures can inject this context.
    """
    window = create_window()
    arcade.set_window(window)
    # Can't use the test_name fixture here:
    # 1. This fixture is session scoped
    # 2. test_name is function scoped
    prepare_window(window, caption=make_window_caption(request))
    return window.ctx


@pytest.fixture(scope="function")
def window(test_name):
    """
    Global window that is shared between tests.

    This just returns the global window, but ensures that the context
    is reset between each test function and the window is flipped
    between each test function.
    """
    window = create_window()
    arcade.set_window(window)
    prepare_window(window, caption=test_name)
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

    @size.setter
    def size(self, size):
        self.window.size = size

    @property
    def center_x(self):
        return self.window.center_x

    @property
    def center_y(self):
        return self.window.center_y

    @property
    def center(self):
        return self.window.center

    @property
    def rect(self):
        return self.window.rect

    @property
    def aspect_ratio(self):
        return self.window.aspect_ratio

    @property
    def projection(self):
        return self.window.projection

    @projection.setter
    def projection(self, projection):
        self.window.projection = projection

    @property
    def viewport(self):
        return self.window.viewport

    @viewport.setter
    def viewport(self, viewport):
        self.window.viewport = viewport

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

    @property
    def current_camera(self):
        return self.window.current_camera

    @property
    def _start_finish_render_data(self):
        return self.window._start_finish_render_data

    @_start_finish_render_data.setter
    def _start_finish_render_data(self, data):
        self.window._start_finish_render_data = data

    @current_camera.setter
    def current_camera(self, new_camera):
        self.window.current_camera = new_camera

    def close(self):
        pass

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

    def on_resize(self, width, height):
        return self.window.on_resize(width, height)

    def on_key_press(self, symbol, modifiers):
        return self.window.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        return self.window.on_key_release(symbol, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        return self.window.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        return self.window.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        return self.window.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return self.window.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def show_view(self, view):
        return self.window.show_view(view)

    def hide_view(self):
        return self.window.hide_view()

    def get_size(self):
        return self.window.get_size()

    def set_size(self, width, height):
        self.window.set_size(width, height)

    def get_framebuffer_size(self):
        return self.window.get_framebuffer_size()

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
        Provides a reference to the default Arcade camera.
        Automatically sets projection and view to the size
        of the screen. Good for resetting the screen.
        """
        return self.window.default_camera

    def use(self):
        self.window.use()

    def push_handlers(self, *args, **kwargs):
        self.window.push_handlers(*args, **kwargs)

    def remove_handlers(self, *args, **kwargs):
        self.window.remove_handlers(*args, **kwargs)

    def run(self):
        self.window.run()

    # --- CLOCK ALIASES ---
    @property
    def time(self):
        return GLOBAL_CLOCK.time

    @property
    def delta_time(self):
        return GLOBAL_CLOCK.delta_time

    @property
    def fixed_time(self):
        return GLOBAL_FIXED_CLOCK.time

    @property
    def fixed_delta_time(self) -> float:
        return self.window._fixed_rate


@pytest.fixture(scope="function")
def window_proxy():
    """Monkey patch the open_window function and return a WindowTools instance."""
    _window = arcade.Window
    arcade.Window = WindowProxy

    _open_window = arcade.open_window

    def open_window(*args, **kwargs):
        window = create_window(*args, **kwargs)
        prepare_window(window)
        return window

    arcade.open_window = open_window

    yield None
    arcade.Window = _window
    arcade.open_window = _open_window
    WINDOW.flip()


# --- Fixtures for offscreen rendering
class Offscreen:
    def __init__(self):
        self.ctx = WINDOW.ctx
        self.texture = self.ctx.texture((1280, 720), components=4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def use(self):
        """Use the offscreen buffer"""
        self.fbo.use()
        WINDOW.projection = Mat4.orthogonal_projection(0, 1280, 0, 720, -100, 100)

    def clear(self):
        """Clear the offscreen buffer"""
        self.fbo.clear()

    def get_image(self) -> PIL.Image.Image:
        """Get the offscreen buffer as an image"""
        region = LBWH(0, 0, 1280, 720)
        return self.read_region_image(region)

    def read_pixel(self, x, y, components=3) -> tuple[int, int, int, int] | tuple[int, int, int]:
        """Read a single RGBA pixel from the offscreen buffer"""
        data = self.fbo.read(components=4, viewport=(x, y, 1, 1))
        return (
            int.from_bytes(data[0:4], "little"),
            int.from_bytes(data[4:8], "little"),
            int.from_bytes(data[8:12], "little"),
            int.from_bytes(data[12:16], "little"),
        )

    def read_region(self, rect: Rect) -> list[tuple[int, int, int, int]]:
        """Read a region of RGBA pixels from the offscreen buffer"""
        data = self.fbo.read(
            components=4, viewport=(rect.left, rect.bottom, rect.width, rect.height)
        )
        return [
            (
                int.from_bytes(data[i : i + 4], "little"),
                int.from_bytes(data[i + 4 : i + 8], "little"),
                int.from_bytes(data[i + 8 : i + 12], "little"),
                int.from_bytes(data[i + 12 : i + 16], "little"),
            )
            for i in range(0, len(data), 16)
        ]

    def read_region_bytes(self, rect: Rect, components=3) -> bytes:
        """Read a region of RGBA pixels from the offscreen buffer as bytes"""
        return self.fbo.read(
            components=components,
            viewport=(rect.left, rect.bottom, rect.width, rect.height),
        )

    def read_region_image(self, rect: Rect, components=3) -> PIL.Image.Image:
        im = PIL.Image.frombytes(
            "RGBA" if components == 4 else "RGB",
            (int(rect.width), int(rect.height)),
            self.read_region_bytes(rect, components=components),
        )
        return im.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)

    def assert_images_almost_equal(self, image1: PIL.Image.Image, image2: PIL.Image.Image, abs=2):
        """Assert that two images are almost equal"""
        assert image1.size == image2.size, f"{image1.size} != {image2.size}"
        assert image1.mode == image2.mode, f"{image1.mode} != {image2.mode}"
        assert image1.tobytes() == pytest.approx(image2.tobytes(), abs=abs)


@pytest.fixture(scope="function")
def offscreen(test_name):
    """
    Offscreen rendering tools.

    A global offscreen 720p target that can be used for testing
    """
    global OFFSCREEN

    window = create_window()
    arcade.set_window(window)
    prepare_window(window, caption=test_name)

    if OFFSCREEN is None:
        OFFSCREEN = Offscreen()

    OFFSCREEN.clear()
    OFFSCREEN.use()
    yield OFFSCREEN
    window.use()
