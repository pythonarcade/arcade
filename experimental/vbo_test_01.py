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


class VertexBuffer():
    """ Class to hold vertex buffer info. """
    def __init__(self, vbo_id, size, width, height, color):
        self.vbo_id = vbo_id
        self.size = size
        self.width = width
        self.height = height
        self.color = color


def create_rect(width, height, color):
    """ Create a vertex buffer for a rectangle. """
    v2f = [-width / 2, -height / 2,
            width / 2, -height / 2,
            width / 2, height / 2,
            -width / 2, height / 2]

    vbo_id = GL.GLuint()

    GL.glGenBuffers(1, ctypes.pointer(vbo_id))

    data2 = (GL.GLfloat*len(v2f))(*v2f)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2, GL.GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(v2f)//2, width, height, color)
    return shape


def render_rect_filled(shape, x, y):
    """ Render the shape at the right spot. """
    # Set color
    GL.glDisable(GL.GL_BLEND)
    GL.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, shape.vbo_id)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, 0)

    GL.glLoadIdentity()
    GL.glTranslatef(x + shape.width / 2, y + shape.height / 2, 0)

    GL.glDrawArrays(GL.GL_QUADS, 0, shape.size)


class Rectangle():

    def __init__(self, x, y, width, height, delta_x, delta_y, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.color = color
        self.vbo = create_rect(self.width, self.height, self.color)

    def move(self):
        self.x += self.delta_x
        self.y += self.delta_y

    def draw(self):
        render_rect_filled(self.vbo, self.x, self.y)


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
            shape = Rectangle(x, y, width, height, d_x, d_y, (red, green, blue))
            self.shape_list.append(shape)

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

        for shape in self.shape_list:
            shape.draw()

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