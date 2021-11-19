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
                out_color = vec4(v_color, 1.0);
            }
            """
        )

        # Vertices
        self.vertex_buffer = self.ctx.buffer(data=array(
            'f',
            [
                # x  y    r    g    b
                -1.0, -1.0, 1.0, 0.0, 0.0,  # lower left
                1, -1.0, 0.0, 1.0, 0.0,  # lower right
                1.0, 1.0, 0.0, 0.0, 1.0,  # upper right
                -1.0, 1.0, 0.0, 1.0, 1.0,  # upper left
                0, 0, 0, 0, 0,  # dummy data for testing
            ]
        ))
        self.ibo_8 = self.ctx.buffer(data=array('B', [3, 0, 2, 1]))
        self.ibo_16 = self.ctx.buffer(data=array('H', [3, 0, 2, 1]))
        self.ibo_32 = self.ctx.buffer(data=array('I', [3, 0, 2, 1]))

        self.vao_32 = self.ctx.geometry(
            [
                BufferDescription(self.vertex_buffer, "2f 3f", ["in_position", "in_color"]),
            ],
            index_buffer=self.ibo_32,
            index_element_size=4,
            mode=self.ctx.TRIANGLE_STRIP
        )
        self.vao_16 = self.ctx.geometry(
            [
                BufferDescription(self.vertex_buffer, "2f 3f", ["in_position", "in_color"]),
            ],
            index_buffer=self.ibo_16,
            index_element_size=2,
            mode=self.ctx.TRIANGLE_STRIP
        )
        self.vao_8 = self.ctx.geometry(
            [
                BufferDescription(self.vertex_buffer, "2f 3f", ["in_position", "in_color"]),
            ],
            index_buffer=self.ibo_16,
            index_element_size=2,
            mode=self.ctx.TRIANGLE_STRIP
        )
        self.frames = 0

    def on_draw(self):
        self.clear()

        mode = self.frames % 3
        if mode == 0:
            self.vao_8.render(self.program, mode=self.ctx.TRIANGLE_STRIP)
        elif mode == 1:
            self.vao_16.render(self.program, mode=self.ctx.TRIANGLE_STRIP)
        elif mode == 2:
            self.vao_32.render(self.program, mode=self.ctx.TRIANGLE_STRIP)

        self.frames += 1


if __name__ == "__main__":
    IndexBufferExample(800, 600, "Index Buffers: 8, 16 and 32 bit")
    arcade.run()
