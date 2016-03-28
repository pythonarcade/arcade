"""
This example uses OpenGL via Pyglet and draws
a bunch of rectangles on the screen.
"""

import random
import time
import pyglet.gl as GL
import pyglet
import ctypes

# Set up the constants
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

RECT_WIDTH = 50
RECT_HEIGHT = 50


def render_rect_filled(shape, offset):
    """ Render the shape at the right spot. """
    # Set color
    GL.glLoadIdentity()
    GL.glColor3ub(shape.color[0], shape.color[1], shape.color[2])

    GL.glTranslatef(shape.x + shape.width / 2, shape.y + shape.height / 2, 0)

    GL.glDrawArrays(GL.GL_QUADS, offset, 4)


class Rectangle():

    def __init__(self, x, y, width, height, delta_x, delta_y, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.color = color

    def move(self):
        self.x += self.delta_x
        self.y += self.delta_y


def create_rects(rect_list):
    """ Create a vertex buffer for a set of rectangles. """

    v2f = []
    for shape in rect_list:
        v2f.extend([-shape.width / 2, -shape.height / 2,
                   shape.width / 2, -shape.height / 2,
                   shape.width / 2, shape.height / 2,
                   -shape.width / 2, shape.height / 2])

    vbo_id = GL.GLuint()

    GL.glGenBuffers(1, ctypes.pointer(vbo_id))

    data2 = (GL.GLfloat*len(v2f))(*v2f)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    GL.GL_STATIC_DRAW)

    return vbo_id


class MyApplication():
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Set background to white
        GL.glClearColor(1, 1, 1, 1)

        self.shape_list = []

        for i in range(2000):
            x = random.randrange(0, SCREEN_WIDTH)
            y = random.randrange(0, SCREEN_HEIGHT)
            width = random.randrange(20, 71)
            height = random.randrange(20, 71)

            d_x = random.randrange(-3, 4)
            d_y = random.randrange(-3, 4)

            red = random.randrange(256)
            green = random.randrange(256)
            blue = random.randrange(256)
            alpha = random.randrange(256)
            shape_type = random.randrange(2)
            shape = Rectangle(x, y, width, height, d_x, d_y,
                              (red, green, blue))
            self.shape_list.append(shape)

        self.vertex_vbo_id = create_rects(self.shape_list)

    def animate(self, dt):
        """ Move everything """

        for shape in self.shape_list:
            shape.move()

    def on_draw(self):
        """
        Render the screen.
        """
        start = time.time()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        GL.glDisable(GL.GL_BLEND)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_vbo_id)
        GL.glVertexPointer(2, GL.GL_FLOAT, 0, 0)

        offset = 0
        for shape in self.shape_list:
            render_rect_filled(shape, offset)
            offset += 4

        elapsed = time.time() - start
        print(elapsed)


def main():
    window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
    app = MyApplication()
    app.setup()
    pyglet.clock.schedule_interval(app.animate, 1/60)

    @window.event
    def on_draw():
        window.clear()
        app.on_draw()

    pyglet.app.run()

main()
