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

            // Unsigned integer sampler for reading uint data from texture
            uniform usampler2D screen;

            in vec2 v_uv;
            out vec4 out_color;

            void main() {
                // Calculate the bit position on the x axis
                uint bit_pos = uint(round((v_uv.x * 64) - 0.5)) % 8u;
                // Create bit mask we can AND the fragment with to extract the pixel value
                uint flag = uint(pow(2u, 7u - bit_pos));
                // Read the fragment value (We reverse the y axis here as well)
                uint frag = texture(screen, v_uv * vec2(1.0, -1.0)).r;
                // Write the pixel value. Values above 1 will be clamped to 1.
                out_color = vec4(vec3(frag & flag), 1.0);
            }
            """,
        )
        # 8 x 4
        self.program["projection"] = get_projection().flatten()
        self.program["screen"] = 0
        b = 0  # border to test scale
        self.quad = geometry.screen_rectangle(
            b, b, SCREEN_WIDTH - b * 2, SCREEN_HEIGHT - b * 2
        )
        self.texture = self.ctx.texture((8, 32), components=1, dtype="i1")
        self.texture.write(
            array(
                "B",
                [
                    # 64 x 32 screen
                    0xAA,
                    0xAA,
                    0xF0,
                    0xF0,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0xF0,
                    0xF0,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0xF0,
                    0xF0,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0xF0,
                    0xF0,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0x0F,
                    0x0F,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0x0F,
                    0x0F,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0x0F,
                    0x0F,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0x0F,
                    0x0F,
                    0xFF,
                    0x00,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0xF0,
                    0xF0,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0xF0,
                    0xF0,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0xF0,
                    0xF0,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0xF0,
                    0xF0,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0x0F,
                    0x0F,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0x0F,
                    0x0F,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0x0F,
                    0x0F,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0x55,
                    0x55,
                    0x0F,
                    0x0F,
                    0x00,
                    0xFF,
                    0xFF,
                    0xFF,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x80,
                    0x00,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x40,
                    0x00,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x20,
                    0x00,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x10,
                    0x00,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x08,
                    0x00,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x04,
                    0x00,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x02,
                    0x00,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x01,
                    0x00,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x80,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x40,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x20,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x10,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x08,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x04,
                    0xAA,
                    0xAA,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x02,
                    0x55,
                    0x55,
                    0xCC,
                    0x99,
                    0xBD,
                    0x63,
                    0x00,
                    0x01,
                ],
            )
        )

    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.quad.render(self.program)


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
