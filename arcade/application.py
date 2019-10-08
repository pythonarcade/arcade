"""
The main window class that all object-oriented applications should
derive from.
"""
import time

from numbers import Number
from typing import Tuple, List, Optional
from arcade import gui

import pyglet.gl as gl
import pyglet

from arcade.window_commands import (get_viewport, set_viewport, set_window)

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 4

_window: 'Window'


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

    def __init__(self, width: int = 800, height: int = 600,
                 title: str = 'Arcade Window', fullscreen: bool = False,
                 resizable: bool = False, update_rate: Optional[float] = 1/60,
                 antialiasing: bool = True):
        """
        Construct a new window

        :param int width: Window width
        :param int height: Window height
        :param str title: Title (appears in title bar)
        :param bool fullscreen: Should this be full screen?
        :param bool resizable: Can the user resize the window?
        :param float update_rate: How frequently to update the window.
        :param bool antialiasing: Should OpenGL's anti-aliasing be enabled?
        """
        if antialiasing:
            config = pyglet.gl.Config(major_version=3,
                                      minor_version=3,
                                      double_buffer=True,
                                      sample_buffers=1,
                                      samples=4)
        else:
            config = pyglet.gl.Config(major_version=3,
                                      minor_version=3,
                                      double_buffer=True)

        try:
            super().__init__(width=width, height=height, caption=title,
                             resizable=resizable, config=config)
        except pyglet.window.NoSuchConfigException:
            raise NoOpenGLException("Unable to create an OpenGL 3.3+ context. "
                                    "Check to make sure your system supports OpenGL 3.3 or higher.")

        if antialiasing:
            try:
                gl.glEnable(gl.GL_MULTISAMPLE_ARB)
            except pyglet.gl.GLException:
                print("Warning: Anti-aliasing not supported on this computer.")

        # Required for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        if update_rate:
            from pyglet import compat_platform
            if compat_platform == 'darwin' or compat_platform == 'linux':
                # Set vsync to false, or we'll be limited to a 1/30 sec update rate possibly
                self.context.set_vsync(False)
            self.set_update_rate(update_rate)

        super().set_fullscreen(fullscreen)
        self.invalid = False
        set_window(self)
        set_viewport(0, self.width, 0, self.height)
        self.current_view: Optional[View] = None
        self.button_list: List[gui.TextButton] = []
        self.dialogue_box_list: List[gui.DialogueBox] = []
        self.text_list: List[gui.Text] = []
        self.textbox_list: List[gui.TextBox] = []
        self.textbox_time = 0.0
        self.key: Optional[int] = None

    def update(self, delta_time: float):
        """
        Move everything. For better consistency in naming, use ``on_update`` instead.

        :param float delta_time: Time interval since the last time the function was called in seconds.

        """
        if self.current_view is not None:
            self.current_view.update(delta_time)

    def on_update(self, delta_time: float):
        """
        Move everything. Perform collision checks. Do all the game logic here.

        :param float delta_time: Time interval since the last time the function was called.

        """
        if self.current_view is not None:
            self.current_view.on_update(delta_time)
        try:
            self.textbox_time += delta_time
            seconds = self.textbox_time % 60
            if seconds >= 0.115:
                if self.textbox_list:
                    for textbox in self.textbox_list:
                        textbox.update(delta_time, self.key)
                    self.textbox_time = 0.0
        except AttributeError:
            pass

    def set_update_rate(self, rate: float):
        """
        Set how often the screen should be updated.
        For example, self.set_update_rate(1 / 60) will set the update rate to 60 fps

        :param float rate: Update frequency in seconds
        """
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule_interval(self.update, rate)
        pyglet.clock.unschedule(self.on_update)
        pyglet.clock.schedule_interval(self.on_update, rate)

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
        :param int modifiers: Shift/click, ctrl/click, etc.
        """
        try:
            if self.button_list:
                for button_widget in self.button_list:
                    if button_widget.active:
                        button_widget.check_mouse_press(x, y)
        except AttributeError:
            pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_mouse_press(x, y, button, modifiers)
        except AttributeError:
            pass
        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.check_mouse_press(x, y)
        except AttributeError:
            pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        :param int buttons: Which button is pressed
        :param int modifiers: Ctrl, shift, etc.
        """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x:
        :param float y:
        :param int button:
        :param int modifiers:
        """
        try:
            if self.button_list:
                for button_widget in self.button_list:
                    if button_widget.active:
                        button_widget.check_mouse_release(x, y)
        except AttributeError:
            pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_mouse_release(x, y, button, modifiers)
        except AttributeError:
            pass
        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.check_mouse_release(x, y)
        except AttributeError:
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
        :param int modifiers: If it was shift/ctrl/alt
        """
        try:
            self.key = symbol
        except AttributeError:
            pass

    def on_key_release(self, symbol: int, modifiers: int):
        """
        Override this function to add key release functionality.

        :param int symbol: Key that was hit
        :param int modifiers: If it was shift/ctrl/alt
        """
        try:
            self.key = None
        except AttributeError:
            pass

    def on_draw(self):
        """
        Override this function to add your custom drawing code.
        """
        try:
            if self.button_list:
                for button in self.button_list:
                    if button.active:
                        button.draw()
        except AttributeError:
            pass
        try:
            if self.text_list:
                for text in self.text_list:
                    if text.active:
                        text.draw()
        except AttributeError:
            pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_draw()
        except AttributeError:
            pass
        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.draw()
        except AttributeError:
            pass

    def on_resize(self, width: float, height: float):
        """
        Override this function to add custom code to be called any time the window
        is resized.

        :param float width: New width
        :param float height: New height
        """
        # This breaks on Linux.
        # See https://github.com/pyglet/pyglet/issues/76
        # super().on_resize(width, height)

        original_viewport = self.get_viewport()

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
            self.update(1 / 60)

    def show_view(self, new_view: 'View'):
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
        if self.current_view is not None:
            self.remove_handlers(self.current_view)

        # push new view's handlers
        self.current_view = new_view
        self.push_handlers(self.current_view)
        self.current_view.on_show()

        # Note: After the View has been pushed onto pyglet's stack of event handlers (via push_handlers()), pyglet
        # will still call the Window's event handlers. (See pyglet's EventDispatcher.dispatch_event() implementation
        # for details)

    def _create(self):
        super()._create()

    def _recreate(self, changes):
        super()._recreate(changes)

    def flip(self):
        super().flip()

    def switch_to(self):
        super().switch_to()

    def set_caption(self, caption):
        super().set_caption(caption)

    def set_minimum_size(self, width, height):
        super().set_minimum_size(width, height)

    def set_maximum_size(self, width, height):
        super().set_maximum_size(width, height)

    def set_location(self, x, y):
        super().set_location(x, y)

    def activate(self):
        super().activate()

    def minimize(self):
        super().minimize()

    def maximize(self):
        super().maximize()

    def set_vsync(self, vsync):
        super().set_vsync(vsync)

    def set_mouse_platform_visible(self, platform_visible=None):
        super().set_mouse_platform_visible(platform_visible)

    def set_exclusive_mouse(self, exclusive=True):
        super().set_exclusive_mouse(exclusive)

    def set_exclusive_keyboard(self, exclusive=True):
        super().set_exclusive_keyboard(exclusive)

    def get_system_mouse_cursor(self, name):
        super().get_system_mouse_cursor(name)

    def dispatch_events(self):
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
    return _window


class View:
    """
    TODO:Thoughts:
    - is there a need for a close()/on_close() method?
    """
    def __init__(self):
        self.window = None
        self.button_list: List[gui.TextButton] = []
        self.dialogue_box_list: List[gui.DialogueBox] = []
        self.text_list: List[gui.Text] = []
        self.textbox_time = 0.0
        self.textbox_list: List[gui.TextBox] = []
        self.key = None

    def update(self, delta_time: float):
        """To be overridden"""
        try:
            self.textbox_time += delta_time
            seconds = self.textbox_time % 60
            if seconds >= 0.115:
                if self.textbox_list:
                    for textbox in self.textbox_list:
                        textbox.update(delta_time, self.key)
                    self.textbox_time = 0.0
        except AttributeError:
            pass

    def on_update(self, delta_time: float):
        """To be overridden"""
        pass

    def on_draw(self):
        """Called when this view should draw"""
        try:
            if self.button_list:
                for button in self.button_list:
                    button.draw()
        except AttributeError:
            pass
        try:
            if self.text_list:
                for text in self.text_list:
                    text.draw()
        except AttributeError:
            pass
        pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_draw()
        except AttributeError:
            pass
        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.draw()
        except AttributeError:
            pass

    def on_show(self):
        """Called when this view is shown"""
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
        :param int modifiers: Shift/click, ctrl/click, etc.
        """
        try:
            if self.button_list:
                for button_widget in self.button_list:
                    button_widget.check_mouse_press(x, y)
        except AttributeError:
            pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_mouse_press(x, y, button, modifiers)
        except AttributeError:
            pass

        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.check_mouse_press(x, y)
        except AttributeError:
            pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        :param int _buttons: Which button is pressed
        :param int _modifiers: Ctrl, shift, etc.
        """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """
        Override this function to add mouse button functionality.

        :param float x:
        :param float y:
        :param int button:
        :param int modifiers:
        """
        try:
            if self.button_list:
                for button_widget in self.button_list:
                    button_widget.check_mouse_release(x, y)
        except AttributeError:
            pass
        try:
            if self.dialogue_box_list:
                for dialogue_box in self.dialogue_box_list:
                    if dialogue_box.active:
                        dialogue_box.on_mouse_release(x, y, button, modifiers)
        except AttributeError:
            pass
        try:
            if self.textbox_list:
                for textbox in self.textbox_list:
                    textbox.check_mouse_release(x, y)
        except AttributeError:
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
        :param int modifiers: If it was shift/ctrl/alt
        """
        try:
            self.key = symbol
        except AttributeError:
            pass

    def on_key_release(self, _symbol: int, _modifiers: int):
        """
        Override this function to add key release functionality.

        :param int _symbol: Key that was hit
        :param int _modifiers: If it was shift/ctrl/alt
        """
        try:
            self.key = None
        except AttributeError:
            pass
