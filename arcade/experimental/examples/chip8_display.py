"""
CHIP-8 is an interpreted minimalist programming language that was designed by
Joseph Weisbecker in the 1970s for use on the RCA COSMAC VIP computer.

This example renders a 64 x 32 pixel display. The pixel format is using
bits to represent what pixel is enabled/disabled so the byte size of
the buffer is 8 x 4 = 32 bytes.

References: 
http://mattmik.com/files/chip8/mastering/chip8.html
https://github.com/JohnEarnest/Octo
"""
import math
from array import array

import arcade
from arcade.gl import geometry
from arcade import get_projection

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 64 * 10
SCREEN_HEIGHT = 32 * 10
SCREEN_TITLE = "CHIP-8 Screen"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """CHIP-8 Screen"""
        super().__init__(width, height, title)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            uniform mat4 projection;
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;
            void main() {
                gl_Position = projection * vec4(in_vert, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330
            uniform usampler2D screen;
            in vec2 v_uv;
            out vec4 out_color;
            void main() {
                out_color = vec4(vec3(texture(screen, v_uv * vec2(1.0, -1.0)).r), 1.0);
            }
            """
        )
        # 8 x 4 
        self.program['projection'] = get_projection().flatten()
        self.program['screen'] = 0
        self.quad = geometry.screen_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.texture = self.ctx.texture((8, 4), components=1, dtype='i1')
        self.texture.write(array(
            'B',
            [
                # 62 x 32 screen
                0xF0, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0xF0,
                0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0,
            ]
        ).tobytes())

    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.quad.render(self.program)


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
