"""
The main window class that all object-oriented applications should
derive from.
"""
import logging
import time
from numbers import Number
from typing import Tuple, Optional

import pyglet
import pyglet.gl as gl

import arcade
from arcade import get_display_size
from arcade import get_viewport
from arcade import set_viewport
from arcade import set_window
from arcade.context import ArcadeContext
from arcade.arcade_types import Color

LOG = logging.getLogger(__name__)

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4

_window: 'Window'


def get_screens():
    """
    Return a list of screens. So for a two-monitor setup, this should return
    a list of two screens. Can be used with arcade.Window to select which
    window we full-screen on.
    """
    display = pyglet.canvas.get_display()
    return display.get_screens()


class NoOpenGLException(Exception):
    """
    Exception when we can't get an OpenGL 3.3+ context
    """
    pass


class Window(pyglet.window.Window):
    """
    The Window class forms the basis of most advanced games that use Arcade.
    It represents a window on the screen, and manages events.
    """

    def __init__(self,
                 width: int = 800,
                 height: int = 600,
                 title: str = 'Arcade Window',
                 fullscreen: bool = False,
                 resizable: bool = False,
                 update_rate: Optional[float] = 1 / 60,
                 antialiasing: bool = True,
                 gl_version: Tuple[int, int] = (3, 3),
                 screen: pyglet.canvas.Screen = None):
        """
        Construct a new window

        :param int width: Window width
        :param int height: Window height
        :param str title: Title (appears in title bar)
        :param bool fullscreen: Should this be full screen?
        :param bool resizable: Can the user resize the window?
        :param float update_rate: How frequently to update the window.
        :param bool antialiasing: Should OpenGL's anti-aliasing be enabled?
        :param Tuple[int,int] gl_version: What OpenGL version to request. This is ``(3, 3)`` by default
                                           and can be overridden when using more advanced OpenGL features.
        """
        if antialiasing:
            config = pyglet.gl.Config(major_version=gl_version[0],
                                      minor_version=gl_version[1],
                                      double_buffer=True,
                                      sample_buffers=1,
                                      samples=4)
        else:
            config = pyglet.gl.Config(major_version=3,
                                      minor_version=3,
                                      double_buffer=True)

        try:
            super().__init__(width=width, height=height, caption=title,
                             resizable=resizable, config=config, vsync=False)
            self.register_event_type('update')
            self.register_event_type('on_update')
        except pyglet.window.NoSuchConfigException:
            raise NoOpenGLException("Unable to create an OpenGL 3.3+ context. "
                                    "Check to make sure your system supports OpenGL 3.3 or higher.")

        if antialiasing:
            try:
                gl.glEnable(gl.GL_MULTISAMPLE_ARB)
            except pyglet.gl.GLException:
                print("Warning: Anti-aliasing not supported on this computer.")

        if update_rate:
            from pyglet import compat_platform
            if compat_platform == 'darwin' or compat_platform == 'linux':
                # Set vsync to false, or we'll be limited to a 1/30 sec update rate possibly
                self.context.set_vsync(False)
            self.set_update_rate(update_rate)

        super().set_fullscreen(fullscreen, screen)
        # This used to be necessary on Linux, but no longer appears to be.
        # With Pyglet 2.0+, setting this to false will not allow the screen to
        # update. It does, however, cause flickering if creating a window that
        # isn't derived from the Window class.
        # self.invalid = False
        set_window(self)

        self._current_view: Optional[View] = None
        self.textbox_time = 0.0
        self.key: Optional[int] = None
        self.ui_manager = arcade.experimental.gui.UIManager(self)

        self._ctx: ArcadeContext = ArcadeContext(self)
        set_viewport(0, self.width - 1, 0, self.height - 1)

        self._background_color: Color = (0, 0, 0, 0)

        # Required for transparency
        self._ctx.enable(self.ctx.BLEND)
        self._ctx.blend_func = self.ctx.BLEND_DEFAULT

    @property
    def current_view(self):
        """
        This property returns the current view being shown.
        To set a different view, call the
        :py:meth:`arcade.Window.show_view` method.
        """
        return self._current_view

    @property
    def ctx(self) -> ArcadeContext:
        """
        The OpenGL context for this window.

        :type: :py:class:`arcade.ArcadeContext`
        """
        return self._ctx

    def clear(self):
        """Clears the window with the configured background color
        set through :py:attr:`arcade.Window.background_color`.
        """
        self.ctx.screen.clear(self.background_color)

    @property
    def background_color(self):
        """Get or set the background color for this window.

        :type: Color
        """
        return self._background_color

    @background_color.setter
    def background_color(self, value: Color):
        self._background_color = value

    def close(self):
        """ Close the Window. """
        super().close()
        pyglet.clock.unschedule(self._dispatch_updates)

    def set_fullscreen(self, fullscreen=True, screen=None, mode=None,
                       width=None, height=None):
        """
        Set if we are full screen or not.

        :param bool fullscreen:
        :param screen:
        :param mode:
        :param int width:
        :param int height:
        """
        super().set_fullscreen(fullscreen, screen, mode, width, height)

    def center_window(self):
        """
        Center the window on the screen.
        """
        # Get the display screen using pyglet
        screen_width, screen_height = get_display_size()

        window_width, window_height = self.get_size()
        # Center the window
        self.set_location((screen_width - window_width) // 2, (screen_height - window_height) // 2)

    def update(self, delta_time: float):
        """
        Move everything. For better consistency in naming, use ``on_update`` instead.

        :param float delta_time: Time interval since the last time the function was called in seconds.

        """
        pass

    def on_update(self, delta_time: float):
        """
        Move everything. Perform collision checks. Do all the game logic here.

        :param float delta_time: Time interval since the last time the function was called.

        """
        pass

    def _dispatch_updates(self, delta_time: float):
        self.dispatch_event('update', delta_time)
        self.dispatch_event('on_update', delta_time)

    def set_update_rate(self, rate: float):
        """
        Set how often the screen should be updated.
        For example, self.set_update_rate(1 / 60) will set the update rate to 60 fps

        :param float rate: Update frequency in seconds
        """
        pyglet.clock.unschedule(self._dispatch_updates)
        pyglet.clock.schedule_interval(self._dispatch_updates, rate)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """
        Override this function to add mouse functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        """
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of the mouse
        :param float y: y position of the mouse
        :param int button: What button was hit. One of:
                           arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT,
                           arcade.MOUSE_BUTTON_MIDDLE
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        :param int buttons: Which button is pressed
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x:
        :param float y:
        :param int button:
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """
        User moves the scroll wheel.

        :param int x:
        :param int y:
        :param int scroll_x:
        :param int scroll_y:
        """
        pass

    def set_mouse_visible(self, visible: bool = True):
        """
        If true, user can see the mouse cursor while it is over the window. Set false,
        the mouse is not visible. Default is true.

        :param bool visible:
        """
        super().set_mouse_visible(visible)

    def on_key_press(self, symbol: int, modifiers: int):
        """
        Override this function to add key press functionality.

        :param int symbol: Key that was hit
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        try:
            self.key = symbol
        except AttributeError:
            pass

    def on_key_release(self, symbol: int, modifiers: int):
        """
        Override this function to add key release functionality.

        :param int symbol: Key that was hit
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        try:
            self.key = None
        except AttributeError:
            pass

    def on_draw(self):
        """
        Override this function to add your custom drawing code.
        """
        pass

    def on_resize(self, width: float, height: float):
        """
        Override this function to add custom code to be called any time the window
        is resized. The only responsibility here is to update the viewport.

        :param float width: New width
        :param float height: New height
        """
        try:
            original_viewport = self.get_viewport()
        except Exception as ex:
            print("Error getting viewport:", ex)
            return

        # unscaled_viewport = self.get_viewport_size()
        # scaling = unscaled_viewport[0] / width

        self.set_viewport(original_viewport[0],
                          original_viewport[0] + width,
                          original_viewport[2],
                          original_viewport[2] + height)

    def set_min_size(self, width: float, height: float):
        """ Wrap the Pyglet window call to set minimum size

        :param float width: width in pixels.
        :param float height: height in pixels.
        """

        if self._resizable:
            super().set_minimum_size(width, height)
        else:
            raise ValueError('Cannot set min size on non-resizable window')

    def set_max_size(self, width: float, height: float):
        """ Wrap the Pyglet window call to set maximum size

        :param float width: width in pixels.
        :param float height: height in pixels.
        :Raises ValueError:

        """

        if self._resizable:
            super().set_maximum_size(width, height)
        else:
            raise ValueError('Cannot set max size on non-resizable window')

    def set_size(self, width: float, height: float):
        """
        Ignore the resizable flag and set the size

        :param float width:
        :param float height:
        """

        super().set_size(width, height)

    def get_size(self) -> Tuple[int, int]:
        """
        Get the size of the window.

        :returns: (width, height)
        """

        return super().get_size()

    def get_location(self) -> Tuple[int, int]:
        """
        Return the X/Y coordinates of the window

        :returns: x, y of window location
        """

        return super().get_location()

    def set_visible(self, visible=True):
        """
        Set if the window is visible or not. Normally, a program's window is visible.

        :param bool visible:
        """
        super().set_visible(visible)

    # noinspection PyMethodMayBeStatic
    def set_viewport(self, left: float, right: float, bottom: float, top: float):
        """
        Set the viewport. (What coordinates we can see.
        Used to scale and/or scroll the screen.)

        :param Number left:
        :param Number right:
        :param Number bottom:
        :param Number top:
        """
        set_viewport(left, right, bottom, top)

    # noinspection PyMethodMayBeStatic
    def get_viewport(self) -> Tuple[float, float, float, float]:
        """ Get the viewport. (What coordinates we can see.) """
        return get_viewport()

    def use(self):
        """Bind the window's framebuffer for rendering commands"""
        self.ctx.screen.use()

    def test(self, frames: int = 10):
        """
        Used by unit test cases. Runs the event loop a few times and stops.

        :param int frames:
        """
        start_time = time.time()
        for i in range(frames):
            self.switch_to()
            self.dispatch_events()
            self.dispatch_event('on_draw')
            self.flip()
            current_time = time.time()
            elapsed_time = current_time - start_time
            start_time = current_time
            if elapsed_time < 1. / 60.:
                sleep_time = (1. / 60.) - elapsed_time
                time.sleep(sleep_time)
            self._dispatch_updates(1 / 60)

    def show_view(self, new_view: 'View'):
        """
        Select the view to show. Calling this function is the same as setting the
        :py:meth:`arcade.Window.current_view` attribute.

        :param View new_view: View to show
        """
        if not isinstance(new_view, View):
            raise ValueError("Must pass an arcade.View object to "
                             "Window.show_view()")

        # Store the Window that is showing the "new_view" View.
        if new_view.window is None:
            new_view.window = self
        elif new_view.window != self:
            raise RuntimeError("You are attempting to pass the same view "
                               "object between multiple windows. A single "
                               "view object can only be used in one window.")

        # remove previously shown view's handlers
        if self._current_view is not None:
            self._current_view.on_hide_view()
            self.remove_handlers(self._current_view)

        # push new view's handlers
        self._current_view = new_view
        self.push_handlers(
            **{
                et: getattr(new_view, et, None)
                for et in self.event_types
                if et != 'on_show' and hasattr(new_view, et)
            }
        )
        self._current_view.on_show()
        self._current_view.on_show_view()

        # Note: After the View has been pushed onto pyglet's stack of event handlers (via push_handlers()), pyglet
        # will still call the Window's event handlers. (See pyglet's EventDispatcher.dispatch_event() implementation
        # for details)

    def _create(self):
        super()._create()

    def _recreate(self, changes):
        super()._recreate(changes)

    def flip(self):
        """ Swap OpenGL and backing buffers for double-buffered windows. """
        super().flip()

    def switch_to(self):
        """ Switch the this window. """
        super().switch_to()

    def set_caption(self, caption):
        """ Set the caption for the window. """
        super().set_caption(caption)

    def set_minimum_size(self, width: int, height: int):
        """ Set smallest window size. """
        super().set_minimum_size(width, height)

    def set_maximum_size(self, width, height):
        """ Set largest window size. """
        super().set_maximum_size(width, height)

    def set_location(self, x, y):
        """ Set location of the window. """
        super().set_location(x, y)

    def activate(self):
        """ Activate this window. """
        super().activate()

    def minimize(self):
        """ Minimize the window. """
        super().minimize()

    def maximize(self):
        """ Maximize  the window. """
        super().maximize()

    def set_vsync(self, vsync: bool):
        """ Set if we sync our draws to the monitors vertical sync rate. """
        super().set_vsync(vsync)

    def set_mouse_platform_visible(self, platform_visible=None):
        """ This does something. """
        super().set_mouse_platform_visible(platform_visible)

    def set_exclusive_mouse(self, exclusive=True):
        """ Capture the mouse. """
        super().set_exclusive_mouse(exclusive)

    def set_exclusive_keyboard(self, exclusive=True):
        """ Capture all keyboard input. """
        super().set_exclusive_keyboard(exclusive)

    def get_system_mouse_cursor(self, name):
        """ Get the system mouse cursor """
        return super().get_system_mouse_cursor(name)

    def dispatch_events(self):
        """ Dispatch events """
        super().dispatch_events()


def open_window(width: int, height: int, window_title: str, resizable: bool = False,
                antialiasing: bool = True) -> Window:
    """
    This function opens a window. For ease-of-use we assume there will only be one window, and the
    programmer does not need to keep a handle to the window. This isn't the best architecture, because
    the window handle is stored in a global, but it makes things easier for programmers if they don't
    have to track a window pointer.

    :param Number width: Width of the window.
    :param Number height: Height of the window.
    :param str window_title: Title of the window.
    :param bool resizable: Whether the window can be user-resizable.
    :param bool antialiasing: Smooth the graphics?

    :returns: Handle to window
    :rtype arcade.Window:
    """

    global _window
    _window = Window(width, height, window_title, resizable=resizable, update_rate=None,
                     antialiasing=antialiasing)
    _window.invalid = False
    return _window


class View:
    """
    Support different views/screens in a window.
    """

    def __init__(self,
                 window: Window = None):

        if window is None:
            self.window = arcade.get_window()
        else:
            self.window = window

        self.key: Optional[int] = None

    def update(self, delta_time: float):
        """To be overridden"""
        pass

    def on_update(self, delta_time: float):
        """To be overridden"""
        pass

    def on_draw(self):
        """Called when this view should draw"""
        pass

    def on_show(self):
        """Called when this view is shown and if window dispatches a on_show event.
        (first time showing window or resize)
        """
        pass

    def on_show_view(self):
        """Called when this view is shown"""
        pass

    def on_hide_view(self):
        """Called when this view is not shown anymore"""
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """
        Override this function to add mouse functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        """
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of the mouse
        :param float y: y position of the mouse
        :param int button: What button was hit. One of:
                           arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT,
                           arcade.MOUSE_BUTTON_MIDDLE
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        :param int _buttons: Which button is pressed
        :param int _modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x:
        :param float y:
        :param int button:
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """
        User moves the scroll wheel.

        :param int x:
        :param int y:
        :param int scroll_x:
        :param int scroll_y:
        """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        """
        Override this function to add key press functionality.

        :param int symbol: Key that was hit
        :param int modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              pressed during this event. See :ref:`keyboard_modifiers`.
        """
        try:
            self.key = symbol
        except AttributeError:
            pass

    def on_key_release(self, _symbol: int, _modifiers: int):
        """
        Override this function to add key release functionality.

        :param int _symbol: Key that was hit
        :param int _modifiers: Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                               pressed during this event. See :ref:`keyboard_modifiers`.
        """
        try:
            self.key = None
        except AttributeError:
            pass
