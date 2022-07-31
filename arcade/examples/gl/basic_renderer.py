import math
import arcade
from arcade.gl import geometry

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Basic Renderer"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        self.time = 0
        super().__init__(width, height, title)
        self.color_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """,
            fragment_shader="""
            #version 330
            uniform vec4 color;
            out vec4 out_color;
            void main() {
                out_color = color;
            }
            """
        )
        self.uv_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330
            in vec2 v_uv;
            out vec4 out_color;
            void main() {
                out_color = vec4(v_uv, 0.0, 1.0);
            }
            """
        )
        self.quad_1 = geometry.quad_2d(pos=(-0.5, 0.5))
        self.quad_2 = geometry.quad_2d(pos=(0.5, 0.5))

    def on_draw(self):
        self.clear()
        self.color_program['color'] = (
            (math.sin(self.time) + 1.0) / 2,
            (math.sin(self.time + 2) + 1.0) / 2,
            (math.sin(self.time + 3) + 1.0) / 2,
            1.0
        )
        self.quad_1.render(self.color_program)
        self.quad_2.render(self.uv_program)

        arcade.draw_circle_filled(100, 100, 100, arcade.color.APPLE_GREEN)

    def on_update(self, dt):
        self.time += dt


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
