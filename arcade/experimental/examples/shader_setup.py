from PIL import Image

import arcade
from arcade.gl import geometry
from arcade.resources import resolve_resource_path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shader Setup"


class ShaderSetup(arcade.Window):
    """Shader setup"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.time = 0
        self.program = self.ctx.program(
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

            uniform sampler2D background;
            uniform float time;

            in vec2 v_uv;
            out vec4 out_color;

            void main() {
                vec2 pos = v_uv * 1.0 - vec2(0.5);
                vec2 uv = v_uv + normalize(pos) + sin(length(pos) * 10 - time);
                out_color = texture(background, uv);
            }
            """
        )
        self.quad = geometry.screen_rectangle(-1, -1, 2, 2)
        image = Image.open(resolve_resource_path(":resources:images/backgrounds/abstract_1.jpg")).convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self.texture = self.ctx.texture(image.size, components=4, data=image.tobytes())

    def on_draw(self):
        self.clear()
        self.program["time"] = self.time
        self.texture.use(0)
        self.quad.render(self.program)

    def on_update(self, dt):
        self.time += dt


if __name__ == "__main__":
    ShaderSetup(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
