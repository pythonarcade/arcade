import struct
import arcade
from arcade.gl import geometry

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Basic Renderer"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            out float value;

            void main() {
                value = gl_VertexID;
            }
            """,
        )
        self.vao = self.ctx.geometry()
        self.buffer = self.ctx.buffer(reserve=40)
        self.vao.transform(self.program, self.buffer, vertices=10)
        print(struct.unpack('10f', self.buffer.read()))

    def on_draw(self):
        pass


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
