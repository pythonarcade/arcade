"""
The main window class that all object-oriented applications should
derive from.
"""
import logging
import os
import time
from typing import Tuple, Optional

import pyglet
import pyglet.gl as gl
from pyglet.canvas.base import ScreenMode

import arcade
from arcade import get_display_size
from arcade import get_viewport
from arcade import set_viewport
from arcade import set_window
from arcade.context import ArcadeContext
from arcade.arcade_types import Color
from arcade import SectionManager

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

    :returns: List of screens, one for each monitor.
    :rtype: List
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

    :param int width: Window width
    :param int height: Window height
    :param str title: Title (appears in title bar)
    :param bool fullscreen: Should this be full screen?
    :param bool resizable: Can the user resize the window?
    :param float update_rate: How frequently to update the window.
    :param bool antialiasing: Should OpenGL's anti-aliasing be enabled?
    :param Tuple[int,int] gl_version: What OpenGL version to request. This is ``(3, 3)`` by default
                                       and can be overridden when using more advanced OpenGL features.
    :param bool visible: Should the window be visible immediately
    :param bool vsync: Wait for vertical screen refresh before swapping buffer
                       This can make animations and movement look smoother.
    :param bool gc_mode: Decides how OpenGL objects should be garbage collected ("context_gc" (default) or "auto")
    :param bool center_window: If true, will center the window.
    :param bool samples: Number of samples used in antialiasing (default 4).
                         Usually this is 2, 4, 8 or 16.
    :param bool enable_polling: Enabled input polling capability. This makes the ``keyboard`` and ``mouse``
                                attributes available for use.
    """

    def __init__(
            self,
            width: int = 800,
            height: int = 600,
            title: str = 'Arcade Window',
            fullscreen: bool = False,
            resizable: bool = False,
            update_rate: Optional[float] = 1 / 60,
            antialiasing: bool = True,
            gl_version: Tuple[int, int] = (3, 3),
            screen: pyglet.canvas.Screen = None,
            style: Optional[str] = pyglet.window.Window.WINDOW_STYLE_DEFAULT,
            visible: bool = True,
            vsync: bool = False,
            gc_mode: str = "context_gc",
            center_window: bool = False,
            samples: int = 4,
            enable_polling: bool = True
    ):
        # In certain environments we can't have antialiasing/MSAA enabled.
        # Detect replit environment
        if os.environ.get("REPL_ID"):
            antialiasing = False

        config = None
        # Attempt to make window with antialiasing
        if antialiasing:
            try:
                config = pyglet.gl.Config(
                    major_version=gl_version[0],
                    minor_version=gl_version[1],
                    double_buffer=True,
                    sample_buffers=1,
                    samples=samples,
                )
                display = pyglet.canvas.get_display()
                screen = display.get_default_screen()
                config = screen.get_best_config(config)
            except pyglet.window.NoSuchConfigException:
                LOG.warning("Skipping antialiasing due missing hardware/driver support")
                config = None
                antialiasing = False
        # If we still don't have a config 
        if not config:
            config = pyglet.gl.Config(
                major_version=3,
                minor_version=3,
                double_buffer=True,
            )
        try:
            super().__init__(width=width, height=height, caption=title,
                             resizable=resizable, config=config, vsync=vsync, visible=visible, style=style)
            self.register_event_type('update')
            self.register_event_type('on_update')
        except pyglet.window.NoSuchConfigException:
            raise NoOpenGLException("Unable to create an OpenGL 3.3+ context. "
                                    "Check to make sure your system supports OpenGL 3.3 or higher.")
        if antialiasing:
            try:
                gl.glEnable(gl.GL_MULTISAMPLE_ARB)
            except pyglet.gl.GLException:
                LOG.warning("Warning: Anti-aliasing not supported on this computer.")

        if update_rate:
            self.set_update_rate(update_rate)

        self.set_vsync(vsync)

        super().set_fullscreen(fullscreen, screen)
        # This used to be necessary on Linux, but no longer appears to be.
        # With Pyglet 2.0+, setting this to false will not allow the screen to
        # update. It does, however, cause flickering if creating a window that
        # isn't derived from the Window class.
        # self.invalid = False
        set_window(self)

        self._current_view: Optional[View] = None
        self.current_camera: Optional[arcade.Camera] = None
        self.textbox_time = 0.0
        self.key: Optional[int] = None
        self.flip_count: int = 0
        self.static_display: bool = False

        self._ctx: ArcadeContext = ArcadeContext(self, gc_mode=gc_mode)
        set_viewport(0, self.width, 0, self.height)
        self._background_color: Color = (0, 0, 0, 0)

        # See if we should center the window
        if center_window:
            self.center_window()

        if enable_polling:
            self.keyboard = pyglet.window.key.KeyStateHandler()
            self.mouse = pyglet.window.mouse.MouseStateHandler()
            self.push_handlers(self.keyboard, self.mouse)
        else:
            self.keyboard = None
            self.mouse = None

        # Events that the section manager should handle (instead of the View) if sections are present in a View
        self.section_manager_events = {'on_mouse_motion', 'on_mouse_drag', 'on_mouse_press',
                                       'on_mouse_release', 'on_mouse_scroll', 'on_mouse_enter',
                                       'on_mouse_leave', 'on_key_press', 'on_key_release', 'on_draw',
                                       'on_update', 'update', 'on_resize'}

    @property
    def current_view(self) -> Optional["View"]:
        """
        This property returns the current view being shown.
        To set a different view, call the
        :py:meth:`arcade.Window.show_view` method.

        :rtype: arcade.View
        """
        return self._current_view

    @property
    def ctx(self) -> ArcadeContext:
        """
        The OpenGL context for this window.

        :type: :py:class:`arcade.ArcadeContext`
        """
        return self._ctx

    def clear(
            self,
            color: Optional[Color] = None,
            normalized: bool = False,
            viewport: Tuple[int, int, int, int] = None,
    ):
        """Clears the window with the configured background color
        set through :py:attr:`arcade.Window.background_color`.

        :param Color color: Optional color overriding the current background color
        :param bool normalized: If the color format is normalized (0.0 -> 1.0) or byte values
        :param Tuple[int, int, int, int]: The viewport range to clear
        """
        color = color if color is not None else self.background_color
        self.ctx.screen.clear(color, normalized=normalized, viewport=viewport)

    @property
    def background_color(self):
        """Get or set the background color for this window.

        If the background color is an ``RGB`` value instead of ``RGBA```
        we assume alpha value 255.

        :type: Color
        """
        return self._background_color

    @background_color.setter
    def background_color(self, value: Color):
        self._background_color = value

    def run(self):
        """
        Shortcut for :py:func:`arcade.run()`.

        For example::

            MyWindow().run()
        """
        arcade.run()

    def close(self):
        """ Close the Window. """
        super().close()
        pyglet.clock.unschedule(self._dispatch_updates)

    def set_fullscreen(self,
                       fullscreen: bool = True,
                       screen: Optional['Window'] = None,
                       mode: ScreenMode = None,
                       width: Optional[float] = None,
                       height: Optional[float] = None):
        """
        Set if we are full screen or not.

        :param bool fullscreen:
        :param screen: Which screen should we display on? See :func:`get_screens`
        :param pyglet.canvas.ScreenMode mode:
                The screen will be switched to the given mode.  The mode must
                have been obtained by enumerating `Screen.get_modes`.  If
                None, an appropriate mode will be selected from the given
                `width` and `height`.
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
        is resized. The main responsibility of this method is updating
        the projection and the viewport.

        If you are not changing the default behavior when overriding, make sure
        you call the parent's ``on_resize`` first::

            def on_resize(self, width: int, height: int):
                super().on_resize(width, height)
                # Add extra resize logic here

        :param int width: New width
        :param int height: New height
        """
        # Retain projection scrolling if applied
        original_viewport = self.get_viewport()
        self.set_viewport(original_viewport[0],
                          original_viewport[0] + width,
                          original_viewport[2],
                          original_viewport[2] + height)

    def set_min_size(self, width: int, height: int):
        """ Wrap the Pyglet window call to set minimum size

        :param float width: width in pixels.
        :param float height: height in pixels.
        """

        if self._resizable:
            super().set_minimum_size(width, height)
        else:
            raise ValueError('Cannot set min size on non-resizable window')

    def set_max_size(self, width: int, height: int):
        """ Wrap the Pyglet window call to set maximum size

        :param int width: width in pixels.
        :param int height: height in pixels.
        :Raises ValueError:

        """

        if self._resizable:
            super().set_maximum_size(width, height)
        else:
            raise ValueError('Cannot set max size on non-resizable window')

    def set_size(self, width: int, height: int):
        """
        Ignore the resizable flag and set the size

        :param int width:
        :param int height:
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

    def set_visible(self, visible: bool = True):
        """
        Set if the window is visible or not. Normally, a program's window is visible.

        :param bool visible:
        """
        super().set_visible(visible)

    # noinspection PyMethodMayBeStatic
    def set_viewport(self, left: float, right: float, bottom: float, top: float):
        """
        Set the viewport. (What coordinates we can see.
        Used to scale and/or scroll the screen).

        See :py:func:`arcade.set_viewport` for more detailed information.

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
        Select the view to show in the next frame.
        This is not a blocking call showing the view.
        Your code will continue to run after this call
        and the view will appear in the next dispatch
        of ``on_update``/``on_draw```.

        Calling this function is the same as setting the
        :py:attr:`arcade.Window.current_view` attribute.

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
            if self._current_view.has_sections:
                self.remove_handlers(self._current_view.section_manager)
            self.remove_handlers(self._current_view)

        # push new view's handlers
        self._current_view = new_view
        if new_view.has_sections:
            self.push_handlers(
                **{
                    et: getattr(new_view.section_manager, et, None)
                    for et in self.section_manager_events
                 }
            )
        self.push_handlers(
            **{
                et: getattr(new_view, et, None)
                for et in self.event_types
                if et != 'on_show' and et not in self.section_manager_events and hasattr(new_view, et)
            }
        )
        self._current_view.on_show()
        self._current_view.on_show_view()
        if self._current_view.has_sections:
            self._current_view.on_show_view()

        # Note: After the View has been pushed onto pyglet's stack of event handlers (via push_handlers()), pyglet
        # will still call the Window's event handlers. (See pyglet's EventDispatcher.dispatch_event() implementation
        # for details)

    def hide_view(self):
        """
        Hide the currently active view (if any) returning us
        back to ``on_draw`` and ``on_update`` functions in the window.

        This is not necessary to call if you are switching views.
        Simply call ``show_view`` again.
        """
        if self._current_view is None:
            return

        self._current_view.on_hide_view()
        if self._current_view.has_sections:
            self._current_view.section_manager.on_hide_view()
            self.remove_handlers(self._current_view.section_manager)
        self.remove_handlers(self._current_view)
        self._current_view = None

    def _create(self):
        super()._create()

    def _recreate(self, changes):
        super()._recreate(changes)

    def flip(self):
        """
        Window framebuffers norally have a back and front buffer.
        This method makes the back buffer visible and hides the front buffer.
        A frame is rendered into the back buffer, so this method displays
        the frame we currently worked on.

        This method also garbage collect OpenGL resources
        before swapping the buffers.
        """
        # Garbage collect OpenGL resources
        num_collected = self.ctx.gc()
        LOG.debug("Garbage collected %s OpenGL resource(s)", num_collected)

        # Attempt to handle static draw setups
        if self.static_display and self.flip_count > 0:
            return
        elif self.static_display:
            self.flip_count += 1

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

    # def set_mouse_platform_visible(self, platform_visible=None):
    #     """ This does something. """
    #     super().set_mouse_platform_visible(platform_visible)

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
    :rtype: Window
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
        self.section_manager: SectionManager = SectionManager(self)

    @property
    def has_sections(self) -> bool:
        """ Return if the View has sections """
        return self.section_manager.has_sections

    def add_section(self, section, at_index: Optional[int] = None) -> None:
        """
        Adds a section to the view Section Manager.
        :param section: the section to add to this section manager
        :param at_index: inserts the section at that index. If None at the end
        """
        return self.section_manager.add_section(section, at_index)

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

    def on_resize(self, width: int, height: int):
        """
        Called when the window is resized while this view is active.
        :py:meth:`~arcade.Window.on_resize` is also called separately.
        By default this method does nothing and can be overridden to
        handle resize logic.
        """
        pass
