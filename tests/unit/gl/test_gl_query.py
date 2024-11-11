import sys
import arcade
from arcade.gl import geometry


def test_create(window: arcade.Window):
    ctx = window.ctx
    SCREEN_WIDTH, SCREEN_HEIGHT = window.get_size()

    program = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_vert;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """,
        fragment_shader="""
        #version 330
        out vec4 outColor;
        void main() {
            outColor = vec4(1.0);
        }
        """,
    )
    quad = geometry.quad_2d_fs()
    query = ctx.query()

    # NOTE: On mac the query doesn't work mixed with other test.
    #       Only when running standalone
    if sys.platform != "darwin":
        with query:
            quad.render(program)

        # gles query doesn't support time and written samples
        if ctx.gl_api == "gl":
            assert query.time_elapsed > 0
            assert query.samples_passed >= SCREEN_WIDTH * SCREEN_HEIGHT

        assert query.primitives_generated == 2
