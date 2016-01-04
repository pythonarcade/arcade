from .window_commands import *


class ArcadeApplication():
    """ Main application class for an Arcade application. """

    def open_window(self):
        """ Set up the window """
        open_window("Arcade Window", 1700, 1000)

        GLUT.glutDisplayFunc(self.render)
        GLUT.glutIdleFunc(self.animate)
        GLUT.glutReshapeFunc(self.reshape)
        GLUT.glutKeyboardFunc(self.key_pressed)

        GLUT.glutSpecialUpFunc(self.special_released)
        GLUT.glutSpecialFunc(self.special_pressed)

    def reshape(self, width, height):
        """ Called when the window is resized. """
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        ratio = width / height
        GL.glOrtho(-1 * ratio, 1 * ratio, -1, 1, -1, 1)
