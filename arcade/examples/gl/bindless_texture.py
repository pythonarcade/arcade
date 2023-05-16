"""
Builds on the custom sprite example adding bindless textures.

The old way of using textures is binding them to a texture unit
and assign that unit to a sampler in the shader. This is a global
state and can be a bit cumbersome to work with when you have
many textures and draw calls. It also means you have to build
texture atlases to properly batch draw calls. This comes with
additional complexity, limitations and challenges.

Bindless textures are textures referenced using a 64 bit integer
we call a "handle". This handle can be stored in a buffer and
declared as a sampler type (it's a 64 bit integer under the hood).
There is no need to bind the texture. They are all just available
though the handles.
"""
from array import array
from typing import List
from itertools import cycle

import arcade
from arcade.gl import BufferDescription, Texture2D


class BindlessTexture(arcade.Window):

    def __init__(self):
        super().__init__(
            1280, 720,
            "Bindless Texture Example",
            resizable=True, gl_version=(4, 3),
        )
        self.program = self.ctx.program(
            vertex_shader="""
            #version 430

            in vec2 in_position;
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

            uniform WindowBlock {
                mat4 projection;
                mat4 view;
            } window;

            flat in int v_texture_index[];
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
            #version 430
            #extension GL_ARB_bindless_texture : require

            struct TextureRef {
                sampler2D tex; // 64 bit integer
            };

            layout(std430, binding=0) buffer BindlessData
            {
                TextureRef Materials[4];
            } bindless_data;

            in flat int texture_index;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                TextureRef ref = bindless_data.Materials[texture_index];
                fragColor = texture(ref.tex, uv);
            }
            """,
        )

        self.handles = []
        self.textures: List[Texture2D] = []
        resources = [
            getattr(arcade.resources, resource)
            for resource in dir(arcade.resources) if resource.startswith('image_')]
        resource_cycle = cycle(resources)

        for i in range(512):
            texture = self.ctx.load_texture(next(resource_cycle))
            texture.wrap_x = self.ctx.CLAMP_TO_EDGE
            texture.wrap_y = self.ctx.CLAMP_TO_EDGE
            self.textures.append(texture)
            self.handles.append(texture.get_handle(resident=True))

        self.texture_ssbo = self.ctx.buffer(data=array('Q', self.handles))

        pos = []
        for y in range(9):
            for x in range(16):
                pos.extend([x * 80 + 40, y * 80 + 40])

        self.buffer_pos = self.ctx.buffer(data=array('f', pos))
        self.geometry = self.ctx.geometry(
            [BufferDescription(self.buffer_pos, '2f', ['in_position'])],
            mode=self.ctx.POINTS,
        )

    def on_draw(self):
        self.texture_ssbo.bind_to_storage_buffer(binding=0)
        self.geometry.render(self.program)


BindlessTexture().run()
