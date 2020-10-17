"""
Example using index buffers with 1, 2, and 4 byte size.
In most cases we can get away with unsigned 32 bit integers.
Still it can be useful to 
"""
from array import array
import arcade


class IndexBufferExample(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 projection;

            in vec2 in_position;
            in vec3 in_color;

            out vec3 v_color;

            void main() {
                gl_Position = projection * vec4(in_position, 0.0, 1.0);
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

    def on_draw(self):
        self.clear()


if __name__ == "__main__":
    IndexBufferExample(800, 600, "Index Buffers: 8, 16 and 32 bit")
    arcade.run()
