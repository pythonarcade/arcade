# https://sites.google.com/site/swinesmallpygletexamples/vbo-triangle

import pyglet
from pyglet.gl import *
from ctypes import pointer, sizeof


class VertexBuffer():
    def __init__(self, vbo_id, size, width, height,):
        self.vbo_id = vbo_id
        self.size = size
        self.width = width
        self.height = height


def create_rect(width, height):
    data = [0, 0,
            width, 0,
            width, height,
            0, height]

    vbo_id = GLuint()

    glGenBuffers(1, pointer(vbo_id))

    v2f = data
    data2 = (GLfloat*len(v2f))(*v2f)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
    glBufferData(GL_ARRAY_BUFFER, sizeof(data2), data2, GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(v2f)//2, width, height)
    return shape


def render_rect_filled(shape, x, y, angle=0):
    glBindBuffer(GL_ARRAY_BUFFER, shape.vbo_id)
    glVertexPointer(2, GL_FLOAT, 0, 0)

    glLoadIdentity()
    glTranslatef(x + shape.width // 2, y + shape.height // 2, 0)
    if angle:
        glRotatef(angle, 0, 0, 1)
    glTranslatef(-shape.width // 2, -shape.height // 2, 0)

    glDrawArrays(GL_QUADS, 0, shape.size)


window = pyglet.window.Window(width=400, height=400)

glClearColor(0.2, 0.4, 0.5, 1.0)

glEnableClientState(GL_VERTEX_ARRAY)


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0, 0, 0)
    render_rect_filled(shape, 0, 0, 0)

shape = create_rect(50, 50)


pyglet.app.run()
