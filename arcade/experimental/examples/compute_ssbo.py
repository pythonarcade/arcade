"""
Compute shader with buffers
"""
import random
import math
from array import array

import arcade
from arcade.gl import BufferDescription

COMPUTE_SHADER = """
#version 430

layout(local_size_x=%COMPUTE_SIZE_X%, local_size_y=%COMPUTE_SIZE_Y%) in;

uniform vec2 screen_size;
uniform vec2 force;
uniform float frame_time;

struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 col;
};

layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    int x = int(gl_GlobalInvocationID);

    Ball in_ball = In.balls[x];

    vec4 p = in_ball.pos.xyzw;
    vec4 v = in_ball.vel.xyzw;

    p.xy += v.xy;

    float rad = p.w * 0.5;
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
    v.xy += force * frame_time;

    Ball out_ball;
    out_ball.pos.xyzw = p.xyzw;
    out_ball.vel.xyzw = v.xyzw;

    vec4 c = in_ball.col.xyzw;
    out_ball.col.xyzw = c.xyzw;

    Out.balls[x] = out_ball;
}
"""


class App(arcade.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(720, 720, "Compute Shader", gl_version=(4, 3), resizable=True, vsync=True)
        self.time = 0
        self.frame_time = 0
        self.num_balls = min(256 * 32, 16384)
        self.group_x = 256
        self.group_y = self.group_x // 256
        self.cs = self.ctx.compute_shader(
            source=COMPUTE_SHADER.replace(
                "%COMPUTE_SIZE_X%", str(self.group_x)).replace(
                    "%COMPUTE_SIZE_Y%", str(self.group_y))
        )

        # Buffers with data for the compute shader (We ping-pong render between these)
        self.ssbo_1 = self.ctx.buffer(data=array('f', self.gen_initial_data()))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

        # Geometry for both buffers
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, "4f 4x4 4f", ["in_vert", "in_col"])],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, "4f 4x4 4f", ["in_vert", "in_col"])],
            mode=self.ctx.POINTS,
        )

        # Program for visualizing the balls
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec4 in_vert;
            in vec4 in_col;

            out vec2 v_pos;
            out float v_radius;
            out vec4 v_col;

            void main()
            {
                v_pos = in_vert.xy;
                v_radius = in_vert.w;
                v_col = in_col;
            }
            """,
            geometry_shader="""
            #version 330

            layout (points) in;
            layout (triangle_strip, max_vertices = 4) out;

            // Use arcade's global projection UBO
            uniform Projection {
                uniform mat4 matrix;
            } proj;

            in vec2 v_pos[];
            in vec4 v_col[];
            in float v_radius[];

            out vec2 g_uv;
            out vec3 g_col;

            void main() {
                vec2 center = v_pos[0];
                vec2 hsize = vec2(v_radius[0]);

                g_col = v_col[0].rgb;

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

                EndPrimitive();
            }

            """,
            fragment_shader="""
            #version 330

            in vec2 g_uv;
            in vec3 g_col;

            out vec4 out_color;

            void main()
            {
                if (length(vec2(0.5, 0.5) - g_uv.xy) > 0.25)
                {
                    discard;
                }

                vec3 c = g_col.rgb;
                // c.xy += v_uv.xy * 0.05;
                // c.xy += v_pos.xy * 0.75;
                out_color = vec4(c, 1.0);
            }
            """,
        )

    def on_draw(self):
        self.clear()
        self.ctx.disable(self.ctx.BLEND)

        # Change the force
        force = math.sin(self.time / 10) / 2, math.cos(self.time / 10) / 2

        # Bind buffer and run compute shader
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)
        self.cs["screen_size"] = self.get_size()
        self.cs["force"] = force
        self.cs["frame_time"] = self.frame_time
        self.cs.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the balls
        self.vao_2.render(self.program)

        # Swap the buffers around (we are ping-ping rendering between two buffers)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # Swap what geometry we draw
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

    def on_update(self, delta_time: float):
        self.time += delta_time
        self.frame_time = delta_time

    def gen_initial_data(self):
        for i in range(self.num_balls):
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
