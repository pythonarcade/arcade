import pytest
import arcade
from arcade.gl import geometry

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.close()


def test_create(ctx):
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
    with query:
        quad.render(program)

    assert query.time_elapsed > 0
    assert query.samples_passed >= SCREEN_WIDTH * SCREEN_HEIGHT
    assert query.primitives_generated == 2
    query = None
