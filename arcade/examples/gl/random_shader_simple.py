"""
Simple shader based noise example

The code creates squares of random colors all around the Window.
Uses code injection to use the built-in random.glsl file. This allows for easy access
to a high quality hash function and methods of using 1, 2, 3, or 4 floats as seeds.
The function generates a value between 0 and 1.

It is very important when using the x and y coordinates to try use both in all instances
If you only use one you will get very obvious artifacts all along the axis that not used.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.random_shader_simple
"""

from time import time
from array import array
from random import random

from arcade import Window
from arcade.gl import BufferDescription


def generate_points(count: int):
    for _ in range(count):
        yield random() * 2 - 1
        yield random() * 2 - 1


class App(Window):

    def __init__(self):
        super().__init__()
        # the number of points we want showing up
        self._point_count = 128
        # so that the colours change every run we store the time at run to use as a seed
        self._time_seed = time()
        self._program = self.ctx.program(
            # We're passing the shader source to ctx.shader_inc() so that we can use
            # the #include directive. This is not needed when using load_program() as
            # it will automatically look for the file.
            vertex_shader=self.ctx.shader_inc(
                """
                #version 330

                in vec2 in_pos;

                // This in the index of this specific vertex.
                // Flat just specifies that the value shouldn't be interpolated between vertices.
                flat out int vert_id;
                out vec2 vert_pos;

                void main(){
                    gl_Position = vec4(in_pos, 0.0, 1.0);

                    vert_id = gl_VertexID;
                    vert_pos = in_pos;
                }
                """
            ),
            fragment_shader=self.ctx.shader_inc("""
            #version 330

            #include :resources:/shaders/lib/random.glsl

            // Predefining the function which will be over written with the code injection.
            // the random function takes in 1, 2, 3, or 4 floats and returns a new float
            // between 0 and 1
            float random(vec2 v);
            float random(vec3 v);
            float random(vec4 v);

            // Both of these are used as seed values to make sure each call is unique
            uniform float time_seed;
            flat in int vert_id;

            // so each pixel in each vertex has the same color we pass in the position
            in vec2 vert_pos;

            out vec4 frag_colour;

            void main() {
                float red = random(vec4(vert_pos.x, vert_pos.y, time_seed, vert_id));
                float green = random(vec4(vert_id, time_seed, vert_pos.y, vert_pos.x));
                float blue = random(vec4(vert_pos.y, vert_pos.x, time_seed, vert_id));
                frag_colour = vec4(red, green, blue, 1.0);
            }
            """),
        )
        self._program["time_seed"] = self._time_seed

        self._geometry = self.ctx.geometry(
            [
                BufferDescription(
                    self.ctx.buffer(data=array("f", generate_points(self._point_count))),
                    "2f",
                    ["in_pos"],
                )
            ],
            mode=self.ctx.POINTS,
        )

    def on_draw(self):
        self.clear()
        self.ctx.point_size = 16.0
        self._geometry.render(self._program)


App().run()
