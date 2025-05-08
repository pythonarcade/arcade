"""
3D Example with offscreen rendering.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.3d_cube_with_cubes
"""

from pyglet.math import Mat4, Vec3

import arcade
from arcade.gl import geometry


class GameView(arcade.Window):

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
        self.frame = 0

        self.fbo1 = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(self.get_size())],
            depth_attachment=self.ctx.depth_texture(self.get_size()),
        )
        self.fbo2 = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(self.get_size())],
            depth_attachment=self.ctx.depth_texture(self.get_size()),
        )

    def on_draw(self):
        self.ctx.enable_only(self.ctx.CULL_FACE, self.ctx.DEPTH_TEST)

        # Draw the current cube using the last one as a texture
        self.fbo1.use()
        self.fbo1.clear(color_normalized=(1.0, 1.0, 1.0, 1.0))

        translate = Mat4.from_translation(Vec3(0, 0, -1.75))
        rx = Mat4.from_rotation(self.time, Vec3(1, 0, 0))
        ry = Mat4.from_rotation(self.time, Vec3(0, 1, 0))
        modelview = translate @ rx @ ry

        self.program["use_texture"] = 1
        self.fbo2.color_attachments[0].use()

        self.program["modelview"] = modelview
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

    def on_resize(self, width, height):
        """Set up viewport and projection"""
        self.ctx.viewport = 0, 0, width, height
        self.program["projection"] = (
            Mat4.perspective_projection(self.aspect_ratio, 0.1, 100, fov=60)
        )


if __name__ == "__main__":
    GameView(720, 720, "3D Cube").run()
