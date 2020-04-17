"""
Low level tests for OpenGL 3.3 wrappers.
"""
import array
import pytest
import arcade
from arcade.gl import BufferDescription
from arcade.gl.glsl import ShaderSource
from arcade.gl import ShaderException

from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    err_check(window.ctx)
    window.close()


def err_check(ctx):
    error = ctx.error
    if error:
        raise ValueError("Error", error)


def test_buffer_description(ctx):
    # TODO: components > 4
    # TODO: padding
    BufferDescription(
        ctx.buffer(reserve=4 * 8),
        '2f 2f',
        ['in_vert', 'in_uv'],
    )


def test_ctx(ctx):
    assert ctx.gl_version >= (3, 3)
    assert ctx.limits.MAX_TEXTURE_SIZE > 4096
    assert ctx.limits.MAX_ARRAY_TEXTURE_LAYERS >= 256


def test_buffer(ctx):
    """Testing OpenGL buffers"""
    buffer = ctx.buffer(data=b'Hello world')
    assert buffer.glo.value > 0
    assert buffer.ctx == ctx
    assert buffer.read() == b'Hello world'
    assert buffer.read(size=5) == b'Hello'
    assert buffer.read(size=5, offset=6) == b'world'

    # Reading outside buffer by 1 byte
    with pytest.raises(ValueError):
        buffer.read(size=12)

    # Reading outside buffer by 1 byte with offset
    with pytest.raises(ValueError):
        buffer.read(size=6, offset=6)

    # Read with zero or negative size
    with pytest.raises(ValueError):
        buffer.read(0)

    buffer.orphan(size=20)
    assert buffer.size == 20
    assert len(buffer.read()) == 20

    buffer.write(b'Testing')
    assert buffer.read(size=7) == b'Testing'
    buffer.write(b'Testing', offset=10)
    assert buffer.read(offset=10, size=7) == b'Testing'

    # Copy buffer
    source = ctx.buffer(reserve=20)
    buffer.copy_from_buffer(source, size=10, offset=0)
    # Copy out of bounds in the source buffer
    with pytest.raises(ValueError):
        buffer.copy_from_buffer(source, size=10, source_offset=15)

    # Copy out of bounds in the destination buffer
    with pytest.raises(ValueError):
        buffer.copy_from_buffer(source, size=10, offset=15)


def test_geometry(ctx):
    """Test vertex_array"""
    program = ctx.load_program(
        vertex_shader=':resources:shaders/line_vertex_shader_vs.glsl',
        fragment_shader=':resources:shaders/line_vertex_shader_fs.glsl',
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
    vao = ctx.geometry(content)
    assert vao.ctx == ctx
    assert vao.num_vertices == num_vertices
    assert vao.index_buffer is None
    vao.render(program, mode=ctx.TRIANGLES)
    vao.render(program, mode=ctx.POINTS)
    vao.render(program, mode=ctx.LINES)


def test_shader_source(ctx):
    """Test shader source parsing"""
    source_wrapper = ShaderSource(
        """
        #version 330
        #define TEST 10
        #define TEST2 20
        in vec2 in_pos;
        in vec2 in_velocity;
        out vec2 out_pos;
        out vec2 out_velocity;
        void main() {
            out_pos = in_pos;
            out_velocity = in_velocity;
        }
        """,
        gl.GL_VERTEX_SHADER,
    )
    assert source_wrapper.version == 330
    assert source_wrapper.out_attributes == ['out_pos', 'out_velocity']
    source = source_wrapper.get_source(defines={'TEST': 1, 'TEST2': '2'})
    assert '#define TEST 1' in source
    assert '#define TEST2 2' in source


def test_program(ctx):
    """Test program"""
    program = ctx.program(
        vertex_shader="""
        #version 330

        uniform vec2 pos_offset;

        in vec2 in_vert;
        in vec2 in_uv;
        out vec2 v_uv;

        void main() {
            gl_Position = vec4(in_vert + pos_offset, 0.0, 1.0);
            v_uv = in_uv;
        }
        """,
        fragment_shader="""
        #version 330

        out vec4 f_color;
        in vec2 v_uv;

        void main() {
            f_color = vec4(v_uv, 0.0, 1.0);
        }
        """,
    )
    assert program.ctx == ctx
    assert program.glo > 0
    program.use()
    assert ctx.active_program == program

    # TODO: Test all uniform types
    program['pos_offset'] = 1, 2
    assert program['pos_offset'] == (1.0, 2.0)
    with pytest.raises(ShaderException):
        program['this_uniform_do_not_exist'] = 0

    # Program with only vertex shader
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_pos;
        out vec2 out_pos;

        void main() {
            out_pos = in_pos + vec2(1.0);
        }
        """,
    )

    # Program with geometry shader
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 pos;
        void main() {
            gl_Position = vec4(pos, 0.0, 1.0);
        }
        """,
        geometry_shader="""
        #version 330

        layout (points) in;
        layout (triangle_strip, max_vertices = 2) out;

        void main() {
            gl_Position = gl_in[0].gl_Position + vec4(-0.1, 0.0, 0.0, 0.0);
            EmitVertex();

            gl_Position = gl_in[0].gl_Position + vec4( 0.1, 0.0, 0.0, 0.0);
            EmitVertex();

            EndPrimitive();
        }
        """,
    )
    assert program.geometry_input == ctx.POINTS
    assert program.geometry_output == ctx.TRIANGLE_STRIP
    assert program.geometry_vertices == 2

    # Uniform testing
    # .. mother of all uniform programs trying to cram in as many as possible!
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_pos;
        in vec2 in_velocity;
        out vec2 out_pos;
        out vec2 out_velocity;

        void main() {
            out_pos = in_pos + vec2(1.0);
            out_velocity = in_pos * 0.99;
        }
        """,
    )
    assert program.out_attributes == ['out_pos', 'out_velocity']


def test_texture(ctx):
    """Test textures"""
    texture = ctx.texture(
        (100, 200),
        components=4,
        filter=(ctx.NEAREST, ctx.NEAREST),
        wrap_x=ctx.CLAMP_TO_EDGE,
        wrap_y=ctx.REPEAT,
    )
    assert texture.ctx == ctx
    assert texture.glo.value > 0
    assert texture.components == 4
    assert texture.width == 100
    assert texture.height == 200
    assert texture.size == (100, 200)
    assert texture.filter == (ctx.NEAREST, ctx.NEAREST)
    assert texture.wrap_x == ctx.CLAMP_TO_EDGE
    assert texture.wrap_y == ctx.REPEAT
    texture.use(0)
    texture.use(1)
    texture.use(2)

    # Make an unreasonable texture
    with pytest.raises(Exception):
        ctx.texture((100_000, 1), 1)

    # Create textures of different components
    c1 = ctx.texture((10, 10), components=1)
    c2 = ctx.texture((10, 10), components=2)
    c3 = ctx.texture((10, 10), components=3)
    c4 = ctx.texture((10, 10), components=4)
    assert c1.components == 1
    assert c2.components == 2
    assert c3.components == 3
    assert c4.components == 4

    # Wrong number of components
    with pytest.raises(ValueError):
        ctx.texture((10, 10), components=5)

    # Create textures using different formats
    def test_texture_format(dtype):
        for components in range(1, 5):
            texture = ctx.texture((10, 10), components=components, dtype=dtype)
            assert texture.ctx == ctx
            assert texture.glo.value > 0
            assert texture.components == components
            assert texture.dtype == dtype

    test_texture_format('f1')
    test_texture_format('f2')
    test_texture_format('f4')

    test_texture_format('i1')
    test_texture_format('i2')
    test_texture_format('i4')

    test_texture_format('u1')
    test_texture_format('u2')
    test_texture_format('u4')

    # Writing to texture
    data = array.array('f', list(range(10))).tobytes()
    texture = ctx.texture((10, 1), components=1, dtype='f4')
    texture.write(data)
    assert texture.read() == data

    buffer = ctx.buffer(data=data)
    texture.write(buffer)
    assert texture.read() == data


def test_framebuffer(ctx):
    """Test framebuffers"""
    fb = ctx.framebuffer(
        color_attachments=[
            ctx.texture((10, 20), components=4),
            ctx.texture((10, 20), components=4)])
    print(fb)
    fb.use()
    assert fb.ctx == ctx
    assert fb.width == 10
    assert fb.height == 20
    assert fb.size == (10, 20)
    assert fb.samples == 0
    assert fb.viewport == (0, 0, 10, 20)
    assert len(fb.color_attachments) == 2
    assert fb.depth_attachment is None
    assert fb.depth_mask is True
    fb.viewport = (1, 2, 3, 4)
    assert fb.viewport == (1, 2, 3, 4)
    fb.viewport = (1, 2)
    assert fb.viewport == (0, 0, 1, 2)
    with pytest.raises(ValueError):
        fb.viewport = 0

    # Ensure bind tracking works
    assert ctx.active_framebuffer == fb
    ctx.window.use()
    ctx.window.use()  # Twice to trigger bind check
    assert ctx.active_framebuffer == ctx.window
    fb.clear()
    fb.clear(color=(0, 0, 0, 0), normalized=False)
    fb.clear(color=(0, 0, 0), normalized=False)
    fb.clear(color=arcade.csscolor.AZURE)
    fb.clear(color=(0, 0, 0, 0))
    assert ctx.active_framebuffer == ctx.window

    # Varying attachment sizes not supported for now
    with pytest.raises(ValueError):
        ctx.framebuffer(
            color_attachments=[
                ctx.texture((10, 10), components=4),
                ctx.texture((10, 11), components=4)])

    # Incomplete framebuffer
    with pytest.raises(ValueError):
        ctx.framebuffer()
