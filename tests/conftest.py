import os
from contextlib import contextmanager
from pathlib import Path
import gc

if os.environ.get("ARCADE_PYTEST_USE_RUST"):
    import arcade_accelerate # pyright: ignore [reportMissingImports]
    arcade_accelerate.bootstrap()

import pytest

import arcade

PROJECT_ROOT = (Path(__file__).parent.parent).resolve()
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures"
arcade.resources.add_resource_handle("fixtures", FIXTURE_ROOT)
WINDOW = None


def create_window(width=800, height=600, caption="Testing", **kwargs):
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


# These are tools for integration tests were examples are run
# creating windows and such. The global test window needs to
# be injected somehow. In addition we need to initialize a
# window subclass on an existing window instance.
class WindowTools:
    """
    Tools for patching windows in integration tests.
    Might cause bleeding from the eyes while reading.
    """

    @contextmanager
    def patch_window_as_global_window_subclass(self, window_cls):
        """Hack in the class as the subclass of the global window instance"""
        # Oh boy here we go .. :O
        default_members = None
        try:
            window = create_window()
            arcade.set_window(window)

            # The arcade window initializer must not be called
            arcade_init = arcade.Window.__init__
            example_init = window_cls.__init__
            def dummy_arcade_init(self, *args, **kwargs):
                arcade.set_window(window)
            def dummy_example_init(self, *args, **kwargs):                
                def dummy_func(self, *args, **kwargs):
                    pass
                window_cls.__init__ = dummy_func
                example_init(window, *args, **kwargs)

            arcade.Window.__init__ = dummy_arcade_init
            window_cls.__init__ = dummy_example_init
            window.__class__ = window_cls  # Make subclass of the instance
            default_members = set(window.__dict__.keys())
            yield window
        finally:
            arcade.Window.__init__ = arcade_init
            window_cls.__init__ = example_init
            window.__class__ = arcade.Window

            # Delete lingering members
            if default_members:
                new_members = list(window.__dict__.keys())
                for member in new_members:
                    if member not in default_members:
                        del window.__dict__[member]



@pytest.fixture(scope="function")
def window_tools():
    """Monkey patch the open_window function and return a WindowTools instance."""
    # Monkey patch the open_window function
    def _create_window(width=800, height=800, caption="Test", **kwargs):
        window = create_window()
        arcade.set_window(window)
        prepare_window(window)
        window.set_size(width, height)
        window.set_caption(caption)
        return window

    arcade.open_window = _create_window 
    return WindowTools()
