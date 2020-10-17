"""
Example using index buffers with 1, 2, and 4 byte size.
In most cases we can get away with unsigned 32 bit integers.
Still it can be useful to 
"""
from array import array

import arcade
from arcade.gl import BufferDescription


class IndexBufferExample(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_position;
            in vec3 in_color;

            out vec3 v_color;

            void main() {
                gl_Position = vec4(in_position, 0.0, 1.0);
                v_color = in_color;
            }
            """,
            fragment_shader="""
            #version 330

            out vec4 out_color;
            in vec3 v_color;

            void main() {
                // out_color = vec4(v_color, 1.0);
                out_color = vec4(1.0);
            }
            """
        )

        # RGB colors
        self.color_buffer = self.ctx.buffer(data=array('f', [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            0.0, 1.0, 1.0,
        ]))

        # Vertices
        self.position_buffer = self.ctx.buffer(data=array('f',
            [
                0.0, 0.0,  # lower left
                1/3, 0.0,  # lower right
                1/3, 1.0,  # upper right
                0.0, 1.0,  # upper left
            ]
        ))
        self.ibo_32 = self.ctx.buffer(data=array('I', [0, 1, 2]))

        self.vbo = self.ctx.geometry(
            [
                BufferDescription(self.position_buffer, "2f", ["in_position"]),
                BufferDescription(self.color_buffer, "3f", ["in_color"]),
            ],
            index_buffer=self.ibo_32,
        )
        print(self.vbo.num_vertices)

    def on_draw(self):
        self.clear()
        self.vbo.render(self.program, mode=self.ctx.TRIANGLES, vertices=3)


if __name__ == "__main__":
    IndexBufferExample(800, 600, "Index Buffers: 8, 16 and 32 bit")
    arcade.run()
