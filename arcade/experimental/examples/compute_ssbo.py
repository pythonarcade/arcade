"""
Compute shader with buffers.

The example is using compute shaders with shader storage buffers (SSBOs).
These are simply large buffers we can read and write to. We also show
how we can visualize the result using a normal shader.

We generate N number of points with random velocities, colors and a radius in python
and write that to an ssbo/buffer. Every frame we run a compute shader
that calculates new positions for every point based on the velocities,
collision with screen borders and a directional force we change over time.
The result ends up in a new buffer because it's not always practical to
read and write to the same buffer at the same time (but it is possible).
We swap the source and target buffer every frame so we keep working on
the previous state (ping-pong).

These points are then rendered as circles/balls using a traditional shader.
We use a geometry shader to on-the-fly create a rectangle for each point.
The size of each ball is based on the radius stored for each point.

The compute shader in this example works in one dimension for simplicity.
"""
import random
import math
from array import array

import arcade
from arcade.gl import BufferDescription

COMPUTE_SHADER = """
#version 430

// Describe the minimum amount of work this compute shader can execute.
// This is called a work group. Our work group will run 256 threads/invocations.
// When we run a compute shader we specify how many of these groups we are executing.
// This work group only has one dimension, but there is also local_size_y and local_size_z.
layout(local_size_x=256) in;

// Global variables for this shader.
// These are assigned to the shader at runtime.
uniform vec2 screen_size;
uniform vec2 force;
uniform float frame_time;

// Use a structure to make it easier to describe the input data.
// Note that these vectors are larger than they need to be
// to provide the compute shader with neatly aligned data.
struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 col;
};

// Input buffer of points/balls
layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;
// Output buffer of points/balls
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    // Get the ball number we are working with.
    // This goes from 0 to N (number of balls)
    int x = int(gl_GlobalInvocationID.x);

    // Get the current ball from the input buffer
    Ball in_ball = In.balls[x];
    // Get position for easier access
    vec4 p = in_ball.pos.xyzw;
    // Get the velocity for easy access
    vec4 v = in_ball.vel.xyzw;

    // Apply velocity
    p.xy += v.xy;

    // Apply external force vector
    v.xy += force * frame_time;

    // Get at weak the radius
    float rad = p.w * 0.5;

    // Check If we are outside the screen.
    // Tweak position and velocity it this is the case.
    // The ball will lose a bit of velocity on collisions.
    if (p.x - rad <= 0.0)
    {
        p.x = rad;
        v.x *= -0.98;
    }
    else if (p.x + rad >= screen_size.x)
    {
        p.x = screen_size.x - rad;
        v.x *= -0.98;
    }

    if (p.y - rad <= 0.0)
    {
        p.y = rad;
        v.y *= -0.98;
    }
    else if (p.y + rad >= screen_size.y)
    {
        p.y = screen_size.y - rad;
        v.y *= -0.98;
    }

    // Create new ball and write to out buffer
    Ball out_ball;
    out_ball.pos = p;
    out_ball.vel = v;
    out_ball.col = in_ball.col;

    Out.balls[x] = out_ball;
}
"""


class App(arcade.Window):

    def __init__(self, *args, **kwargs):
        # We need to specify OpenGL 4.3 when using Compute Shaders
        super().__init__(720, 720, "Compute Shader", gl_version=(4, 3), resizable=True, vsync=True)
        # Keep track of time
        self.time = 0
        self.frame_time = 0
        # The work group size we have configured the compute shader to.
        # This is hardcoded the compute shader (careful with changing)
        self.work_group_size = 256
        # How many work groups to execute when running the compute shader
        self.work_groups_to_execute = 20
        # How many balls/points to work with
        self.num_balls = self.work_group_size * self.work_groups_to_execute

        # Create the compute shader. We only need the source.
        self.cs = self.ctx.compute_shader(source=COMPUTE_SHADER)

        # Buffers with data for the compute shader (We ping-pong render between these).
        # The generated data is 12 x 32bit floats containing positions, velocities and
        # colors. Some of these floats are just dummy/padding floats to make the data
        # neatly aligned for the compute shader. There are strict rules for this
        # for a compute shader to be able to parallelize the work over potentially
        # thousands of threads.
        self.ssbo_1 = self.ctx.buffer(data=array('f', self.gen_initial_data(self.num_balls)))
        # Create a second buffer with the exact same byte size
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

        # Create a geometry instance describing the buffer contents so the
        # shader visualizing them knows how to map the buffer data to vertex shader inputs.
        # We need one for each buffer because the data is moving between the
        # two buffers every frame.
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, "4f 4x4 4f", ["in_vert", "in_col"])],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, "4f 4x4 4f", ["in_vert", "in_col"])],
            mode=self.ctx.POINTS,
        )

        # Program for visualizing the balls.
        # This is simply
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            // Input from buffers as described in the geometry
            in vec4 in_vert;
            in vec4 in_col;

            // Output values to the geometry shader
            out vec2 v_pos;
            out float v_radius;
            out vec4 v_col;

            void main()
            {
                // We just forward every every every ball to geometry shader
                v_pos = in_vert.xy;
                v_radius = in_vert.w;
                v_col = in_col;
            }
            """,
            geometry_shader="""
            #version 330

            // Configure the geometry shader to only take one vertex
            // per invocation from the vertex shader.
            layout (points) in;
            // Configure the geomtry shader to emit triangle strips
            // and limit the max number of vertices to 4.
            layout (triangle_strip, max_vertices = 4) out;

            // Use arcade's global projection UBO
            uniform Projection {
                uniform mat4 matrix;
            } proj;

            // The input from the vertex shader.
            // These should be unsized arrays since the geometry shader
            // can be configured to take more than one vertex from the
            // vertex shader per invocation. For example lines or triangles.
            // The compiler will ensure the arrays have the right size.
            in vec2 v_pos[];
            in vec4 v_col[];
            in float v_radius[];

            // Output color texture coordinates and color to the
            // fragment shader. These are emitted together with
            // the gl_Position every time EmitVertex() is called.
            out vec2 g_uv;
            out vec3 g_col;

            void main() {
                // We use the ball position as the center point of the rectangle we are emitting
                vec2 center = v_pos[0];
                // Calculate the half size to easily emit 4 vertices around the center.
                vec2 hsize = vec2(v_radius[0]);

                // Configure outout color. This color can change per vertex
                // but we're using the same color for all vertices of the ball
                // so we only need to set it once.
                g_col = v_col[0].rgb;

                // Emit 4 vertices making a rectangle as a triangle strip.
                // We need to supply separate texture coordinates for each vertex
                gl_Position = proj.matrix * vec4(vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
                g_uv = vec2(0, 1);
                EmitVertex();
                gl_Position = proj.matrix * vec4(vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
                g_uv = vec2(0, 0);
                EmitVertex();
                gl_Position = proj.matrix * vec4(vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
                g_uv = vec2(1, 1);
                EmitVertex();
                gl_Position = proj.matrix * vec4(vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
                g_uv = vec2(1, 0);
                EmitVertex();

                // End the triangle strip here
                EndPrimitive();
            }

            """,
            fragment_shader="""
            #version 330

            // Inputs from the geometry shader.
            // The fragmet shader runs for every pixel it needs to fill in a triangle.
            // These inputs will be an interpolated value based on the distance
            // from each vertex. See. barycentric coordinate.
            in vec2 g_uv;
            in vec3 g_col;

            // The pixel value that will end up on the screen
            out vec4 out_color;

            void main()
            {
                // We use the texture coordinates to calculate the distance
                // from the center of the rectangle to discard pixels
                // outside a certain radius so we end up with filled circle.
                if (length(vec2(0.5, 0.5) - g_uv.xy) > 0.25)
                {
                    // Stop this shader invocation.
                    // No fragment will be written to the screen.
                    discard;
                }
                // Set final pixel value. This is simply
                // the color from the geometry shader.
                out_color = vec4(g_col, 1.0);
            }
            """,
        )

    def on_draw(self):
        self.clear()
        self.ctx.disable(self.ctx.BLEND)

        # Calculate a directional force based on time.
        # This will affect the locations of the balls,
        force = math.sin(self.time / 10) / 2, math.cos(self.time / 10) / 2

        # Bind buffers to the binding indices configured in the compute shader
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)

        # Set uniforms / global values in shader
        self.cs["screen_size"] = self.get_size()
        self.cs["force"] = force
        self.cs["frame_time"] = self.frame_time

        # Run the compute shader.
        # This will look at each ball in the first buffer
        # and write new balls in the second buffer applying
        # new positions, velocities and apply force.
        self.cs.run(group_x=self.work_groups_to_execute)

        # Draw the points and balls emitting circles to the screen.
        # We are drawing the balls in the second buffer.
        self.vao_2.render(self.program)

        # Swap the buffers around (we are ping-ping rendering between two buffers)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # Swap what geometry we draw
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

    def on_update(self, delta_time: float):
        # Keep our time variables up to date
        self.time += delta_time
        self.frame_time = delta_time

    def gen_initial_data(self, num_balls):
        """
        Generate positions, velocities and color data
        for num_balls. This is a generator function
        that yields a stream of values.

        Each ball has:
        * position and radius (3 floats + 1 padding float)
        * velocity (2 floats + 2 padding floats)
        * color: (3 floats + 1 padding float)
        """
        for i in range(num_balls):
            angle = (i / self.num_balls) * math.pi * 2.0
            radius = random.random() * 10 + 3
            # pos
            yield random.randrange(0, self.width)
            yield random.randrange(0, self.height)
            yield 0.0  # z (padding)
            yield radius  # w / radius
            # Velocity
            v = random.random() * 1.0 + 0.1
            yield math.cos(angle) * v  # vx
            yield math.sin(angle) * v  # vy
            yield 0.0  # vz (padding)
            yield 0.0  # vw (padding)
            # Color
            yield 1.0 * random.random()  # r
            yield 1.0 * random.random()  # g
            yield 1.0 * random.random()  # b
            yield 1.0  # a


app = App()
arcade.run()
