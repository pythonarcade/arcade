"""
Low level tests for OpenGL 3.3 wrappers.
"""
import array
import pytest
import arcade
from arcade.gl import BufferDescription
from arcade.gl.vertex_array import VertexArray
from arcade.gl.program import Program

from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.close()


def test_buffer_description(ctx):
    # TODO: components > 4
    # TODO: padding
    BufferDescription(
        ctx.buffer(reserve=4 * 8),
        '2f 2f',
        ['in_vert', 'in_uv'],
    )


# TODO: Instanced
# TODO: tranform
# TODO: index buffer


def test_geometry(ctx):
    """Test vertex_array"""
    program = ctx.load_program(
        vertex_shader=':resources:shaders/shapes/line/line_vertex_shader_vs.glsl',
        fragment_shader=':resources:shaders/shapes/line/line_vertex_shader_fs.glsl',
    )
    num_vertices = 100
    content = [
        BufferDescription(
            ctx.buffer(reserve=4 * num_vertices),
            '4f1',
            ['in_color'],
            normalized=['in_color'],
        ),
        BufferDescription(
            ctx.buffer(reserve=8 * num_vertices),
            '2f',
            ['in_vert']
        ),
    ]
    geo = ctx.geometry(content)
    assert geo.ctx == ctx
    assert geo.num_vertices == num_vertices
    assert geo.index_buffer is None
    geo.render(program, mode=ctx.TRIANGLES)
    geo.render(program, mode=ctx.POINTS)
    geo.render(program, mode=ctx.LINES)

    vao = geo.instance(program)
    assert isinstance(vao, VertexArray)
    assert isinstance(vao.program, Program)
    assert vao.num_vertices == -1
    assert vao.ibo is None
    geo.flush()
    with pytest.raises(NotImplementedError):
        geo.transform(program)


def test_incomplete_geometry(ctx):
    with pytest.raises(ValueError):
        ctx.geometry(None)
    with pytest.raises(ValueError):
        ctx.geometry([])
