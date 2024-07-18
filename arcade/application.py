"""
The main window class that all object-oriented applications should
derive from.
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Optional

import pyglet
import pyglet.gl as gl
import pyglet.window.mouse
from pyglet.display.base import ScreenMode
from pyglet.window import MouseCursor

import arcade
from arcade.clock import GLOBAL_CLOCK, GLOBAL_FIXED_CLOCK, _setup_clock, _setup_fixed_clock
from arcade.color import TRANSPARENT_BLACK
from arcade.context import ArcadeContext
from arcade.sections import SectionManager
from arcade.types import LBWH, Color, Rect, RGBANormalized, RGBOrA255
from arcade.utils import is_raspberry_pi
from arcade.window_commands import get_display_size, set_window

if TYPE_CHECKING:
    from arcade.camera import Projector
    from arcade.camera.default import DefaultProjector
    from arcade.start_finish_data import StartFinishRenderData


LOG = logging.getLogger(__name__)

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4

_window: "Window"

__all__ = [
    "get_screens",
    "NoOpenGLException",
    "Window",
    "open_window",
    "View",
    "MOUSE_BUTTON_LEFT",
    "MOUSE_BUTTON_MIDDLE",
    "MOUSE_BUTTON_RIGHT",
]


def get_screens() -> list:
    """
    Return a list of screens. So for a two-monitor setup, this should return
    a list of two screens. Can be used with :class:`arcade.Window` to select which
    window we full-screen on.

    Returns:
        List of screens, one for each monitor.
    """
    display = pyglet.display.get_display()
    return display.get_screens()


class NoOpenGLException(Exception):
    """Exception when we can't get an OpenGL 3.3+ context"""

    pass


class Window(pyglet.window.Window):
    """
    A window that will appear on your desktop.

    This class is a subclass of Pyglet's Window class with many
    Arcade-specific features added.

    .. note::

        Arcade currently cannot easily support multiple windows. If you need
        multiple windows, consider using multiple views or divide the window
        into sections.

    .. _pyglet_pg_window_size_position:
    ..  https://pyglet.readthedocs.io/en/latest/programming_guide/windowing.html#size-and-position
    .. _pyglet_pg_window_style:
    ..  https://pyglet.readthedocs.io/en/latest/programming_guide/windowing.html#window-style

    Args:
        width (int, optional): Window width. Defaults to 1280.
        height (int, optional): Window height. Defaults to 720.
        title (str, optional): The title/caption of the window
        fullscreen (bool, optional): Should this be full screen?
        resizable (bool, optional): Can the user resize the window?
        update_rate (float, optional): How frequently to run the on_update event.
        draw_rate (float, optional): How frequently to run the on_draw event.
            (this is the FPS limit)
        fixed_rate (float, optional): How frequently should the fixed_updates run,
            fixed updates will always run at this rate.
        fixed_frame_cap (float, optional): The maximum number of fixed updates that
            can occur in one update loop.defaults to infinite. If large lag spikes
            cause your game to freeze, try setting this to a smaller number. This
            may cause your physics to lag behind temporarily.
        antialiasing (bool, optional): Use multisampling framebuffer (antialiasing)
        samples (int): Number of samples used in antialiasing (default 4).
            Usually this is 2, 4, 8 or 16.
        gl_version (tuple[int, int], optional): What OpenGL version to request.
            This is ``(3, 3)`` by default and can be overridden when using more
            advanced OpenGL features.
        screen (optional): Pass a pyglet :py:class:`~pyglet.display.Screen` to
            request the window be placed on it. See `pyglet's window size &
            position guide <pyglet_pg_window_size_position_>`_ to learn more.
        style (optional): Request a non-default window style, such as borderless.
            Some styles only work in certain situations. See `pyglet's guide
            to window style <pyglet_pg_window_style_>`_ to learn more.
        visible (bool, optional): Should the window be visible immediately
        vsync (bool, optional): Wait for vertical screen refresh before swapping buffer
            This can make animations and movement look smoother.
        gc_mode (str, optional): Decides how OpenGL objects should be garbage collected
            ("context_gc" (default) or "auto")
        center_window (bool, optional): If true, will center the window.
        enable_polling (bool, optional): Enabled input polling capability.
            This makes the :py:attr:`keyboard` and :py:attr:`mouse` attributes available for use.

    Raises:
        NoOpenGLException: If the system does not support OpenGL requested OpenGL version.
    """

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        title: str | None = "Arcade Window",
        fullscreen: bool = False,
        resizable: bool = False,
        update_rate: float = 1 / 60,
        antialiasing: bool = True,
        gl_version: tuple[int, int] = (3, 3),
        screen: pyglet.display.Screen | None = None,
        style: str | None = pyglet.window.Window.WINDOW_STYLE_DEFAULT,
        visible: bool = True,
        vsync: bool = False,
        gc_mode: str = "context_gc",
        center_window: bool = False,
        samples: int = 4,
        enable_polling: bool = True,
        gl_api: str = "gl",
        draw_rate: float = 1 / 60,
        fixed_rate: float = 1.0 / 60.0,
        fixed_frame_cap: int | None = None,
    ) -> None:
        # In certain environments we can't have antialiasing/MSAA enabled.
        # Detect replit environment
        if os.environ.get("REPL_ID"):
            antialiasing = False

        # Detect Raspberry Pi and switch to OpenGL ES 3.1
        if is_raspberry_pi():
            gl_version = 3, 1
            gl_api = "gles"

        self.headless: bool = arcade.headless
        """If True, the window is running in headless mode."""

        config = None
        # Attempt to make window with antialiasing
        if antialiasing:
            try:
                config = pyglet.gl.Config(
                    major_version=gl_version[0],
                    minor_version=gl_version[1],
                    opengl_api=gl_api,  # type: ignore  # pending: upstream fix
                    double_buffer=True,
                    sample_buffers=1,
                    samples=samples,
                    depth_size=24,
                    stencil_size=8,
                    red_size=8,
                    green_size=8,
                    blue_size=8,
                    alpha_size=8,
                )
                display = pyglet.display.get_display()
                screen = display.get_default_screen()  # type: ignore  # pending: resolve upstream type tricks
                if screen:
                    config = screen.get_best_config(config)
            except pyglet.window.NoSuchConfigException:
                LOG.warning("Skipping antialiasing due missing hardware/driver support")
                config = None
                antialiasing = False
        # If we still don't have a config
        if not config:
            config = pyglet.gl.Config(
                major_version=gl_version[0],
                minor_version=gl_version[1],
                opengl_api=gl_api,  # type: ignore  # pending: upstream fix
                double_buffer=True,
                depth_size=24,
                stencil_size=8,
                red_size=8,
                green_size=8,
                blue_size=8,
                alpha_size=8,
            )
        try:
            super().__init__(
                width=width,
                height=height,
                caption=title,
                resizable=resizable,
                config=config,
                vsync=vsync,
                visible=visible,
                style=style,
            )
            # pending: weird import tricks resolved
            self.register_event_type("on_update")  # type: ignore
            self.register_event_type("on_action")  # type: ignore
            self.register_event_type("on_fixed_update")  # type: ignore
        except pyglet.window.NoSuchConfigException:
            raise NoOpenGLException(
                "Unable to create an OpenGL 3.3+ context. "
                "Check to make sure your system supports OpenGL 3.3 or higher."
            )
        if antialiasing:
            try:
                gl.glEnable(gl.GL_MULTISAMPLE_ARB)
            except pyglet.gl.GLException:
                LOG.warning("Warning: Anti-aliasing not supported on this computer.")

        _setup_clock()
        _setup_fixed_clock(fixed_rate)

        # We don't call the set_draw_rate function here because unlike the updates,
        # the draw scheduling is initially set in the call to pyglet.app.run()
        # that is done by the run() function. run() will pull this draw rate from
        # the Window and use it. Calls to set_draw_rate only need
        # to be done if changing it after the application has been started.
        self._draw_rate = draw_rate

        # Fixed rate cannot be changed post initialization as this throws off physics sims.
        # If more time resolution is needed in fixed updates, devs can do 'sub-stepping'.
        self._fixed_rate = fixed_rate
        self._fixed_frame_cap = fixed_frame_cap
        self.set_update_rate(update_rate)

        self.set_vsync(vsync)

        super().set_fullscreen(fullscreen, screen)
        # This used to be necessary on Linux, but no longer appears to be.
        # With Pyglet 2.0+, setting this to false will not allow the screen to
        # update. It does, however, cause flickering if creating a window that
        # isn't derived from the Window class.
        set_window(self)

        self.push_handlers(on_resize=self._on_resize)

        self._ctx: ArcadeContext = ArcadeContext(self, gc_mode=gc_mode, gl_api=gl_api)
        self._background_color: Color = TRANSPARENT_BLACK

        self._current_view: Optional[View] = None

        # See if we should center the window
        if center_window:
            self.center_window()

        self.keyboard: Optional[pyglet.window.key.KeyStateHandler] = None
        """
        A pyglet KeyStateHandler that can be used to poll the state of the keyboard.

            Example::

                    if self.window.keyboard[key.SPACE]:
                        print("The space key is currently being held down.")
        """
        self.mouse: Optional[pyglet.window.mouse.MouseStateHandler] = None
        """
        A pyglet MouseStateHandler that can be used to poll the state of the mouse.

            Example::

                if self.window.mouse.LEFT:
                    print("The left mouse button is currently being held down.")
                print(
                    "The mouse is at position "
                    f"{self.window.mouse["x"]}, {self.window.mouse["y"]}"
                )
        """

        if enable_polling:
            self.keyboard = pyglet.window.key.KeyStateHandler()

            if arcade.headless:
                self.push_handlers(self.keyboard)

            else:
                self.mouse = pyglet.window.mouse.MouseStateHandler()
                self.push_handlers(self.keyboard, self.mouse)
        else:
            self.keyboard = None
            self.mouse = None

        # Framebuffer for drawing content into when start_render is called.
        # These are typically functions just at module level wrapped in
        # start_render and finish_render calls. The framebuffer is repeatedly
        # rendered to the window when the event loop starts.
        self._start_finish_render_data: Optional[StartFinishRenderData] = None

    @property
    def current_view(self) -> Optional["View"]:
        """
        The currently active view.

        To set a different view, call :py:meth:`~arcade.Window.show_view`.
        """
        return self._current_view

    @property
    def ctx(self) -> ArcadeContext:
        """
        The OpenGL context for this window.

        This context instance provides access to a powerful set of
        features for lower level OpenGL programming. It is also used
        internally by Arcade to manage OpenGL resources.
        """
        return self._ctx

    def clear(
        self,
        color: Optional[RGBOrA255] = None,
        color_normalized: Optional[RGBANormalized] = None,
        viewport: Optional[tuple[int, int, int, int]] = None,
    ) -> None:
        """
        Clears the window with the configured background color
        set through :py:attr:`~arcade.Window.background_color`.

        Args:
            color (optional): Override the current background color
                with one of the following:

                1. A :py:class:`~arcade.types.Color` instance
                2. A 3 or 4-length RGB/RGBA :py:class:`tuple` of byte values (0 to 255)

            color_normalized (RGBANormalized, optional): override the current background color
                using normalized values (0.0 to 1.0). For example, (1.0, 0.0, 0.0, 1.0)
                making the window contents red.

            viewport (Tuple[int, int, int, int], optional): The area of the window to clear.
                By default, the entire window is cleared.
                The viewport format is ``(x, y, width, height)``.
        """
        # Use the configured background color if none is provided
        if color is None and color_normalized is None:
            color = self.background_color
        self.ctx.screen.clear(color=color, color_normalized=color_normalized, viewport=viewport)

    @property
    def background_color(self) -> Color:
        """
        Get or set the background color for this window.
        This affects what color the window will contain when
        :py:meth:`~arcade.Window.clear` is called.

        Examples::

            # Use Arcade's built in Color values
            window.background_color = arcade.color.AMAZON

            # Set the background color with a custom Color instance
            MY_RED = arcade.types.Color(255, 0, 0)
            window.background_color = MY_RED

            # Set the background color directly from an RGBA tuple
            window.background_color = 255, 0, 0, 255

            # Set the background color directly from an RGB tuple
            # RGB tuples will assume 255 as the opacity / alpha value
            window.background_color = 255, 0, 0
        """
        return self._background_color

    @background_color.setter
    def background_color(self, value: RGBOrA255) -> None:
        self._background_color = Color.from_iterable(value)

    @property
    def rect(self) -> Rect:
        """Return a Rect describing the size of the window."""
        return LBWH(0, 0, self.width, self.height)

    def run(self) -> None:
        """
        Run the event loop.

        After the window has been set up, and the event hooks are in place, this
        is usually one of the last commands on the main program. This is a blocking
        function starting pyglet's event loop meaning it will start to dispatch
        events such as ``on_draw`` and ``on_update``.
        """
        arcade.run()

    def close(self) -> None:
        """Close the Window."""
        super().close()
        # Make sure we don't reference the window any more
        set_window(None)
        pyglet.clock.unschedule(self._dispatch_updates)

    def set_fullscreen(
        self,
        fullscreen: bool = True,
        screen=None,
        mode: ScreenMode | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> None:
        """
        Change the fullscreen status of the window.

        In most cases you simply want::

            # Enter fullscreen mode
            window.set_fullscreen(True)
            # Leave fullscreen mode
            window.set_fullscreen(False)

        When entering fullscreen mode the window will resize to the screen's
        resolution. When leaving fullscreen mode the window will resize back
        to the size it was before entering fullscreen mode.

        Args:
            fullscreen (bool): Should we enter or leave fullscreen mode?
            screen (optional): Which screen should we display on? See :func:`get_screens`
            mode (optional): The screen will be switched to the given mode.  The mode must
                have been obtained by enumerating `Screen.get_modes`.  If
                None, an appropriate mode will be selected from the given
                `width` and `height`.
            width: Override the width of the window. Will be rounded to
                :py:attr:`int`.
            height: Override the height of the window. Will be rounded to
                :py:attr:`int`.
        """
        # fmt: off
        super().set_fullscreen(
            fullscreen, screen, mode,
            # TODO: resolve the upstream int / float screen coord issue
            None if width is None else int(width),
            None if height is None else int(height))
        # fmt: on

    def center_window(self) -> None:
        """Center the window on your desktop."""
        # Get the display screen using pyglet
        screen_width, screen_height = get_display_size()

        window_width, window_height = self.get_size()
        # Center the window
        self.set_location((screen_width - window_width) // 2, (screen_height - window_height) // 2)

    def on_update(self, delta_time: float) -> Optional[bool]:
        """
        This method can be implemented and is reserved for game logic.
        Move sprites. Perform collision checks and other game logic.
        This method is called every frame before :meth:`on_draw`.

        The ``delta_time`` can be used to make sure the game runs at the same
        speed, no matter the frame rate.

        Args:
            delta_time (float): Time interval since the last time the function was
                called in seconds.
        """
        pass

    def on_fixed_update(self, delta_time: float):
        """
        Called for each fixed update. This is useful for physics engines
        and other systems that should update at a constant rate.

        Args:
            delta_time (float): Time interval since the last time the function was
                called in seconds.
        """
        pass

    def _dispatch_updates(self, delta_time: float) -> None:
        """
        Internal function that is scheduled with Pyglet's clock, this function gets
        run by the clock, and dispatches the on_update events.

        It also accumulates time and runs fixed updates until the Fixed Clock catches
        up to the global clock

        Args:
            delta_time (float): Time interval since the last time the function was
                called in seconds.
        """
        GLOBAL_CLOCK.tick(delta_time)
        fixed_count = 0
        while GLOBAL_FIXED_CLOCK.accumulated >= self._fixed_rate and (
            self._fixed_frame_cap is None or fixed_count <= self._fixed_frame_cap
        ):
            GLOBAL_FIXED_CLOCK.tick(self._fixed_rate)
            self.dispatch_event("on_fixed_update", self._fixed_rate)
            fixed_count += 1
        self.dispatch_event("on_update", GLOBAL_CLOCK.delta_time)

    def set_update_rate(self, rate: float) -> None:
        """
        Set how often the on_update function should be dispatched.
        For example::

            # Set the update rate to 60 times per second.
            self.set_update_rate(1 / 60)

        :param rate: Update frequency in seconds
        """
        self._update_rate = rate
        pyglet.clock.unschedule(self._dispatch_updates)
        pyglet.clock.schedule_interval(self._dispatch_updates, rate)

    def set_draw_rate(self, rate: float) -> None:
        """
        Set how often the on_draw function should be run.
        For example::

            # Set the draw rate to 60 frames per second.
            set.set_draw_rate(1 / 60)
        """
        self._draw_rate = rate
        pyglet.clock.unschedule(pyglet.app.event_loop._redraw_windows)
        pyglet.clock.schedule_interval(pyglet.app.event_loop._redraw_windows, self._draw_rate)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Called repeatedly while the mouse is moving in the window area.

        Override this function to respond to changes in mouse position.

        Args:
            x (int): x position of mouse within the window in pixels
            y (int): y position of mouse within the window in pixels
            dx (int): Change in x since the last time this method was called
            dy (int): Change in y since the last time this method was called
        """
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> Optional[bool]:
        """
        Called once whenever a mouse button gets pressed down.

        Override this function to handle mouse clicks. For an example of
        how to do this, see arcade's built-in :ref:`aiming and shooting
        bullets <sprite_bullets_aimed>` demo.

        Args:
            x (int): x position of the mouse
            y (int): y position of the mouse
            button (int): What button was pressed.
                This will always be one of the following:

                - ``arcade.MOUSE_BUTTON_LEFT``
                - ``arcade.MOUSE_BUTTON_RIGHT``
                - ``arcade.MOUSE_BUTTON_MIDDLE``

            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                      active during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        Called repeatedly while the mouse moves with a button down.

        Override this function to handle dragging.

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            dx (int): Change in x since the last time this method was called
            dy (int): Change in y since the last time this method was called
            buttons (int): Which button is pressed
            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              active during this event. See :ref:`keyboard_modifiers`.
        """
        return self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> Optional[bool]:
        """
        Called once whenever a mouse button gets released.

        Override this function to respond to mouse button releases. This
        may be useful when you want to use the duration of a mouse click
        to affect gameplay.

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            button (int): What button was hit. One of:

                - ``arcade.MOUSE_BUTTON_LEFT``
                - ``arcade.MOUSE_BUTTON_RIGHT``
                - ``arcade.MOUSE_BUTTON_MIDDLE``

            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                active during this event. See :ref:`keyboard_modifiers`.
        """
        return False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> Optional[bool]:
        """
        Called repeatedly while a mouse scroll wheel moves.

        Override this function to respond to scroll events. The scroll
        arguments may be positive or negative to indicate direction, but
        the units are unstandardized. How many scroll steps you receive
        may vary wildly between computers depending a number of factors,
        including system settings and the input devices used (i.e. mouse
        scrollwheel, touch pad, etc).

        .. warning:: Not all users can scroll easily!

                 Only some input devices support horizontal
                 scrolling. Standard vertical scrolling is common,
                 but some laptop touch pads are hard to use.

                 This means you should be careful about how you use
                 scrolling. Consider making it optional
                 to maximize the number of people who can play your
                 game!

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            scroll_x (int): number of steps scrolled horizontally
                     since the last call of this function
            scroll_y (int): number of steps scrolled vertically since
                     the last call of this function
        """
        return False

    def set_mouse_visible(self, visible: bool = True) -> None:
        """
        Set whether to show the system's cursor while over the window

        By default, the system mouse cursor is visible whenever the
        mouse is over the window. To hide the cursor, pass ``False`` to
        this function. Pass ``True`` to make the cursor visible again.

        The window will continue receiving mouse events while the cursor
        is hidden, including movements and clicks. This means that
        functions like :meth:`~.Window.on_mouse_motion` and
        t':meth:`~.Window.on_mouse_press` will continue to work normally.

        You can use this behavior to visually replace the system mouse
        cursor with whatever you want. One example is :ref:`a game
        character that is always at the most recent mouse position in
        the window<sprite_collect_coins>`.

        .. note:: Advanced users can try using system cursor state icons

                 It may be possible to use system icons representing
                 cursor interaction states such as hourglasses or resize
                 arrows by using features :class:``~arcade.Window`` inherits
                 from the underlying pyglet window class. See the
                 `pyglet overview on cursors
                 <https://pyglet.readthedocs.io/en/master/programming_guide/mouse.html#changing-the-mouse-cursor>`_
                 for more information.

        Args:
            visible (bool): Whether to hide the system mouse cursor
        """
        super().set_mouse_visible(visible)

    def on_action(self, action_name: str, state) -> None:
        """
        Called when an action is dispatched.
        This is related to the input manager.

        Args:
            action_name (str): The name of the action
            state: The state of the action
        """
        pass

    def on_key_press(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called once when a key gets pushed down.

        Override this function to add key press functionality.

        .. tip:: If you want the length of key presses to affect
                 gameplay, you also need to override
                 :meth:`~.Window.on_key_release`.

        Args:
            symbol (int): Key that was just pushed down
            modifiers (int): Bitwise 'and' of all modifiers (shift,
                      ctrl, num lock) active during this event.
                      See :ref:`keyboard_modifiers`.
        """
        return False

    def on_key_release(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called once when a key gets released.

        Override this function to add key release functionality.

        Situations that require handling key releases include:

        * Rhythm games where a note must be held for a certain
          amount of time
        * 'Charging up' actions that change strength depending on
          how long a key was pressed
        * Showing which keys are currently pressed down

        Args:
            symbol (int): Key that was released
            modifiers (int): Bitwise 'and' of all modifiers (shift,
                      ctrl, num lock) active during this event.
                      See :ref:`keyboard_modifiers`.
        """
        return False

    def on_draw(self) -> Optional[bool]:
        """
        Override this function to add your custom drawing code.

        This method is usually called 60 times a second unless
        another update rate has been set. Should be called after
        :meth:`~arcade.Window.on_update`.

        This function should normally start with a call to
        :meth:`~arcade.Window.clear` to clear the screen.
        """
        if self._start_finish_render_data:
            self.clear()
            self._start_finish_render_data.draw()
            return True

        return False

    def _on_resize(self, width: int, height: int) -> Optional[bool]:
        """
        The internal method called when the window is resized.

        The purpose of this method is mainly setting the viewport
        to the new size of the window. Users should override
        :meth:`~arcade.Window.on_resize` instead. This method is
        called first.

        Args:
            width (int): New width of the window
            height (int): New height of the window
        """
        # Retain viewport
        self.viewport = (0, 0, width, height)

        return False

    def on_resize(self, width: int, height: int) -> Optional[bool]:
        """
        Override this method to add custom actions when the window is resized.

        An internal ``_on_resize`` is called first adjusting the viewport
        to the new size of the window so there is no need to call
        ```super().on_resize(width, height)```.

        Args:
            width (int): New width of the window
            height (int): New height of the window
        """
        pass

    def set_minimum_size(self, width: int, height: int) -> None:
        """
        Set the minimum size of the window.

        This will limit how small the window can be resized.

        Args:
            width (int): Minimum width
            height (int): Minimum height
        """
        super().set_minimum_size(width, height)

    def set_maximum_size(self, width: int, height: int) -> None:
        """
        Sets the maximum size of the window.

        This will limit how large the window can be resized.

        Args:
            width (int): Maximum width
            height (int): Maximum height
        """
        super().set_maximum_size(width, height)

    def set_size(self, width: int, height: int) -> None:
        """
        Resize the window.

        Args:
            width (int): New width of the window
            height (int): New height of the window
        """
        super().set_size(width, height)

    def get_size(self) -> tuple[int, int]:
        """Get the size of the window."""
        return super().get_size()

    def get_location(self) -> tuple[int, int]:
        """Get the current X/Y coordinates of the window."""
        return super().get_location()

    def set_visible(self, visible: bool = True):
        """
        Set if the window should be visible or not.

        Args:
            visible (bool): Should the window be visible?
        """
        super().set_visible(visible)

    def use(self) -> None:
        """Make the window the target for drawing.

        The window will always be the target for drawing unless
        offscreen framebuffers are used in the application.

        This simply binds the window's framebuffer.
        """
        self.ctx.screen.use()

    @property
    def default_camera(self) -> DefaultProjector:
        """
        The default camera for the window.

        This is an extremely simple camera simply responsible for
        maintaining the default projection and viewport.
        """
        return self._ctx._default_camera

    @property
    def current_camera(self) -> Projector:
        """
        Get or set the current camera.

        This represents the projector currently being used to define
        the projection and view matrices.
        """
        return self._ctx.current_camera

    @current_camera.setter
    def current_camera(self, next_camera):
        self._ctx.current_camera = next_camera

    @property
    def viewport(self) -> tuple[int, int, int, int]:
        """
        Get/set the viewport of the window.

        This will define what area of the window is rendered into.
        The values are ``x, y, width, height``. The value will normally
        be ``(0, 0, screen width, screen height)``.

        In most case you don't want to change this value manually
        and instead rely on the cameras.
        """
        return self._ctx.screen.viewport

    @viewport.setter
    def viewport(self, new_viewport: tuple[int, int, int, int]):
        if self._ctx.screen == self._ctx.active_framebuffer:
            self._ctx.viewport = new_viewport
        else:
            self._ctx.screen.viewport = new_viewport

    def test(self, frames: int = 10) -> None:
        """
        Used by unit test cases. Runs the event loop a few times and stops.

        :param frames:
        """
        start_time = time.time()
        for _ in range(frames):
            self.switch_to()
            self.dispatch_events()
            self.dispatch_event("on_draw")
            self.flip()
            current_time = time.time()
            elapsed_time = current_time - start_time
            start_time = current_time
            if elapsed_time < 1.0 / 60.0:
                sleep_time = (1.0 / 60.0) - elapsed_time
                time.sleep(sleep_time)
            self._dispatch_updates(1 / 60)

    def show_view(self, new_view: "View") -> None:
        """
        Set the currently active view.

        This will hide the current view
        and show the new view in the next frame.

        This is not a blocking call. It will simply point to the new view
        and return immediately.

        Calling this function is the same as setting the
        :py:attr:`arcade.Window.current_view` attribute.

        Args:
            new_view (View): The view to activate.
        """
        if not isinstance(new_view, View):
            raise TypeError(
                f"Window.show_view() takes an arcade.View," f"but it got a {type(new_view)}."
            )

        self._ctx.screen.use()
        self.viewport = (0, 0, self.width, self.height)

        # Store the Window that is showing the "new_view" View.
        if new_view.window is None:
            new_view.window = self
        # NOTE: This is not likely to happen and is creating issues for the test suite.
        # elif new_view.window != self:
        #     raise RuntimeError((
        #         "You are attempting to pass the same view "
        #         "object between multiple windows. A single "
        #         "view object can only be used in one window. "
        #         f"{self} != {new_view.window}"
        #     ))

        # remove previously shown view's handlers
        if self._current_view is not None:
            self._current_view.on_hide_view()
            if self._current_view.has_sections:
                self.remove_handlers(self._current_view.section_manager)
            self.remove_handlers(self._current_view)

        # push new view's handlers
        self._current_view = new_view
        if new_view.has_sections:
            section_manager_managed_events = new_view.section_manager.managed_events
            section_handlers = {
                event_type: getattr(new_view.section_manager, event_type, None)
                for event_type in section_manager_managed_events
            }
            if section_handlers:
                self.push_handlers(**section_handlers)
        else:
            section_manager_managed_events = set()

        # Note: Excluding on_show because this even can trigger multiple times.
        #       It should only be called once when the view is shown.
        view_handlers = {
            event_type: getattr(new_view, event_type, None)
            for event_type in self.event_types
            if event_type != "on_show"
            and event_type not in section_manager_managed_events
            and hasattr(new_view, event_type)
        }
        if view_handlers:
            self.push_handlers(**view_handlers)
        self._current_view.on_show_view()
        if self._current_view.has_sections:
            self._current_view.section_manager.on_show_view()

        # Note: After the View has been pushed onto pyglet's stack of event handlers
        # (via push_handlers()), pyglet
        # will still call the Window's event handlers.
        # (See pyglet's EventDispatcher.dispatch_event() implementation for details)

    def hide_view(self) -> None:
        """
        Hide the currently active view (if any).

        This is only necessary if you don't want an active view
        falling back to the window's event handlers. It's not
        necessary to call when changing the active view.
        """
        if self._current_view is None:
            return

        self._current_view.on_hide_view()
        if self._current_view.has_sections:
            self._current_view.section_manager.on_hide_view()
            self.remove_handlers(self._current_view.section_manager)
        self.remove_handlers(self._current_view)
        self._current_view = None

    # def _create(self) -> None:
    #     super()._create()

    # def _recreate(self, changes) -> None:
    #     super()._recreate(changes)

    def flip(self) -> None:
        """
        Present the rendered content to the screen.

        This is not necessary to call when using the standard standard
        event loop. The event loop will automatically call this method
        after ``on_draw`` has been called.

        Window framebuffers normally have a back and front buffer meaning
        they are "double buffered". Content is always drawn into the back
        buffer while the front buffer contains the previous frame.
        Swapping the buffers makes the back buffer visible and hides the
        front buffer. This is done to prevent flickering and tearing.

        This method also garbage collects OpenGL resources if there are
        any dead resources to collect.
        """
        # Garbage collect OpenGL resources
        num_collected = self.ctx.gc()
        LOG.debug("Garbage collected %s OpenGL resource(s)", num_collected)

        super().flip()

    def switch_to(self) -> None:
        """Switch the this window context.

        This is normally only used in multi-window applications.
        """
        super().switch_to()

    def set_caption(self, caption) -> None:
        """Set the caption/title of the window."""
        super().set_caption(caption)

    def set_location(self, x, y) -> None:
        """Set location of the window."""
        super().set_location(x, y)

    def activate(self) -> None:
        """Activate this window."""
        super().activate()

    def minimize(self) -> None:
        """Minimize the window."""
        super().minimize()

    def maximize(self) -> None:
        """Maximize  the window."""
        super().maximize()

    def set_vsync(self, vsync: bool) -> None:
        """Set if we sync our draws to the monitors vertical sync rate."""
        super().set_vsync(vsync)

    def set_mouse_platform_visible(self, platform_visible=None) -> None:
        """
        .. warning:: You are probably looking for
                     :meth:`~.Window.set_mouse_visible`!

        This is a lower level function inherited from the pyglet window.

        For more information on what this means, see the documentation
        for :py:meth:`pyglet.window.Window.set_mouse_platform_visible`.
        """
        super().set_mouse_platform_visible(platform_visible)

    def set_exclusive_mouse(self, exclusive=True) -> None:
        """Capture the mouse."""
        super().set_exclusive_mouse(exclusive)

    def set_exclusive_keyboard(self, exclusive=True) -> None:
        """Capture all keyboard input."""
        super().set_exclusive_keyboard(exclusive)

    def get_system_mouse_cursor(self, name) -> MouseCursor:
        """Get the system mouse cursor"""
        return super().get_system_mouse_cursor(name)

    def dispatch_events(self) -> None:
        """Dispatch events"""
        super().dispatch_events()

    def on_mouse_enter(self, x: int, y: int) -> Optional[bool]:
        """
        Called once whenever the mouse enters the window area on screen.

        This event will not be triggered if the mouse is currently being
        dragged.

        Args:
            x (int): The x position the mouse entered the window
            y (int): The y position the mouse entered the window
        """
        pass

    def on_mouse_leave(self, x: int, y: int) -> Optional[bool]:
        """
        Called once whenever the mouse leaves the window area on screen.

        This event will not be triggered if the mouse is currently being
        dragged. Note that the coordinates of the mouse pointer will be
        outside of the window rectangle.

        Args:
            x (int): The x position the mouse entered the window
            y (int): The y position the mouse entered the window
        """
        pass

    @property
    def center(self) -> tuple[float, float]:
        """
        Returns center coordinates of the window

        Equivalent to ``(self.width / 2, self.height / 2)``.
        """
        return (self.width / 2, self.height / 2)

    @property
    def center_x(self) -> float:
        """
        Returns the center x-coordinate of the window.

        Equivalent to ``self.width / 2``.
        """
        return self.width / 2

    @property
    def center_y(self) -> float:
        """
        Returns the center y-coordinate of the window.

        Equivalent to ``self.height / 2``.
        """
        return self.height / 2

    # --- CLOCK ALIASES ---
    @property
    def time(self) -> float:
        """
        Shortcut to the global clock's time.

        This is the time in seconds since the application started.
        """
        return GLOBAL_CLOCK.time

    @property
    def fixed_time(self) -> float:
        """
        Shortcut to the fixed clock's time.

        This is the time in seconds since the application started
        but updated at a fixed rate.
        """
        return GLOBAL_FIXED_CLOCK.time

    @property
    def delta_time(self) -> float:
        """Shortcut for the global clock's delta_time."""
        return GLOBAL_CLOCK.delta_time

    @property
    def fixed_delta_time(self) -> float:
        """The configured fixed update rate"""
        return self._fixed_rate


def open_window(
    width: int,
    height: int,
    window_title: Optional[str] = None,
    resizable: bool = False,
    antialiasing: bool = True,
) -> Window:
    """
    Shortcut for opening/creating a window with less options.

    For a full set of window options, create a :py:class:`~arcade.Window`
    instance directly.

    Args:
        width (int): Width of the window.
        height (int): Height of the window.
        window_title (str): Title/caption of the window.
        resizable (bool): Whether the user can resize the window.
        antialiasing (bool): Whether to use antialiasing
    """

    global _window
    _window = Window(width, height, window_title, resizable=resizable, antialiasing=antialiasing)
    _window.invalid = False
    return _window


class View:
    """
    A view is a way to separate drawing and logic from the window itself.
    Subclassing the window is very inflexible since you can't easily switch
    your update and draw logic.

    A view is a way to encapsulate that logic so you can easily switch between
    different parts of your game. Maybe you have a title screen, a game screen,
    and a game over screen. Each of these could be a different view.

    Args:
        window (Window, optional): The window this view is associated with. If None,
            the current window is used. (Normally you don't need to provide this).
    """

    def __init__(self, window: Optional[Window] = None) -> None:
        self.window = arcade.get_window() if window is None else window
        self.key: Optional[int] = None
        self._section_manager: Optional[SectionManager] = None

    @property
    def section_manager(self) -> SectionManager:
        """The section manager for this view.

        If the view has section manager one will be created.
        """
        if self._section_manager is None:
            self._section_manager = SectionManager(self)
        return self._section_manager

    @property
    def has_sections(self) -> bool:
        """Returns ``True`` if this view has sections."""
        if self._section_manager is None:
            return False
        else:
            return self.section_manager.has_sections

    def add_section(
        self,
        section: arcade.Section,
        at_index: Optional[int] = None,
        at_draw_order: Optional[int] = None,
    ) -> None:
        """
        Adds a section to the view Section Manager.

        Args:
            section (arcade.Section): The section to add to this section manager
            at_index (int, optional): The index to insert the section for event capture and
                update events. If ``None`` it will be added at the end.
            at_draw_order (int, optional): Inserts the section in a specific draw order.
                Overwrites section.draw_order
        """
        self.section_manager.add_section(section, at_index, at_draw_order)

    def clear(
        self,
        color: Optional[RGBOrA255] = None,
        color_normalized: Optional[RGBANormalized] = None,
        viewport: Optional[tuple[int, int, int, int]] = None,
    ) -> None:
        """
        Clears the window with the configured background color
        set through :py:attr:`arcade.Window.background_color`.

        :param color: (Optional) override the current background color
            with one of the following:

            1. A :py:class:`~arcade.types.Color` instance
            2. A 3 or 4-length RGB/RGBA :py:class:`tuple` of byte values (0 to 255)

        :param color_normalized: (Optional) override the current background color
            using normalized values (0.0 to 1.0). For example, (1.0, 0.0, 0.0, 1.0)
            making the window contents red.

        :param Tuple[int, int, int, int] viewport: The viewport range to clear
        """
        self.window.clear(color=color, color_normalized=color_normalized, viewport=viewport)

    def on_update(self, delta_time: float) -> Optional[bool]:
        """
        This method can be implemented and is reserved for game logic.
        Move sprites. Perform collision checks and other game logic.
        This method is called every frame before :meth:`on_draw`.

        The ``delta_time`` can be used to make sure the game runs at the same
        speed, no matter the frame rate.

        Args:
            delta_time (float): Time interval since the last time the function was
                called in seconds.
        """
        pass

    def on_fixed_update(self, delta_time: float):
        """
        Called for each fixed update. This is useful for physics engines
        and other systems that should update at a constant rate.

        Args:
            delta_time (float): Time interval since the last time the function was
                called in seconds.
        """
        pass

    def on_draw(self) -> Optional[bool]:
        """
        Override this function to add your custom drawing code.

        This method is usually called 60 times a second unless
        another update rate has been set. Should be called after
        :meth:`~arcade.Window.on_update`.

        This function should normally start with a call to
        :meth:`~arcade.Window.clear` to clear the screen.
        """
        pass

    def on_show_view(self) -> None:
        """Called once when the view is shown.

        .. seealso:: :py:meth:`~arcade.View.on_hide_view`
        """
        pass

    def on_hide_view(self) -> None:
        """Called once when this view is hidden."""
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Called repeatedly while the mouse is moving in the window area.

        Override this function to respond to changes in mouse position.

        Args:
            x (int): x position of mouse within the window in pixels
            y (int): y position of mouse within the window in pixels
            dx (int): Change in x since the last time this method was called
            dy (int): Change in y since the last time this method was called
        """
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> Optional[bool]:
        """
        Called once whenever a mouse button gets pressed down.

        Override this function to handle mouse clicks. For an example of
        how to do this, see arcade's built-in :ref:`aiming and shooting
        bullets <sprite_bullets_aimed>` demo.

        Args:
            x (int): x position of the mouse
            y (int): y position of the mouse
            button (int): What button was pressed.
                This will always be one of the following:

                - ``arcade.MOUSE_BUTTON_LEFT``
                - ``arcade.MOUSE_BUTTON_RIGHT``
                - ``arcade.MOUSE_BUTTON_MIDDLE``

            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                      active during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int
    ) -> Optional[bool]:
        """
        Called repeatedly while the mouse moves with a button down.

        Override this function to handle dragging.

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            dx (int): Change in x since the last time this method was called
            dy (int): Change in y since the last time this method was called
            buttons (int): Which button is pressed
            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                              active during this event. See :ref:`keyboard_modifiers`.
        """
        self.on_mouse_motion(x, y, dx, dy)
        return False

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> Optional[bool]:
        """
        Called once whenever a mouse button gets released.

        Override this function to respond to mouse button releases. This
        may be useful when you want to use the duration of a mouse click
        to affect gameplay.

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            button (int): What button was hit. One of:

                - ``arcade.MOUSE_BUTTON_LEFT``
                - ``arcade.MOUSE_BUTTON_RIGHT``
                - ``arcade.MOUSE_BUTTON_MIDDLE``

            modifiers (int): Bitwise 'and' of all modifiers (shift, ctrl, num lock)
                active during this event. See :ref:`keyboard_modifiers`.
        """
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> Optional[bool]:
        """
        Called repeatedly while a mouse scroll wheel moves.

        Override this function to respond to scroll events. The scroll
        arguments may be positive or negative to indicate direction, but
        the units are unstandardized. How many scroll steps you receive
        may vary wildly between computers depending a number of factors,
        including system settings and the input devices used (i.e. mouse
        scrollwheel, touch pad, etc).

        .. warning:: Not all users can scroll easily!

            Only some input devices support horizontal
            scrolling. Standard vertical scrolling is common,
            but some laptop touch pads are hard to use.

            This means you should be careful about how you use
            scrolling. Consider making it optional
            to maximize the number of people who can play your
            game!

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            scroll_x (int): number of steps scrolled horizontally
                     since the last call of this function
            scroll_y (int): number of steps scrolled vertically since
                     the last call of this function
        """
        pass

    def on_key_press(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called once when a key gets pushed down.

        Override this function to add key press functionality.

        .. tip:: If you want the length of key presses to affect
                 gameplay, you also need to override
                 :meth:`~.Window.on_key_release`.

        Args:
            symbol (int): Key that was just pushed down
            modifiers (int): Bitwise 'and' of all modifiers (shift,
                      ctrl, num lock) active during this event.
                      See :ref:`keyboard_modifiers`.
        """
        return False

    def on_key_release(self, _symbol: int, _modifiers: int) -> Optional[bool]:
        """
        Called once when a key gets released.

        Override this function to add key release functionality.

        Situations that require handling key releases include:

        * Rhythm games where a note must be held for a certain
          amount of time
        * 'Charging up' actions that change strength depending on
          how long a key was pressed
        * Showing which keys are currently pressed down

        Args:
            symbol (int): Key that was released
            modifiers (int): Bitwise 'and' of all modifiers (shift,
                      ctrl, num lock) active during this event.
                      See :ref:`keyboard_modifiers`.
        """
        return False

    def on_resize(self, width: int, height: int) -> Optional[bool]:
        """
        Override this method to add custom actions when the window is resized.

        An internal ``_on_resize`` is called first adjusting the viewport
        to the new size of the window so there is no need to call
        ```super().on_resize(width, height)```.

        Args:
            width (int): New width of the window
            height (int): New height of the window
        """
        pass

    def on_mouse_enter(self, x: int, y: int) -> Optional[bool]:
        """
        Called once whenever the mouse enters the window area on screen.

        This event will not be triggered if the mouse is currently being
        dragged.

        Args:
            x (int): The x position the mouse entered the window
            y (int): The y position the mouse entered the window
        """
        pass

    def on_mouse_leave(self, x: int, y: int) -> Optional[bool]:
        """
        Called once whenever the mouse leaves the window area on screen.

        This event will not be triggered if the mouse is currently being
        dragged. Note that the coordinates of the mouse pointer will be
        outside of the window rectangle.

        Args:
            x (int): The x position the mouse entered the window
            y (int): The y position the mouse entered the window
        """
        pass
