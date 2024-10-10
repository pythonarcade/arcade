"""
This version also includes a geometry shader emitting quads.

Shows simple use of transform feedback.

Transforming is similar to rendering except that the output
or the shader is a buffer instead of a framebuffer/screen.
This lets us to arbitrary calculations on floats or integers.

This examples shows a common ping-ping technique were we
transform a buffer with positions and velocities between
two buffers so we always work on the previous state.

* A list of N points are initialized with random positions and velocities
* A point of gravity is moving around on the screen affecting the points

Using transforms in this way makes us able to process
a system that is reacting to external forces in this way.
There are no predetermined paths and they system just lives on its own.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.transform_feedback_geo
"""

from array import array
import random
import arcade
import arcade.clock
from arcade.gl import BufferDescription

# Do the math to figure out our screen dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Transform Feedback"


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.ctx = self.window.ctx

        # Program to visualize the points
        self.points_program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_pos;
            void main() {
                // Just pass the position to the geometry shader
                gl_Position = vec4(in_pos, 0.0, 1.0);
            }
            """,
            geometry_shader="""
            #version 330

            uniform WindowBlock {
                mat4 projection;
                mat4 view;
            } window;

            // We are receiving points and emitting triangle strip (4 vertices making a quad)
            layout (points) in;
            layout (triangle_strip, max_vertices = 4) out;

            const float P_SIZE = 10.0;
            out vec2 uv;

            void main() {
                // The input point is the center of the quad
                vec2 center = gl_in[0].gl_Position.xy;
                // Emit 4 vertices making a triangle strip representing a quad

                mat4 mvp = window.projection * window.view;

                gl_Position = mvp * vec4(center + vec2(-P_SIZE,  P_SIZE), 0.0, 1.0);
                uv = vec2(0, 1);
                EmitVertex();

                gl_Position = mvp * vec4(center + vec2(-P_SIZE, -P_SIZE), 0.0, 1.0);
                uv = vec2(0, 0);
                EmitVertex();

                gl_Position = mvp * vec4(center + vec2( P_SIZE,  P_SIZE), 0.0, 1.0);
                uv = vec2(1, 1);
                EmitVertex();

                gl_Position = mvp * vec4(center + vec2( P_SIZE, -P_SIZE), 0.0, 1.0);
                uv = vec2(1, 0);
                EmitVertex();
                EndPrimitive();
            }
            """,
            fragment_shader="""
            #version 330

            // Texture coordinates generated in geometry shader
            in vec2 uv;
            // The pixel we are writing to in the framebuffer
            out vec4 fragColor;

            void main() {
                float l = length(uv * 2.0 - vec2(1.0));
                if (l > 1.0) discard;
                fragColor = vec4(0.1);
            }
            """,
        )

        # A program transforming points being affected by a gravity point
        self.gravity_program = self.ctx.program(
            vertex_shader="""
            #version 330

            // Delta time (since last frame)
            uniform float dt;
            // Strength of gravity
            uniform float force;
            // Position of gravity
            uniform vec2 gravity_pos;

            // The format of the data in our transform buffer(s)
            in vec2 in_pos;
            in vec2 in_vel;

            // We are writing to a buffer of the same format
            out vec2 out_pos;
            out vec2 out_vel;

            void main() {
                // Simplified gravity calculations
                vec2 dir = normalize(gravity_pos - in_pos) * force;
                vec2 vel = in_vel + dir / length(dir) * 1.0;

                // Write to the output buffer
                out_vel = vel;
                out_pos = in_pos + vel * dt;
            }
            """,
        )
        N = 10_000
        # Make two buffers we transform between so we can work on the previous result
        self.buffer_1 = self.ctx.buffer(data=array("f", self.gen_initial_data(N)))
        self.buffer_2 = self.ctx.buffer(reserve=self.buffer_1.size)

        # We also need to be able to visualize both versions (draw to the screen)
        self.vao_1 = self.ctx.geometry([BufferDescription(self.buffer_1, "2f 2x4", ["in_pos"])])
        self.vao_2 = self.ctx.geometry([BufferDescription(self.buffer_2, "2f 2x4", ["in_pos"])])

        # We need to be able to transform both buffers (ping-pong)
        self.gravity_1 = self.ctx.geometry(
            [BufferDescription(self.buffer_1, "2f 2f", ["in_pos", "in_vel"])]
        )
        self.gravity_2 = self.ctx.geometry(
            [BufferDescription(self.buffer_2, "2f 2f", ["in_pos", "in_vel"])]
        )

        self.mouse_pos = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

    def gen_initial_data(self, count):
        for _ in range(count):
            yield random.uniform(0, WINDOW_WIDTH)  # pos x
            yield random.uniform(0, WINDOW_HEIGHT)  # pos y
            yield random.uniform(-10, 10)  # velocity x
            yield random.uniform(-10, 10)  # velocity y

    def on_draw(self):
        self.clear()

        # Set up blending states
        self.ctx.enable_only(self.ctx.BLEND)
        self.ctx.blend_func = self.ctx.BLEND_ADDITIVE

        # Set uniforms in the program
        self.gravity_program["dt"] = arcade.clock.GLOBAL_CLOCK.delta_time
        self.gravity_program["force"] = 10.0
        self.gravity_program["gravity_pos"] = self.mouse_pos

        # Transform data in buffer_1 into buffer_2
        self.gravity_1.transform(self.gravity_program, self.buffer_2)
        # Render the result (Draw buffer_2)
        self.vao_2.render(self.points_program, mode=self.ctx.POINTS)

        # Swap around stuff around so we transform back and fourth between the two buffers
        self.gravity_1, self.gravity_2 = self.gravity_2, self.gravity_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1
        self.buffer_1, self.buffer_2 = self.buffer_2, self.buffer_1

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = x, y


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
