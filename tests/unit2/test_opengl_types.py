import pytest
import arcade
from pyglet import gl
from arcade.gl import types, ShaderException

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.use()
    window.close()


def test_attrib_format(ctx):
    attr = types.AttribFormat('test', gl.GL_FLOAT, 4, 4, 0)
    assert attr.bytes_total == 16
    assert repr(attr).startswith('<AttribFormat ')


def test_buffer_description(ctx):
    buffer = ctx.buffer(reserve=16)
    descr = types.BufferDescription(buffer, '4f', ['in_vert'])
    assert descr.buffer == buffer
    assert descr.attributes == ['in_vert']
    assert descr.stride == 16
    assert repr(descr).startswith('<BufferDescription')

    # Use format with wrong number of components
    with pytest.raises(ValueError):
        types.BufferDescription(ctx.buffer(reserve=15), '5f', ['in_vert'])

    # Mismatch length between attribute and format
    with pytest.raises(ShaderException):
        types.BufferDescription(ctx.buffer(reserve=16), '4f 4f', ['in_vert'])
    with pytest.raises(ShaderException):
        types.BufferDescription(ctx.buffer(reserve=16), '4f', ['in_vert', 'in_normal'])

    # FIXME: Non-existing normalized attribute doesn't work
    # types.BufferDescription(ctx.buffer(reserve=16), '4f', ['in_vert'], normalized=['test', 'a', 'b'])

    # Wrong buffer size. It doesn't align with the format
    with pytest.raises(ValueError):
        types.BufferDescription(ctx.buffer(reserve=10), '4f', ['in_vert'])


def test_type_info(ctx):
    tp = types.TypeInfo('test', gl.GL_FLOAT, gl.GLfloat, 4, 4)
    assert tp.size == 16
    assert repr(tp).startswith('<TypeInfo')
