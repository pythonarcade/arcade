import pytest
import arcade
from pyglet import gl
from arcade.gl import ShaderException
from arcade.gl.glsl import ShaderSource

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.close()


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


def test_shader_source_empty(ctx):
    with pytest.raises(ValueError):
        ShaderSource("", gl.GL_VERTEX_SHADER)


def test_shader_source_missing_version(ctx):
    """ShaderException: Cannot find #version in shader source"""
    with pytest.raises(ShaderException):
        ShaderSource(
            (
                "in vec3 in_vert\n"
                "void main() {\n"
                "   gl_Position = vec3(in_vert, 1.0);\n"
                "}\n"
            ),
            gl.GL_VERTEX_SHADER,
        )


def test_shader_source_malformed(ctx):
    """Malformed glsl source"""
    with pytest.raises(ShaderException):
        ShaderSource(
            (
                "in in_vert\n"
                "void main() \n"
                "   gl_Position = vec3(in_vert, 1.0)\n"
                "}\n"
            ),
            gl.GL_VERTEX_SHADER,
        )
    with pytest.raises(ShaderException):
        ShaderSource(
            (
                "#version\n"
                "in in_vert\n"
                "void main() \n"
                "   gl_Position = vec3(in_vert, 1.0)\n"
                "}\n"
            ),
            gl.GL_VERTEX_SHADER,
        )
    wrapper = ShaderSource(
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
        gl.GL_VERTEX_SHADER,
    )
    source = wrapper.get_source(defines={'TEST': 1})
    assert 'TEST 1' in source


def test_shader_program_broken_out(ctx):
    wrapper = ShaderSource(
        (
            "#version 330\n"
            "in vec3 in_vert;\n"
            "out out_vert;\n"
            "void main() \n"
            "   out_vert = in_vert;\n"
            "}\n"
        ),
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
    assert ctx.active_program == program
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


def test_uniforms(ctx):
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
