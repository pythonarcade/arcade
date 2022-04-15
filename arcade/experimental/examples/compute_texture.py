"""
Rendering to texture with a compute shader
"""

import arcade
from arcade.gl import geometry

SIZE = 512, 512

COMPUTE_SHADER = """
#version 430

// Describes the minimal amount of work this compute shader
// can execute. 16 x 16 = 256 threads. When we run a compute
// shader we specify how many of these groups we are executing.
// This is called a work group.
layout (local_size_x = 16, local_size_y = 16) in;

// tell OpenGL what format the image is (rgba8).
// Important: The binding needs to match the unit
// Parameter in Texture.bind_to_image.
// Each image needs a different binding unit starting from 0
layout(rgba8, binding=0) uniform writeonly image2D destTex;

uniform float time;

void main() {
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);

    // Calculate 1.0 - distance from the center in each work group
    // gl_LocalInvocationID is the current (x, y) invocation in your work group.
    // We make a 16 x 16 square containing the inverse distance from the center
    float local = 1.0 - length(vec2(ivec2(gl_LocalInvocationID.xy) - 8) / 8.0);

    // Wave covering the screen diagonally using the global invocation value.
    // This would pretty much be the pixel location
    float global = sin(float(gl_GlobalInvocationID.x + gl_GlobalInvocationID.y) * 0.01 + time) / 2.0 + 0.5;
    imageStore(destTex, texelPos, vec4(local, global, 0.0, 1.0));
}
"""


class App(arcade.Window):

    def __init__(self, *args, **kwargs):
        # We need to specify OpenGL 4.3 when using Compute Shaders
        super().__init__(*SIZE, "Compute Shader", gl_version=(4, 3))
        self.time = 0
        self.cs = self.ctx.compute_shader(source=COMPUTE_SHADER)
        self.texture = self.ctx.texture(SIZE, components=4)
        self.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

        # Simple program rendering textured retangle to the screen
        # using normalized device coordinates (no projection)
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
        # Group size is configured to be 16 x 16 in the shader source.
        gw, gh = 16, 16
        # Figure how many groups (16 x 16 tiles) the image consists of
        # This example is a 512 x 512 by default so we will will get
        # 32 x 32 groups/tiles = 1024 work groups executed in total.
        nx, ny = w // gw, h // gh

        # Bind image + run compute shader
        self.texture.bind_to_image(0, write=True)

        # Run the compute shader
        self.cs.run(group_x=nx, group_y=ny)

        # Visualize the generated texture
        self.texture.use(0)
        self.quad.render(self.program)

    def on_update(self, delta_time: float):
        self.time += delta_time
        self.cs["time"] = self.time * 10


app = App()
arcade.run()
