"""
Redering to texture with a compute shader
"""

import arcade
from arcade.gl import geometry

SIZE = 512, 512

COMPUTE_SHADER = """
#version 430

layout (local_size_x = 16, local_size_y = 16) in;
// match the input texture format!
layout(rgba8, location=0) writeonly uniform image2D destTex;
uniform float time;

void main() {
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);

    // Calculate 1.0 - distance from the center in each work group
    float local = 1.0 - length(vec2(ivec2(gl_LocalInvocationID.xy) - 8) / 8.0);

    // Wave covering the screen diagonally
    float global = sin(float(gl_WorkGroupID.x + gl_WorkGroupID.y) * 0.1 + time) / 2.0 + 0.5;
    imageStore(destTex, texelPos, vec4(local, global, 0.0, 1.0));
}
"""


class App(arcade.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*SIZE, "Compute Shader", gl_version=(4, 3))
        self.time = 0
        self.cs = self.ctx.compute_shader(source=COMPUTE_SHADER)
        self.texture = self.ctx.texture(SIZE, components=4)
        self.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

        # Visualize the texture
        self.program = self.ctx.program(
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

            uniform sampler2D image;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                fragColor = texture(image, uv);
            }
            """,
        )
        self.quad = geometry.quad_2d_fs()

    def on_draw(self):
        self.clear()

        # Calculate invocation parameters
        w, h = self.texture.size
        gw, gh = 16, 16  # group size
        nx, ny, nz = w // gw, h // gh, 1

        # Bind image + run compute shader
        self.texture.bind_to_image(0, write=True)
        self.cs.run(group_x=nx, group_y=ny, group_z=nz)

        # Visualize the generated texture
        self.texture.use(0)
        self.quad.render(self.program)

    def on_update(self, delta_time: float):
        self.time += delta_time
        self.cs["time"] = self.time * 10


app = App()
arcade.run()
