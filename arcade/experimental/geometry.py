"""
Temporary module to play with shaders and geometry
"""
import array
from arcade import shader, get_window
import pyglet.gl as gl


def quad_fs(program, size=(1.0, 1.0), pos=(0.0, 0.0)):
    width, height = size
    xpos, ypos = pos
    my_array = \
        [
            xpos - width / 2.0, ypos + height / 2.0, 0.0, 1.0,
            xpos - width / 2.0, ypos - height / 2.0, 0.0, 0.0,
            xpos + width / 2.0, ypos - height / 2.0, 1.0, 0.0,
            xpos - width / 2.0, ypos + height / 2.0, 0.0, 1.0,
            xpos + width / 2.0, ypos - height / 2.0, 1.0, 0.0,
            xpos + width / 2.0, ypos + height / 2.0, 1.0, 1.0
        ]
    print(my_array)
    data = array.array('f', my_array)

    ctx = get_window().ctx
    vbo = ctx.buffer(data=data.tobytes())
    vao_content = [
        shader.BufferDescription(
            vbo,
            '2f 2f',
            ('in_vert', 'in_uv'),
        )
    ]
    return Thingy(ctx.vertex_array(program, vao_content), program, vbo)


def screen_rectangle(program,
                     rectangle_size=(2.0, 2.0),
                     center_pos=(0.0, 0.0),
                     screen_size=(2.0, 2.0)):
    """ Calculate a rectangle """

    screen_width, screen_height = screen_size
    quad_width, quad_height = rectangle_size
    normalized_width = quad_width / screen_width * 2
    normalized_height = quad_height / screen_height * 2
    xpos, ypos = center_pos
    normalized_xpos = xpos / (screen_width / 2) - 1
    normalized_ypos = ypos / (screen_height / 2) - 1
    print(normalized_height, normalized_ypos, ypos)
    my_array = \
        [
            normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
            normalized_xpos - normalized_width / 2, normalized_ypos - normalized_height / 2, 0.0, 0.0,
            normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
            normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
            normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
            normalized_xpos + normalized_width / 2, normalized_ypos + normalized_height / 2, 1.0, 1.0
        ]
    print(my_array)
    data = array.array('f', my_array)

    ctx = get_window().ctx
    vbo = ctx.buffer(data=data.tobytes())
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
