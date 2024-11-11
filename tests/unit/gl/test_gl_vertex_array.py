"""
Low level tests for OpenGL 3.3 wrappers.
"""
import array
import struct
import pytest
from arcade.gl import BufferDescription
from arcade.gl.vertex_array import VertexArray
from arcade.gl.program import Program


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


def test_padding(ctx):\
    ctx.geometry([BufferDescription(
        ctx.buffer(reserve=4 * 7 * 10),
        '2f 3x4 2f',
        ('in_pos', 'in_vel'),
    )])


def test_transform(ctx):
    """Test basic transform"""
    program = ctx.program(vertex_shader="""
        #version 330
        out float value;
        void main() {
            value = float(gl_VertexID);
        }
        """
    )
    buffer = ctx.buffer(reserve=4 * 5)
    vao = ctx.geometry()
    vao.transform(program, buffer, vertices=5)
    assert struct.unpack('5f', buffer.read()) == (0.0, 1.0, 2.0, 3.0, 4.0)


def test_index_buffer_32bit(ctx):
    """Create a vao with 32 bit index buffer"""
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
        }
        """,
        fragment_shader="""
        #version 330
        out vec4 color;
        void main() {
            color = vec4(1.0);
        }
        """,
    )
    vertex_buffer = ctx.buffer(data=array.array('f', [0.0] * 2 * 4))
    ibo = ctx.buffer(data=array.array('I', [0, 1, 2, 0, 1, 3]))
    vao = ctx.geometry(
        [
            BufferDescription(vertex_buffer, "2f", ["in_position"]),
        ],
        index_buffer=ibo,
        index_element_size=4,
        mode=ctx.TRIANGLES,
    )
    assert vao.ctx == ctx
    assert vao.num_vertices == 6
    assert vao.index_buffer == ibo
    vao.render(program)


def test_index_buffer_16bit(ctx):
    """Create a vao with 16 bit index buffer"""
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
        }
        """,
        fragment_shader="""
        #version 330
        out vec4 color;
        void main() {
            color = vec4(1.0);
        }
        """,
    )
    vertex_buffer = ctx.buffer(data=array.array('f', [0.0] * 2 * 4))
    ibo = ctx.buffer(data=array.array('H', [0, 1, 2, 0, 1, 3]))
    vao = ctx.geometry(
        [
            BufferDescription(vertex_buffer, "2f", ["in_position"]),
        ],
        index_buffer=ibo,
        index_element_size=2,
        mode=ctx.TRIANGLES,
    )
    assert vao.ctx == ctx
    assert vao.num_vertices == 6
    assert vao.index_buffer == ibo
    vao.render(program)


def test_index_buffer_8bit(ctx):
    """Create a vao with 8 bit index buffer"""
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
        }
        """,
        fragment_shader="""
        #version 330
        out vec4 color;
        void main() {
            color = vec4(1.0);
        }
        """,
    )
    vertex_buffer = ctx.buffer(data=array.array('f', [0.0] * 2 * 4))
    ibo = ctx.buffer(data=array.array('B', [0, 1, 2, 0, 1, 3]))
    vao = ctx.geometry(
        [
            BufferDescription(vertex_buffer, "2f", ["in_position"]),
        ],
        index_buffer=ibo,
        index_element_size=1,
        mode=ctx.TRIANGLES,
    )
    assert vao.ctx == ctx
    assert vao.num_vertices == 6
    assert vao.index_buffer == ibo
    vao.render(program)


def test_index_buffer_incorrect_type_size(ctx):
    """Attempt to use an illegal index buffer type size"""
    for size in [0, 3, 5]:
        with pytest.raises(ValueError):
            ctx.geometry(
                [
                    BufferDescription(ctx.buffer(reserve=16), "2f", ["in_position"]),
                ],
                index_buffer=ctx.buffer(reserve=16),
                index_element_size=size,
            )


def test_incomplete_geometry(ctx):
    ctx.geometry()


def test_appending_extra_buffer_description(ctx):
    """Attempt to append a BufferDescription with the same attribute name"""
    with pytest.raises(ValueError):
        geometry = ctx.geometry(
            [
                BufferDescription(ctx.buffer(reserve=16), "2f", ['in_position'])
            ]
        )
        geometry.append_buffer_description(BufferDescription(ctx.buffer(reserve=16), '4f', ['in_position']))


def test_vertex_array_wrong_attrib_mapping(ctx):
    """Attempt to map an float buffer into an int attribute"""
    geometry =ctx.geometry(
        [BufferDescription(ctx.buffer(reserve=16), '2f', ['in_pos'])]
    )
    program = ctx.program(
        vertex_shader="""
            #version 330
            in ivec2 in_pos;
            out ivec2 out_pos;
            void main() {
                out_pos = in_pos;
            }
        """,
    )
    with pytest.raises(ValueError, match="GL_INT"):
        geometry.transform(program, ctx.buffer(reserve=16))
