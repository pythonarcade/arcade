"""
Simple instancing example.

We draw a triangle N times using instancing.
A position offset and color is passed in per instance.
To make things a bit more interesting we also rotate the triangle.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.instancing
"""

import random
from array import array

import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Instancing"


class GameView(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform float time;

            in vec2 in_vert;
            // Per instance data
            in vec2 in_offset;
            in vec4 in_color;

            out vec4 v_color;

            void main() {
                // Create rotation based on what instance we are drawing
                float angle = time * 0.5 + float(gl_InstanceID);
                mat2 rot = mat2(
                    cos(angle), sin(angle),
                    -sin(angle), cos(angle)
                );

                // scale down triangle, offset and rotate
                vec2 pos = (rot * (in_vert * 0.07)) + in_offset;

                gl_Position = vec4(pos, 0.0, 1.0);
                v_color = in_color;
            }
            """,
            fragment_shader="""
            #version 330

            in vec4 v_color;
            out vec4 out_color;

            void main() {
                out_color = v_color;
            }
            """,
        )

        self.instances = 1_000
        # Create triangle
        # fmt: off
        vertices = array("f", [
            # x, y
            0.0, 0.8,
            -0.8, -0.8,
            0.8, -0.8,
        ])
        # fmt: on

        # Generate per instance data. We'll create a generator function for this (less messy)
        def gen_instance_data(instances):
            random.seed(123456)
            for _ in range(instances):
                # random x and y
                yield random.uniform(-1.0, 1.0)
                yield random.uniform(-1.0, 1.0)
                # random rgba color
                yield random.uniform(0.1, 1.0)
                yield random.uniform(0.1, 1.0)
                yield random.uniform(0.1, 1.0)
                yield random.uniform(0.1, 1.0)

        per_instance = array("f", gen_instance_data(self.instances))

        self.geometry = self.ctx.geometry(
            [
                # Base geometry
                BufferDescription(
                    self.ctx.buffer(data=vertices),
                    "2f",
                    ["in_vert"],
                ),
                # Per instance buffer
                BufferDescription(
                    self.ctx.buffer(data=per_instance),
                    "2f 4f",
                    ["in_offset", "in_color"],
                    instanced=True,
                ),
            ],
            mode=self.ctx.TRIANGLES,
        )

    def on_draw(self):
        self.clear()
        self.ctx.enable(self.ctx.BLEND)

        self.program["time"] = self.time
        self.geometry.render(self.program, instances=self.instances)


if __name__ == "__main__":
    GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    arcade.run()
