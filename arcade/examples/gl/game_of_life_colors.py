"""
Game of Life - Shader Version

This version uses shaders which draws to textures to
run Conway's Game of Life with an added twist: colors.

Press SPACE to reset the simulation with random data.

It uses two textures: One to keep the old state and
a second to draw the new state into. These textures are
flipped around after every update.

You can configure the cell and window size by changing
the constants at the top of the file after the imports.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.game_of_life_colors
"""

import random
from array import array

import arcade
from arcade import key
from arcade.gl import geometry


CELL_SIZE = 2  # Cell size in pixels
WINDOW_WIDTH = 512  # Width of the window
WINDOW_HEIGHT = 512  # Height of the window
FRAME_DELAY = 2  # The game will only update every 2nd frame


class GameOfLife(arcade.Window):

    def __init__(self, width, height):
        super().__init__(width, height, "Game of Life - Shader Version")
        self.frame = 0

        # Calculate how many cells we need to simulate at this pixel size
        self.texture_size = width // CELL_SIZE, height // CELL_SIZE

        # Create two textures for the next and previous state (RGB textures)
        self.texture_1 = self.ctx.texture(
            self.texture_size,
            components=3,
            filter=(self.ctx.NEAREST, self.ctx.NEAREST),
        )
        self.texture_2 = self.ctx.texture(
            self.texture_size,
            components=3,
            filter=(self.ctx.NEAREST, self.ctx.NEAREST),
        )
        self.write_initial_state()

        # Add the textures to framebuffers so we can render to them
        self.fbo_1 = self.ctx.framebuffer(color_attachments=[self.texture_1])
        self.fbo_2 = self.ctx.framebuffer(color_attachments=[self.texture_2])

        # Fullscreen quad (using triangle strip)
        self.quad_fs = geometry.quad_2d_fs()

        # Shader to draw the texture
        self.display_program = self.ctx.program(
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
            out vec4 fragColor;
            in vec2 uv;

            void main() {
                fragColor = texture(texture0, uv);
            }
            """,
        )

        # Shader which calculates the next game state.
        # It uses the previous state as input (texture0) and
        # renders the next state into the second texture.
        self.life_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D texture0;
            out vec4 fragColor;

            // Check if something is living in the cell
            bool cell(vec4 fragment) {
                return length(fragment.xyz) > 0.1;
            }

            void main() {
                // Get the pixel position we are currently writing
                ivec2 pos = ivec2(gl_FragCoord.xy);

                // Grab neighbor fragments + current one
                vec4 v1 = texelFetch(texture0, pos + ivec2(-1, -1), 0);
                vec4 v2 = texelFetch(texture0, pos + ivec2( 0, -1), 0);
                vec4 v3 = texelFetch(texture0, pos + ivec2( 1, -1), 0);

                vec4 v4 = texelFetch(texture0, pos + ivec2(-1, 0), 0);
                vec4 v5 = texelFetch(texture0, pos, 0);
                vec4 v6 = texelFetch(texture0, pos + ivec2(1,  0), 0);

                vec4 v7 = texelFetch(texture0, pos + ivec2(-1, 1), 0);
                vec4 v8 = texelFetch(texture0, pos + ivec2( 0, 1), 0);
                vec4 v9 = texelFetch(texture0, pos + ivec2( 1, 1), 0);

                // Cell in current position is alive?
                bool living = cell(v5);

                // Count how many neighbors is alive
                int neighbors = 0;
                if (cell(v1)) neighbors++;
                if (cell(v2)) neighbors++;
                if (cell(v3)) neighbors++;
                if (cell(v4)) neighbors++;
                if (cell(v6)) neighbors++;
                if (cell(v7)) neighbors++;
                if (cell(v8)) neighbors++;
                if (cell(v9)) neighbors++;

                // Average color for all neighbors
                vec4 sum = (v1 + v2 + v3 + v4 + v6 + v7 + v8 + v9) / float(neighbors);

                if (living) {
                    if (neighbors == 2 || neighbors == 3) {
                        // The cell lives, but we write out the average color minus a small value
                        fragColor = vec4(sum.rgb - vec3(1.0/255.0), 1.0);
                    } else {
                        // The cell dies when too few or too many neighbors
                        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
                    }
                } else {
                    if (neighbors == 3) {
                        // A new cell was born
                        fragColor = vec4(normalize(sum.rgb), 1.0);
                    } else {
                        // Still dead
                        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
                    }
                }
            }
            """,
        )

    def gen_initial_data(self, num_values: int):
        """Generate initial data.

        We need to be careful about the initial game state. Carelessly
        random numbers will make the simulation die in only a few frames.
        Instead, we need to generate values which leave room for life
        to exist.

        The implementtation below is one of the slowest possible ways to
        would generate the initial data, but it keeps things simple for
        this example.
        """
        choices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 64, 128, 192, 255]
        for i in range(num_values):
            yield random.choice(choices)

    def write_initial_state(self):
        """Write initial data to the source texture."""
        size = self.texture_size
        self.texture_1.write(array("B", self.gen_initial_data(size[0] * size[1] * 3)))

    def on_draw(self):
        self.clear()

        # Should we do an update this frame?
        if self.frame % FRAME_DELAY == 0:
            # Calculate the next state
            self.fbo_2.use()  # Render to texture 2
            self.texture_1.use()  # Take texture 1 as input
            self.quad_fs.render(self.life_program)  # Run the life program

            # Draw result to screen
            self.ctx.screen.use()  # Switch back to rendering to screen
            self.texture_2.use()  # Take texture 2 as input
            self.quad_fs.render(self.display_program)  # Display the texture

            # Swap things around for the next frame
            self.texture_1, self.texture_2 = self.texture_2, self.texture_1
            self.fbo_1, self.fbo_2 = self.fbo_2, self.fbo_1
        # Otherwise just draw the current texture
        else:
            # Draw the current texture to the screen
            self.ctx.screen.use()  # Switch back to rendering to screen
            self.texture_1.use()  # Take texture 2 as input
            self.quad_fs.render(self.display_program)  # Display the texture

    def on_update(self, delta_time: float):
        # Track the number of frames
        self.frame += 1

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.SPACE:
            self.write_initial_state()


if __name__ == "__main__":
    game = GameOfLife(WINDOW_WIDTH, WINDOW_HEIGHT)
    game.run()
