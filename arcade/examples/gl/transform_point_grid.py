"""
Transform feedback example moving points using the mouse.
Each point as a desired position and a current position.
A radius around the mouse pointer will push the points
current position. Each point will constantly strive to
be at its desired position.

We're using a common trick ping-pong transforming
the point data between two buffers on the gpu
so we can keep working on the previous data.
This is mainly because it's not always safe to
read and write to the same buffer at the same time.

Increase the window resolution to get more points.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.transform_point_grid
"""

import random
from array import array

from pyglet.math import Mat4
import arcade
from arcade import gl
import arcade.clock


def gen_initial_data(window, width, height):
    """Generate a grid of points (current and desired position)"""
    dx, dy = window.width / width, window.height / height
    for y in range(height):
        for x in range(width):
            # current pos
            yield x * dx + dx / 2
            yield y * dy + dy / 2
            # desired pos
            yield x * dx + dx / 2
            yield y * dy + dy / 2


def gen_colors(width, height):
    """Generate some random colors"""
    for _ in range(width * height):
        yield random.uniform(0, 1)
        yield random.uniform(0, 1)
        yield random.uniform(0, 1)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.window.set_vsync(True)
        self.ctx = self.window.ctx

        self.ctx.disable(self.ctx.BLEND)

        # Two buffers on the gpu with positions
        self.buffer1 = self.ctx.buffer(data=array("f", gen_initial_data(self, *self.size)))
        self.buffer2 = self.ctx.buffer(reserve=self.buffer1.size)
        # Buffer with color for each point
        self.colors = self.ctx.buffer(data=array("f", gen_colors(*self.size)))

        # Geometry for drawing the two buffer variants.
        # We pad away the desired position and add the color data.
        self.geometry1 = self.ctx.geometry(
            [
                gl.BufferDescription(self.buffer1, "2f 2x4", ["in_pos"]),
                gl.BufferDescription(self.colors, "3f", ["in_color"]),
            ]
        )
        self.geometry2 = self.ctx.geometry(
            [
                gl.BufferDescription(self.buffer2, "2f 2x4", ["in_pos"]),
                gl.BufferDescription(self.colors, "3f", ["in_color"]),
            ]
        )

        # Transform geometry for the two buffers. This is used to move the points
        # with a transform shader
        self.transform1 = self.ctx.geometry(
            [gl.BufferDescription(self.buffer1, "2f 2f", ["in_pos", "in_dest"])]
        )
        self.transform2 = self.ctx.geometry(
            [gl.BufferDescription(self.buffer2, "2f 2f", ["in_pos", "in_dest"])]
        )

        # Let's make the coordinate system match the viewport
        projection = Mat4.orthogonal_projection(0, self.width, 0, self.height, -100, 100)

        # Draw the points with the the supplied color
        self.points_program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 projection;
            in vec2 in_pos;
            in vec3 in_color;
            out vec3 color;

            void main() {
                gl_Position = projection * vec4(in_pos, 0.0, 1.0);
                color = in_color;
            }
            """,
            fragment_shader="""
            #version 330

            in vec3 color;
            out vec4 fragColor;

            void main() {
                fragColor = vec4(color, 1.0);
            }
            """,
        )
        # Write the projection matrix to the program uniform
        self.points_program["projection"] = projection

        # Program altering the point location.
        # We constantly try to move the point to its desired location.
        # In addition we check the distance to the mouse pointer and move it if
        # within a certain range.
        self.transform_program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform float dt; // time delta (between frames)
            uniform vec2 mouse_pos;

            in vec2 in_pos;
            in vec2 in_dest;

            out vec2 out_pos;
            out vec2 out_dest;

            void main() {
                out_dest = in_dest;
                // Slowly move the point towards the desired location
                vec2 dir = in_dest - in_pos;
                vec2 pos = in_pos + dir * dt;
                // Move the point away from the mouse position
                float dist = length(pos - mouse_pos);
                if (dist < 90.0) {
                    pos += (pos - mouse_pos) * dt * 10.0;
                }
                out_pos = pos;
            }
            """,
        )
        self.mouse_pos = -100, -100

    def on_draw(self):
        self.clear()
        # Set a point size. Multiply with pixel ratio taking retina resolutions
        # and UI scaling into account
        self.ctx.point_size = 2 * self.window.get_pixel_ratio()

        # Draw the points we calculated last frame
        self.geometry1.render(self.points_program, mode=gl.POINTS)

        # Move points with transform
        self.transform_program["dt"] = arcade.clock.GLOBAL_CLOCK.delta_time
        self.transform_program["mouse_pos"] = self.mouse_pos
        self.transform1.transform(self.transform_program, self.buffer2)

        # Swap variables around (ping-pong rendering)
        self.buffer1, self.buffer2 = self.buffer2, self.buffer1
        self.geometry1, self.geometry2 = self.geometry2, self.geometry1
        self.transform1, self.transform2 = self.transform2, self.transform1

    def on_mouse_motion(self, x, y, dx, dy):
        """Update the current mouse position"""
        self.mouse_pos = x, y


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(768, 768, "Moving Point Grid - GPU")

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
