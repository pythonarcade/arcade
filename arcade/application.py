from .window_commands import *


class ArcadeApplication():
    """
    Main application class for an Arcade application.

    :Example

    >>> import arcade
    >>>
    >>> class MyApplication(arcade.ArcadeApplication):
    ...
    ...     def __init__(self):
    ...         pass
    ...
    ...     def render(self):
    ...         arcade.start_render()
    ...         # Draw stuff here
    ...         arcade.swap_buffers()
    ...
    ...     def key_pressed(self, key, x, y):
    ...         pass
    ...
    ...     def special_pressed(self, key, x, y):
    ...         pass
    ...
    ...     def special_released(self, key, x, y):
    ...         pass
    ...
    ...     def animate(self):
    ...         # Update items here
    ...         arcade.redisplay()
    ...
    ...     def run(self):
    ...         self.open_window(500, 500)
    ...
    ...         # Enable the line below to keep the window up.
    ...         # Disabled now for automated tests.
    ...         # arcade.run()
    >>>
    >>> app = MyApplication()
    >>> app.run()
    """

    def open_window(self, width, height):
        """ Set up the window """
        open_window("Arcade Window", width, height)

        set_render_function(self.render)
        GLUT.glutIdleFunc(self.animate)
        set_resize_window_function(default_resize_window_function)
        set_keyboard_handler_function(self.key_pressed)

        GLUT.glutSpecialUpFunc(self.special_released)
        GLUT.glutSpecialFunc(self.special_pressed)

    def render(self):
        pass

    def animate(self):
        pass

    def key_pressed(self, key, x, y):
        pass

    def special_pressed(self, key, x, y):
        pass

    def special_released(self, key, x, y):
        pass
