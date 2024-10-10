"""
Example showing how er can emit particles with the gpu.
We work with transform shaders to do all the logic.

This example was created on a Raspberry PI 4.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.transform_emit
"""

# import struct
import random
from array import array
import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Transform Emit - GPU"

class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.ctx = self.window.ctx

        # Program to simply draw the points
        self.visualize_points_program = self.ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_pos;
                in vec3 in_col;

                out vec3 color;

                void main() {
                    gl_Position = vec4(in_pos, 0.0, 1.0);
                    color = in_col;
                }
                """,
            fragment_shader="""
                #version 330

                out vec4 fragColor;
                in vec3 color;

                void main() {
                    fragColor = vec4(color, 1.0);
                }
            """,
        )

        # Program to emit points into a buffer
        self.emit_program = self.ctx.program(
            vertex_shader="""
                #version 330
                #define M_PI 3.1415926535897932384626433832795
                uniform float time;

                out vec2 out_pos;
                out vec2 out_vel;

                float rand(float n) { return fract(sin(n) * 43758.5453123); }

                void main() {
                    float a = mod(time * float(gl_VertexID) + rand(time), M_PI * 2.0);
                    float r = clamp(rand(time + float(gl_VertexID)), 0.1, 0.9);

                    out_pos = vec2(0.0);
                    out_vel = vec2(sin(a), cos(a)) * r;
                }
            """,
            varyings=["out_pos", "out_vel"],
            varyings_capture_mode="separate",
        )

        self.move_program = self.ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_pos;
                in vec2 in_vel;

                out vec2 v_pos;
                out vec2 v_vel;

                void main() {
                    v_pos = in_pos;
                    v_vel = in_vel;
                }
            """,
            geometry_shader="""
                #version 330

                layout(points) in;
                layout(points, max_vertices = 1) out;

                uniform float dt;

                in vec2 v_pos[];
                in vec2 v_vel[];

                out vec2 out_pos;
                out vec2 out_vel;

                void main() {
                    vec2 pos = v_pos[0];
                    vec2 vel = v_vel[0];

                    if (pos.y > -1.0) {
                        out_pos = pos + vel * dt;
                        out_vel = vel - vec2(0.0, dt);
                        EmitVertex();
                    }

                }
            """,
            varyings=["out_pos", "out_vel"],
            varyings_capture_mode="separate",
        )

        # Configuration
        self.num_points = 10_000
        self.active_points = 0
        self.emit_max_points = 100

        # First set of positions and velocities
        self.buffer_pos_1 = self.ctx.buffer(reserve=self.num_points * 8)
        self.buffer_vel_1 = self.ctx.buffer(reserve=self.num_points * 8)

        # Second set of positions and velocities
        self.buffer_pos_2 = self.ctx.buffer(reserve=self.num_points * 8)
        self.buffer_vel_2 = self.ctx.buffer(reserve=self.num_points * 8)

        self.buffer_colors = self.ctx.buffer(
            data=array("f", [random.random() for _ in range(self.num_points * 3)])
        )

        # Geometry definition for drawing the two sets of positions
        self.draw_geometry_1 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_1, "2f", ("in_pos",)),
                BufferDescription(self.buffer_colors, "3f", ("in_col",)),
            ],
            mode=self.ctx.POINTS,
        )
        self.draw_geometry_2 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_2, "2f", ("in_pos",)),
                BufferDescription(self.buffer_colors, "3f", ("in_col",)),
            ],
            mode=self.ctx.POINTS,
        )

        # Geometry we use to move he points
        self.move_geometry_1 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_1, "2f", ("in_pos",)),
                BufferDescription(self.buffer_vel_1, "2f", ("in_vel",)),
            ],
            mode=self.ctx.POINTS,
        )
        self.move_geometry_2 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_2, "2f", ("in_pos",)),
                BufferDescription(self.buffer_vel_2, "2f", ("in_vel",)),
            ],
            mode=self.ctx.POINTS,
        )

        self.emit_geometry = self.ctx.geometry()
        self.query = self.ctx.query(primitives=True)

    def on_draw(self):
        self.clear()
        self.ctx.enable_only()

        self.draw_geometry_2.render(self.visualize_points_program)

        # Swap things around for the next frame
        self.draw_geometry_1, self.draw_geometry_2 = self.draw_geometry_2, self.draw_geometry_1
        self.buffer_pos_1, self.buffer_pos_2 = self.buffer_pos_2, self.buffer_pos_1
        self.buffer_vel_1, self.buffer_vel_2 = self.buffer_vel_2, self.buffer_vel_1

    def on_update(self, delta_time):
        # print("active points", self.active_points)

        # Do we have points to emit?
        if self.active_points < self.num_points:

            emit_count = min(self.num_points - self.active_points, self.emit_max_points)
            # print("Emitting", emit_count)

            # Emit some particles
            self.emit_program["time"] = self.window.time
            self.emit_geometry.transform(
                self.emit_program,
                [self.buffer_pos_1, self.buffer_vel_1],
                vertices=emit_count,
                buffer_offset=self.active_points * 8,
            )
            self.active_points += emit_count

        # Move the points. This will also purge dead particles
        self.move_program["dt"] = delta_time
        with self.query:
            self.move_geometry_1.transform(
                self.move_program,
                [self.buffer_pos_2, self.buffer_vel_2],
                vertices=self.active_points,
            )
        self.active_points = self.query.primitives_generated
        # print("after moving", self.active_points)


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
