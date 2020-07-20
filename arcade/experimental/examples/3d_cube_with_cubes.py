"""
3D Example
This example needs pyrr installed for matrix math:
    pip install pyrr
"""
from array import array

from pyrr import Matrix44

import arcade
from arcade.gl import geometry


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False)

        # Use the standard cube
        self.cube = geometry.cube()
        # Simple color lighting program for cube
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 projection;
            uniform mat4 modelview;

            in vec3 in_position;
            in vec3 in_normal;
            in vec2 in_uv;

            out vec3 normal;
            out vec3 pos;
            out vec2 uv;

            void main() {
                vec4 p = modelview * vec4(in_position, 1.0);
                gl_Position = projection * p;
                mat3 m_normal = transpose(inverse(mat3(modelview)));
                normal = m_normal * in_normal;
                pos = p.xyz;
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D texture0;
            uniform bool use_texture;
            out vec4 fragColor;

            in vec3 normal;
            in vec3 pos;
            in vec2 uv;

            void main()
            {
                float l = dot(normalize(-pos), normalize(normal));
                if (use_texture) {
                    fragColor = vec4(texture(texture0, uv).rgb * (0.25 + abs(l) * 0.75), 1.0);
                } else {
                    fragColor = vec4(1.0) * (0.25 + abs(l) * 0.75);
                }
            }
            """,
        )
        # Program for drawing fullscreen quad with texture
        self.quad_program = self.ctx.program(
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

            uniform sampler2D texture0;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                fragColor = texture(texture0, uv);
            }
            """,
        )
        self.quad_fs = geometry.quad_2d_fs()

        self.on_resize(*self.get_size())
        self.time = 0
        self.frame = 0

        self.fbo1 = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.get_size()))],
            depth_attachment=self.ctx.depth_texture(self.get_size()),
        )
        self.fbo2 = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((self.get_size()))],
            depth_attachment=self.ctx.depth_texture(self.get_size()),
        )

    def on_draw(self):
        self.ctx.enable_only(self.ctx.CULL_FACE, self.ctx.DEPTH_TEST)

        # Draw the current cube using the last one as a texture
        self.fbo1.use()
        self.fbo1.clear(color=(1.0, 1.0, 1.0, 1.0), normalized=True)
        rotate = Matrix44.from_eulers((self.time, self.time * 0.77, self.time * 0.01), dtype='f4')
        translate = Matrix44.from_translation((0, 0, -1.75), dtype='f4')
        modelview = translate * rotate
        if self.frame > 0:
            self.program['use_texture'] = 1
            self.fbo2.color_attachments[0].use()
        self.program['modelview'] = modelview.flatten()
        self.cube.render(self.program)

        self.ctx.disable(self.ctx.DEPTH_TEST)

        # Draw the current cube texture
        self.use()
        self.clear()
        self.fbo1.color_attachments[0].use()
        self.quad_fs.render(self.quad_program)

        # Swap offscreen buffers
        self.fbo1, self.fbo2 = self.fbo2, self.fbo1
        self.frame += 1

    def on_update(self, dt):
        self.time += dt

    def on_resize(self, width, height):
        """Set up viewport and projection"""
        ratio = arcade.get_scaling_factor(self)
        self.ctx.viewport = 0, 0, int(width * ratio), int(height * ratio)
        aspect_ratio = width / height
        self.program['projection'] = Matrix44.perspective_projection(60, aspect_ratio, 0.1, 100).flatten()


if __name__ == "__main__":
    MyGame(720, 720, "3D Cube")
    arcade.run()
