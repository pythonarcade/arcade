from .window_commands import *


class ArcadeApplication():
    """ Main application class for an Arcade application. """

    def open_window(self, width, height):
        """ Set up the window """
        open_window("Arcade Window", width, height)

        set_render_function(self.render)
        GLUT.glutIdleFunc(self.animate)
        set_resize_window_function(default_resize_window_function)
        GLUT.glutKeyboardFunc(self.key_pressed)

        GLUT.glutSpecialUpFunc(self.special_released)
        GLUT.glutSpecialFunc(self.special_pressed)

    def render(self):
        pass

    def animate(self):
        pass
