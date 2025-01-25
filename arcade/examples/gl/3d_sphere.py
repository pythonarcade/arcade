"""
A 3D sphere example.

We're showing how to use the geometry.sphere() function to create a sphere
and how different context flags affects the rendering of a 3d object.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.3d_sphere
"""

import arcade
from arcade.math import clamp
from arcade.gl import geometry
from pyglet.math import Mat4, Vec3
from pyglet.graphics import Batch


class Sphere3D(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.sphere = geometry.sphere(1.0, 32, 32, uvs=False)
        # Simple color lighting program
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform WindowBlock {
                mat4 projection;
                mat4 view;
            } window;

            in vec3 in_position;
            in vec3 in_normal;

            out vec3 normal;
            out vec3 pos;

            void main() {
                vec4 p = window.view * vec4(in_position, 1.0);
                gl_Position = window.projection * p;
                mat3 m_normal = transpose(inverse(mat3(window.view)));
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
                // Draw front and back face differently
                if (l < 0.0) {
                    l = abs(l);
                    fragColor = vec4(0.75, 0.0, 0.0, 1.0) * (0.25 + abs(l) * 0.75);
                } else {
                    fragColor = vec4(1.0) * (0.25 + abs(l) * 0.75);
                }
            }
            """,
        )
        self.on_resize(*self.get_size())

        self.text_batch = Batch()
        self.text_cull = arcade.Text(
            "F2: Toggle cull face (True)",
            x=10,
            y=10,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )
        self.text_depth = arcade.Text(
            "F1: Toggle depth test (True)",
            x=10,
            y=30,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )
        self.text_wireframe = arcade.Text(
            "SPACE: Toggle wireframe (False)",
            x=10,
            y=50,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )
        self.text_fs = arcade.Text(
            "F: Toggle fullscreen (False)",
            x=10,
            y=70,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )
        self.text_vert_count = arcade.Text(
            "Use mouse wheel to add/remove vertices",
            x=10,
            y=90,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )
        self.text_rotate = arcade.Text(
            "Drag mouse to rotate object",
            x=10,
            y=110,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )

        self.set_vsync(True)

        self.rot_x = 0
        self.rot_y = 0
        self.wireframe = True
        self.vert_count = 0.5
        self.drag_time = None
        self.flags = set([self.ctx.DEPTH_TEST])

    def on_draw(self):
        self.clear()
        self.ctx.enable_only(*self.flags)
        self.ctx.wireframe = self.wireframe
        time = self.drag_time or self.time

        # Position and rotate the sphere
        translate = Mat4.from_translation(Vec3(0, 0, -2.5))
        rx = Mat4.from_rotation(time + self.rot_x, Vec3(0, 1, 0))
        ry = Mat4.from_rotation(time + self.rot_y, Vec3(1, 0, 0))
        # Set matrices and draw
        self.view = translate @ rx @ ry
        self.projection = Mat4.perspective_projection(self.aspect_ratio, 0.1, 100, fov=60)
        self.sphere.render(self.program, vertices=int(self.sphere.num_vertices * self.vert_count))

        # Switch to 2D mode when drawing text
        self.projection = Mat4.orthogonal_projection(0, self.width, 0, self.height, -1, 1)
        self.ctx.disable(self.ctx.DEPTH_TEST, self.ctx.CULL_FACE)
        self.ctx.wireframe = False
        self.view = Mat4()

        with self.ctx.enabled_only():
            self.text_batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.close()

        elif key == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
            self.text_fs.text = f"F: Toggle fullscreen ({self.fullscreen})"

        elif key == arcade.key.SPACE:
            self.wireframe = not self.wireframe
            self.set_vsync(True)
            self.text_wireframe.text = f"SPACE: Toggle wireframe ({self.wireframe})"

        elif key == arcade.key.F1:
            if self.ctx.DEPTH_TEST in self.flags:
                self.flags.remove(self.ctx.DEPTH_TEST)
            else:
                self.flags.add(self.ctx.DEPTH_TEST)
            self.text_depth.text = f"F1: Toggle depth test ({self.ctx.DEPTH_TEST in self.flags})"

        elif key == arcade.key.F2:
            if self.ctx.CULL_FACE in self.flags:
                self.flags.remove(self.ctx.CULL_FACE)
            else:
                self.flags.add(self.ctx.CULL_FACE)
            self.text_cull.text = f"F2: Toggle cull face ({self.ctx.CULL_FACE in self.flags})"

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.drag_time = self.time
        self.rot_x += dx / 100
        self.rot_y -= dy / 100

    def on_mouse_release(self, x, y, button, modifiers):
        self.drag_time = None

    def on_mouse_scroll(self, x: int, y: int, scroll_x: float, scroll_y: float):
        self.vert_count = clamp(self.vert_count + scroll_y / 500, 0.0, 1.0)


if __name__ == "__main__":
    window = Sphere3D(1280, 720, "3D Cube")
    window.set_vsync(True)
    arcade.run()
