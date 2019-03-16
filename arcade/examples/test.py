SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

import pyglet
from pyglet.gl import *
from pyglet import clock
import time

class MyGame(pyglet.window.Window):

    def __init__(self, width, height):
        config = Config(sample_buffers=1,
                        samples=16,
                        double_buffer=True)

        super().__init__(width, height,
                         config=config)
        glEnable(GL_MULTISAMPLE_ARB)

    def on_draw(self):
        print("Ok")
        # arcade.start_render()

        size = self.height / 4
        # glClear(GL_COLOR_BUFFER_BIT)
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLoadIdentity()
        glTranslatef(self.width/2, self.height/2, 0)
        glRotatef(5, 0, 0, 1)

        glColor3f(1, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(-size, -size)
        glVertex2f(size, -size)
        glVertex2f(size, size)
        glVertex2f(-size, size)
        glEnd()



def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)

    # while True:
    #     window.on_draw()
    #     window.flip()
    #     window.dispatch_events()
    pyglet.app.run()


if __name__ == "__main__":
    main()
