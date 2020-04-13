"""
Temporary module to play with shaders and geometry
"""
import array
from arcade import shader, get_window


def quad_fs(size=(1.0, 1.0), pos=(0.0, 0.0)):
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
    return ctx.geometry(vao_content)


def screen_rectangle(rectangle_size=None,
                     center_pos=None,
                     screen_size=None):
    """ Calculate a rectangle """

    if rectangle_size is None and center_pos is None and screen_size is None:
        rectangle_size = (2.0, 2.0)
        center_pos = (0.0, 0.0)
        screen_size = (2.0, 2.0)
    elif screen_size is None:
        screen_size = (get_window().width, get_window().height)
        if center_pos is None:
            center_pos = (get_window().width / 2.0, get_window().height / 2.0)
    print(f"Size: {screen_size}")
    screen_width, screen_height = screen_size
    quad_width, quad_height = rectangle_size
    normalized_width = quad_width / screen_width * 2
    normalized_height = quad_height / screen_height * 2
    xpos, ypos = center_pos
    normalized_xpos = xpos / (screen_width / 2) - 1
    normalized_ypos = ypos / (screen_height / 2) - 1
    my_array = \
        [
            normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
            normalized_xpos - normalized_width / 2, normalized_ypos - normalized_height / 2, 0.0, 0.0,
            normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
            normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
            normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
            normalized_xpos + normalized_width / 2, normalized_ypos + normalized_height / 2, 1.0, 1.0
        ]
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
    return ctx.geometry(vao_content)
