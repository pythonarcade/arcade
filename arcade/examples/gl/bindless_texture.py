"""
Builds on the custom sprite example adding bindless textures.

The old way of using textures is binding them to a texture unit
and assign that unit to a sampler in a shader. This is a global
state and can be a bit cumbersome to work with when you have
many textures and draw calls. It also means you have to build
texture atlases to properly batch draw calls. This comes with
additional complexity, limitations and challenges.

Bindless textures are textures referenced using a 64 bit integer
we call a "handle". This handle can be stored in a buffer and
declared as a sampler type (it's a 64 bit integer under the hood).
There is no need to bind the texture. They are all just available
though the handles.

This example builds on the custom sprite shader example.
We render points and use a geometry shader to expand them to
quads.

Note that texture handles are very unsafe. Using non-existing
handles or handles that are not resident can cause crashes.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.bindless_texture
"""

from array import array
from itertools import cycle

import arcade
from arcade.gl import BufferDescription, Texture2D


class BindlessTexture(arcade.Window):

    def __init__(self):
        super().__init__(
            1280,
            720,
            "Bindless Texture Example",
            resizable=True,
            gl_version=(4, 3),
        )

        # Custom sprite shader program using bindless textures
        self.program = self.ctx.program(
            vertex_shader="""
            #version 430

            // The point position
            in vec2 in_position;
            // Pass the vertex index (0, 1, ...) to the geometry shader
            flat out int v_texture_index;

            void main() {
                gl_Position = vec4(in_position, 0.0, 1.0);
                v_texture_index = gl_VertexID;
            }
            """,
            geometry_shader="""
            #version 430

            layout(points) in;
            layout(triangle_strip, max_vertices=4) out;

            // The global window block with matrices (always present)
            uniform WindowBlock {
                mat4 projection;
                mat4 view;
            } window;

            // Pick up the texture index from the vertex shader
            flat in int v_texture_index[];
            // Pass the texture index to the fragment shader
            flat out int texture_index;
            out vec2 uv;

            void main() {
                // Create some more convenient variables for the input
                vec2 center = gl_in[0].gl_Position.xy;
                vec2 hsize = vec2(40, 40);

                texture_index = v_texture_index[0];

                // Emit a triangle strip of 4 vertices making a triangle.
                // The fragment shader will then fill these to triangles in the next stage.
                mat4 mvp = window.projection * window.view;

                // Upper left
                gl_Position = mvp * vec4(vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
                uv = vec2(0, 1);
                EmitVertex();

                // lower left
                gl_Position =mvp * vec4(vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
                uv = vec2(0, 0);
                EmitVertex();

                // upper right
                gl_Position = mvp * vec4(vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
                uv = vec2(1, 1);
                EmitVertex();

                // lower right
                gl_Position = mvp * vec4(vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
                uv = vec2(1, 0);
                EmitVertex();

                // We are done with this triangle strip now
                EndPrimitive();
            }
            """,
            fragment_shader="""
            #version 460
            #extension GL_ARB_bindless_texture : require

            // This is the structure of the data in the shader storage buffer.
            // The texture handles in the buffer are 64 bit integers and are
            // automatically converted into sampler objects for us.
            struct TextureRef {
                layout (bindless_sampler) sampler2D tex; // 64 bit integer
            };

            // Shader storage buffer with texture handles
            layout(std430, binding=0) buffer BindlessData
            {
                TextureRef Materials[];
            } bindless_data;

            // Get the texture index from the geometry shader
            in flat int texture_index;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                // Look up the sampler in the shader storage buffer
                TextureRef ref = bindless_data.Materials[texture_index];
                // Write pixel to screen
                fragColor = texture(ref.tex, uv);
            }
            """,
        )

        self.handles = []
        self.textures: list[Texture2D] = []
        # Make a cycle iterator from Arcade's resources (images)
        resources = arcade.resources.list_built_in_assets(name="female", extensions=(".png",))
        resource_cycle = cycle(resources)

        # Load enough textures to cover for each point/sprite
        for i in range(16 * 9):
            texture = self.ctx.load_texture(
                next(resource_cycle),
                immutable=True,
                wrap_x=self.ctx.CLAMP_TO_EDGE,
                wrap_y=self.ctx.CLAMP_TO_EDGE,
            )
            # Make sure we keep a reference to the texture to avoid GC
            self.textures.append(texture)
            # Create a texture handle and make it resident.
            self.handles.append(texture.get_handle(resident=True))

        # Create the shader storage buffer with the texture handles
        self.texture_ssbo = self.ctx.buffer(data=array("Q", self.handles))

        # Generate some points/positions for our sprites
        pos = []
        for y in range(9):
            for x in range(16):
                pos.extend([x * 80 + 40, y * 80 + 40])

        # Create a buffer with the positions
        self.buffer_pos = self.ctx.buffer(data=array("f", pos))
        # Create a geometry object with the positions
        self.geometry = self.ctx.geometry(
            [BufferDescription(self.buffer_pos, "2f", ["in_position"])],
            mode=self.ctx.POINTS,
        )

    def on_draw(self):
        self.clear()
        self.ctx.enable(self.ctx.BLEND)
        # Bind the SSBO with texture handles to binding point 0
        # matching the binding point in the shader.
        self.texture_ssbo.bind_to_storage_buffer(binding=0)

        # Draw the sprites
        self.geometry.render(self.program)


BindlessTexture().run()
