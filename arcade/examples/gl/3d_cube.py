"""
Simple 3D Example

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.3d_cube
"""

from pyglet.math import Mat4, Vec3
import arcade
from arcade.gl import geometry


class GameView(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.set_vsync(True)
        # Use the standard cube
        self.cube = geometry.cube()
        # Simple color lighting program
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 projection;
            uniform mat4 modelview;

            in vec3 in_position;
            in vec3 in_normal;

            out vec3 normal;
            out vec3 pos;

            void main() {
                vec4 p = modelview * vec4(in_position, 1.0);
                gl_Position = projection * p;
                mat3 m_normal = transpose(inverse(mat3(modelview)));
                normal = m_normal * in_normal;
                pos = p.xyz;
            }
            """,
            fragment_shader="""
            #version 330

            out vec4 fragColor;

            in vec3 normal;
            in vec3 pos;

            void main()
            {
                float l = dot(normalize(-pos), normalize(normal));
                fragColor = vec4(1.0) * (0.25 + abs(l) * 0.75);
            }
            """,
        )
        self.on_resize(*self.get_size())

    def on_draw(self):
        self.clear()
        self.ctx.enable_only(self.ctx.CULL_FACE, self.ctx.DEPTH_TEST)

        translate = Mat4.from_translation(Vec3(0, 0, -1.75))
        rx = Mat4.from_rotation(self.time, Vec3(1, 0, 0))
        ry = Mat4.from_rotation(self.time * 0.77, Vec3(0, 1, 0))
        modelview = translate @ rx @ ry
        self.program["modelview"] = modelview

        self.cube.render(self.program)

    def on_resize(self, width, height):
        """Set up viewport and projection"""
        self.ctx.viewport = 0, 0, width, height
        self.program["projection"] = (
            Mat4.perspective_projection(self.aspect_ratio, 0.1, 100, fov=60)
        )


if __name__ == "__main__":
    GameView(1280, 720, "3D Cube")
    arcade.run()
