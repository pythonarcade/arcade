from array import array
import random
import struct
import arcade
from arcade.gl import BufferDescription, geometry

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Transform Feedback"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.dt = 0
        self.points_progran = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_pos;
            out vec3 color;
            void main() {
                color = vec3(
                    mod((gl_VertexID * 100 % 11) / 10.0, 1.0),
                    mod((gl_VertexID * 100 % 27) / 10.0, 1.0),
                    mod((gl_VertexID * 100 % 71) / 10.0, 1.0));
                gl_Position = vec4(in_pos, 0.0, 1.0);
            }
            """,
            fragment_shader="""
            #version 330

            in vec3 color;
            out vec4 fragColor;

            void main() {
                fragColor = vec4(color, 1.0);
            }
            """,
        )

        self.gravity_program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform float dt;
            uniform float force;

            in vec2 in_pos;
            in vec2 in_vel;

            out vec2 out_pos;
            out vec2 out_vel;

            void main() {
                vec2 gravity_pos = vec2(0.0, 0.0);
                vec2 dir = normalize(gravity_pos - in_pos) * force;
                vec2 vel = in_vel + dir / length(dir) * dt;

                out_vel = vel;
                out_pos = in_pos + vel * dt;
            }
            """,
        )
        N = 2000
        self.buffer_1 = self.ctx.buffer(data=array('f', self.gen_initial_data(N)))
        self.buffer_2 = self.ctx.buffer(reserve=self.buffer_1.size)

        self.vao_1 = self.ctx.geometry([BufferDescription(self.buffer_1, '2f 2x4', ['in_pos'])])
        self.vao_2 = self.ctx.geometry([BufferDescription(self.buffer_2, '2f 2x4', ['in_pos'])])

        self.gravity_1 = self.ctx.geometry([BufferDescription(self.buffer_1, '2f 2f', ['in_pos', 'in_vel'])])
        self.gravity_2 = self.ctx.geometry([BufferDescription(self.buffer_2, '2f 2f', ['in_pos', 'in_vel'])])

    def gen_initial_data(self, count):
        for _ in range(count):
            yield random.uniform(-1.2, 1.2)  # pos x
            yield random.uniform(-1.2, 1.2)  # pos y
            yield random.uniform(-.3, .3)  # velocity x
            yield random.uniform(-.3, .3)  # velocity y

    def on_draw(self):
        self.clear()
        self.ctx.point_size = 3

        self.gravity_program['dt'] = self.dt
        self.gravity_program['force'] = 0.75

        # Transform data
        self.gravity_1.transform(self.gravity_program, self.buffer_2)
        # Render the result
        self.vao_2.render(self.points_progran, mode=self.ctx.POINTS)

        # Swap around stuff ...
        self.gravity_1, self.gravity_2 = self.gravity_2, self.gravity_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1
        self.buffer_1, self.buffer_2 = self.buffer_2, self.buffer_1

    def on_update(self, dt):
        self.dt = dt / 4


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
