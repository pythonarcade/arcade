"""
Drawing bezier curve using tessellation shader.
This example is ported from moderngl : https://github.com/moderngl/moderngl/blob/master/examples/tesselation.py
"""
from array import array

import arcade
from arcade.gl import BufferDescription

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Bezier Curve Tessellation"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        self.time = 0
        super().__init__(width, height, title, gl_version=(4, 1))
        self.program = self.ctx.program(
            vertex_shader="""
            #version 400 core

            uniform float time;
            in vec2 in_vert;

            void main() {
                vec2 pos = vec2(in_vert.x, sin(in_vert.y + in_vert.x * 1.5 + time * 0.5));
                gl_Position = vec4(pos, 0.0, 1.0);
            }
            """,
            tess_control_shader="""
            #version 400 core

            uniform float time;
            layout(vertices = 4) out;

            void main() {
                // set tesselation levels (can be computed dynamically)
                gl_TessLevelOuter[0] = 1;
                gl_TessLevelOuter[1] = int(time * 2) % 32 + 1;
                // pass through vertex positions
                gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
            }
            """,
            tess_evaluation_shader="""
            #version 400 core

            layout(isolines, fractional_even_spacing, ccw) in;

            // compute a point on a bezier curve with the points p0, p1, p2, p3
            // the parameter u is in [0, 1] and determines the position on the curve
            vec3 bezier(float u, vec3 p0, vec3 p1, vec3 p2, vec3 p3) {
                float B0 = (1.0 - u) * (1.0 - u) * (1.0 - u);
                float B1 = 3.0 * (1.0 - u) * (1.0 - u) * u;
                float B2 = 3.0 * (1.0 - u) * u * u;
                float B3 = u * u * u;
                return B0 * p0 + B1 * p1 + B2 * p2 + B3 * p3;
            }
            void main() {
                float u = gl_TessCoord.x;
                vec3 p0 = vec3(gl_in[0].gl_Position);
                vec3 p1 = vec3(gl_in[1].gl_Position);
                vec3 p2 = vec3(gl_in[2].gl_Position);
                vec3 p3 = vec3(gl_in[3].gl_Position);
                gl_Position = vec4(bezier(u, p0, p1, p2, p3), 1.0);
            }
            """,
            fragment_shader="""
            #version 400 core

            out vec4 frag_color;

            void main() {
                frag_color = vec4(1.0);
            }
            """
        )

        # We are processing patches of 4 vertices
        self.ctx.patch_vertices = 4

        vertices = array(
            "f",
            # x, y
            [
                -1.0, 0.0,
                -0.5, 1.0,
                0.5, -1.0,
                1.0, 0.0,
            ]
        )
        self.geometry = self.ctx.geometry([
            BufferDescription(
                self.ctx.buffer(data=vertices),
                "2f",
                ["in_vert"]
            )
        ])

    def on_draw(self):
        self.clear()
        self.program["time"] = self.time
        self.geometry.render(self.program, mode=self.ctx.PATCHES)

    def on_update(self, dt):
        self.time += dt


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
