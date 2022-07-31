"""
3D Example
This example needs pyrr installed for matrix math:
    pip install pyrr
"""
from pyglet.math import Mat4
import arcade
from arcade.gl import geometry


class MyGame(arcade.Window):

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
        self.time = 0

    def on_draw(self):
        self.clear()
        self.ctx.enable_only(self.ctx.CULL_FACE, self.ctx.DEPTH_TEST)

        translate = Mat4.from_translation((0, 0, -1.75))
        rx = Mat4.from_rotation(self.time, (1, 0, 0))
        ry = Mat4.from_rotation(self.time * 0.77, (0, 1, 0))
        modelview = rx @ ry @ translate
        self.program['modelview'] = modelview

        self.cube.render(self.program)

    def on_update(self, dt):
        self.time += dt

    def on_resize(self, width, height):
        """Set up viewport and projection"""
        self.ctx.viewport = 0, 0, width, height
        self.program['projection'] = Mat4.perspective_projection(self.aspect_ratio, 0.1, 100, fov=60)


if __name__ == "__main__":
    MyGame(800, 600, "3D Cube")
    arcade.run()
