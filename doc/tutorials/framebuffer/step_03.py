import arcade
from arcade.experimental.texture_render_target import RenderTargetTexture

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template Simple"


class RandomFilter(RenderTargetTexture):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D texture0;

            in vec2 uv;
            uniform vec4 my_color;
            out vec4 fragColor;

            void main() {
                vec4 color = texture(texture0, uv);

                if (color.a > 0)
                    fragColor = my_color;
                else
                    fragColor = vec4(0, 0, 0, 0);
            }
            """,
        )
        self.program["my_color"] = 1, 0, 1, 1

    def use(self):
        self._fbo.use()

    def draw(self):
        self.texture.use(0)
        self._quad_fs.render(self.program)


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.filter = RandomFilter(width, height)

    def on_draw(self):
        self.clear()
        self.filter.clear()
        self.filter.use()
        arcade.draw_circle_filled(self.width / 2, self.height / 2, 100, arcade.color.RED)

        self.use()
        self.filter.draw()


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
