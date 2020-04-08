"""
Temporary module to play with shaders and geometry
"""
import numpy
from arcade import shader, get_window
import pyglet.gl as gl


def quad_fs(program, size=(1.0, 1.0), pos=(0.0, 0.0)):
    width, height = size
    xpos, ypos = pos
    data = numpy.array([
        xpos - width / 2.0, ypos + height / 2.0, 0.0, 1.0,
        xpos - width / 2.0, ypos - height / 2.0, 0.0, 0.0,
        xpos + width / 2.0, ypos - height / 2.0, 1.0, 0.0,
        xpos - width / 2.0, ypos + height / 2.0, 0.0, 1.0,
        xpos + width / 2.0, ypos - height / 2.0, 1.0, 0.0,
        xpos + width / 2.0, ypos + height / 2.0, 1.0, 1.0
    ], dtype=numpy.float32)

    ctx = get_window().ctx
    vbo = ctx.buffer(data.tobytes())
    vao_content = [
        shader.BufferDescription(
            vbo,
            '2f 2f',
            ('in_vert', 'in_uv'),
        )
    ]
    return Thingy(ctx.vertex_array(program, vao_content), program, vbo)


class Thingy:
    """Some stupid wrapper!"""
    def __init__(self, vao, program, buffer):
        self.vao = vao
        self.program = program
        self.buffer = buffer

    def render(self):
        self.vao.render(gl.GL_TRIANGLES)
