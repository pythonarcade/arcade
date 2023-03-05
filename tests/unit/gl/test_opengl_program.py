import struct
import pytest
import arcade
from pyglet import gl
from pyglet.math import Mat4
from arcade.gl import ShaderException
from arcade.gl.uniform import UniformBlock
from arcade.gl.glsl import ShaderSource


def test_shader_source(ctx):
    """Test shader source parsing"""
    source_wrapper = ShaderSource(
        ctx,
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
        None,
        gl.GL_VERTEX_SHADER,
    )
    if ctx.gl_api == "gl":
        assert source_wrapper.version == 330
    elif ctx.gl_api == "gles":
        assert source_wrapper.version == 310

    assert source_wrapper.out_attributes == ['out_pos', 'out_velocity']
    source = source_wrapper.get_source(defines={'TEST': 1, 'TEST2': '2'})
    assert '#define TEST 1' in source
    assert '#define TEST2 2' in source


def test_shader_source_empty(ctx):
    with pytest.raises(ValueError):
        ShaderSource(ctx, "", None, gl.GL_VERTEX_SHADER)


def test_shader_source_missing_version(ctx):
    """ShaderException: Cannot find #version in shader source"""
    with pytest.raises(ShaderException):
        ShaderSource(
            ctx,
            (
                "in vec3 in_vert\n"
                "void main() {\n"
                "   gl_Position = vec3(in_vert, 1.0);\n"
                "}\n"
            ),
            None,
            gl.GL_VERTEX_SHADER,
        )


def test_shader_source_malformed(ctx):
    """Malformed glsl source"""
    with pytest.raises(ShaderException):
        ShaderSource(
            ctx,
            (
                "in in_vert\n"
                "void main() \n"
                "   gl_Position = vec3(in_vert, 1.0)\n"
                "}\n"
            ),
            None,
            gl.GL_VERTEX_SHADER,
        )
    with pytest.raises(ShaderException):
        ShaderSource(
            ctx,
            (
                "#version\n"
                "in in_vert\n"
                "void main() \n"
                "   gl_Position = vec3(in_vert, 1.0)\n"
                "}\n"
            ),
            None,
            gl.GL_VERTEX_SHADER,
        )
    wrapper = ShaderSource(
        ctx,
        (
            "#version 330\n"
            "\n"
            "in in_vert\n"
            "#define\n"
            "#define TEST2 0\n"
            "#define TEST 0\n"
            "void main() \n"
            "   gl_Position = vec3(in_vert, 1.0)\n"
            "}\n"
        ),
        None,
        gl.GL_VERTEX_SHADER,
    )
    source = wrapper.get_source(defines={'TEST': 1})
    assert 'TEST 1' in source


def test_shader_program_broken_out(ctx):
    wrapper = ShaderSource(
        ctx,
        (
            "#version 330\n"
            "in vec3 in_vert;\n"
            "out out_vert;\n"
            "void main() \n"
            "   out_vert = in_vert;\n"
            "}\n"
        ),
        None,
        gl.GL_VERTEX_SHADER,
    )
    wrapper.out_attributes == ['out_vert']


def test_program_basic(ctx):
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
    # assert ctx.active_program == program
    assert repr(program).startswith('<Program')

    # TODO: Test all uniform types
    program['pos_offset'] = 1, 2
    assert program['pos_offset'] == (1.0, 2.0)
    with pytest.raises(KeyError):
        program['this_uniform_do_not_exist'] = 0
    with pytest.raises(KeyError):
        program['this_uniform_do_not_exist']


def test_vertex_shader(ctx):
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

def test_geo_shader(ctx):
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


def test_gl_attributes(ctx):
    """Make sure built in attributes don't interfere with generic attribute detection"""
    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 pos;
        void main() {
            gl_Position = vec4(pos + vec2(gl_VertexID) + vec2(gl_InstanceID) , 0.0, 1.0);
        }
        """,
    )


def test_compile_failed(ctx):
    with pytest.raises(ShaderException):
        program = ctx.program(
            vertex_shader="""
            #version 330
            in vec2 pos
            void main() {
                gl_Position = vec4(pos
            }
            """,
        )


def test_link_failed(ctx):
    with pytest.raises(ShaderException):
        program = ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_pos;
            in vec2 in_uv;
            out vec2 v_uv;
            void main() {
                gl_Position = vec4(in_pos, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330
            in vec3 v_uv;
            out vec4 v_color;
            void main() {
                v_color = vec4(v_uv.xy, 0.0, 1.0);
            }
            """,
        )


def test_varyings(ctx):
    """Test varyings"""
    src = """
        #version 330
        in vec2 in_pos;
        in vec2 in_velocity;
        out vec2 out_pos;
        out vec2 out_velocity;

        void main() {
            out_pos = in_pos + vec2(1.0);
            out_velocity = in_pos * 0.99;
        }
    """

    program = ctx.program(
        vertex_shader=src,
    )
    assert program.varyings == ['out_pos', 'out_velocity']

    if ctx.gl_version >= (4, 1):
        program = ctx.program(
            vertex_shader="""
            #version 410
            layout(location = 0) in vec2 in_pos;
            layout(location = 1) in vec2 in_velocity;
            layout(location = 0) out vec2 out_pos;
            layout(location = 1) out vec2 out_velocity;

            void main() {
                out_pos = in_pos + vec2(1.0);
                out_velocity = in_pos * 0.99;
            }
            """,
        )
        assert program.varyings == ['out_pos', 'out_velocity']

    # Illegal varying names
    with pytest.raises(ShaderException):
        ctx.program(vertex_shader=src, varyings=["somthing", "stuff"])

    # Mapping one of two varyings
    program = ctx.program(vertex_shader=src, varyings=["out_pos"])
    assert program.varyings == ['out_pos']
    program = ctx.program(vertex_shader=src, varyings=["out_velocity"])
    assert program.varyings == ['out_velocity']

    # Configure capture mode
    program = ctx.program(vertex_shader=src, varyings_capture_mode="interleaved")
    assert program.varyings_capture_mode == "interleaved"
    program = ctx.program(vertex_shader=src, varyings_capture_mode="separate")
    assert program.varyings_capture_mode == "separate"


def test_uniform_block(ctx):
    """Test uniform block"""
    # Simple tranform with a uniform block
    program = ctx.program(vertex_shader="""
        #version 330
        uniform Projection {
            uniform mat4 matrix;
        } proj;

        out vec2 pos;

        void main() {
            pos = (proj.matrix * vec4(800, 600, 0.0, 1.0)).xy;
        }
    """
    )
    # Obtain the ubo info and modify binding + test properties
    ubo = program['Projection']
    assert isinstance(ubo, UniformBlock)
    program['Projection'] = 1
    assert ubo.binding == 1
    ubo.binding = 0
    assert ubo.binding == 0
    assert ubo.index == 0
    assert ubo.name == "Projection"

    # Project a point (800, 600) into (1, 1) using a projection matrix
    projection_matrix = Mat4.orthogonal_projection(0, 800, 0, 600, -10, 10)
    ubo_buffer = ctx.buffer(data=projection_matrix)
    buffer = ctx.buffer(reserve=8)
    vao = ctx.geometry()
    ubo_buffer.bind_to_uniform_block(0)
    vao.transform(program, buffer, vertices=1)
    assert struct.unpack('2f', buffer.read()) == pytest.approx((1, 1), 0.01)
