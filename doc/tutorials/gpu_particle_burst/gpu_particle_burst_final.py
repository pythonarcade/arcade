"""
Example showing how to create particle explosions via the GPU.
"""
from array import array
import math
import time
import random
import arcade
from arcade.gl import BufferDescription

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "GPU Particle Explosion"

PARTICLE_COUNT = 10000
GRAVITY = 0.3

MIN_FADE_TIME = 0.25
MAX_FADE_TIME = 1.5

class Burst:
    buffer = None
    vao = None
    start_time = None

class MyWindow(arcade.Window):
    """ Main window"""
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.burst_list = []

        # Program to visualize the points
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            uniform float time;
            uniform float gravity;
            
            in vec2 in_pos;
            in vec2 in_vel;
            in float in_fade;
            in vec3 in_color;
            out vec4 color;

            void main() {

               float alpha = 1.0 - (in_fade * time);
               if(alpha < 0.0) alpha = 0;
               color = vec4(in_color[0], in_color[1], in_color[2], alpha);

                vec2 new_vel = in_vel;
                new_vel[1] -= time * gravity;

                vec2 new_pos = in_pos + (new_vel * time);
                gl_Position = vec4(new_pos, 0.0, 1);
            }
            """,
            fragment_shader="""
            #version 330

            // Color passed in from the vertex shader
            in vec4 color;
            // The pixel we are writing to in the framebuffer
            out vec4 fragColor;

            void main() {
                // Fill the point
                fragColor = vec4(color);
            }
            """,
        )

        self.ctx.enable_only(self.ctx.BLEND)

    def gen_initial_data(self, count, x, y):
        for _ in range(count):
            x = x
            y = y
            angle = random.uniform(0, 2 * math.pi)
            # speed = random.uniform(.0, .3)
            speed = abs(random.gauss(0, 1)) * .5
            dx = math.sin(angle) * speed
            dy = math.cos(angle) * speed
            fade_rate = random.uniform(1 / MAX_FADE_TIME, 1 / MIN_FADE_TIME)
            red = random.uniform(0, 1.0)
            green = random.uniform(0, red)
            blue = 0
            yield x
            yield y
            yield dx
            yield dy
            yield fade_rate
            yield red
            yield green
            yield blue

    def on_draw(self):
        self.clear()
        self.ctx.point_size = 2 * self.get_pixel_ratio()

        for burst in self.burst_list:
            # Set uniforms in the program
            self.program['time'] = time.time() - burst.start_time
            self.program['gravity'] = GRAVITY

            # Render the result
            burst.vao.render(self.program, mode=self.ctx.POINTS)

    def on_update(self, dt):
        temp_list = self.burst_list.copy()
        for burst in temp_list:
            if time.time() - burst.start_time > MAX_FADE_TIME:
               self.burst_list.remove(burst)


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        burst = Burst()
        x2 = x / self.width * 2. - 1.
        y2 = y / self.height * 2. - 1.
        burst.buffer = self.ctx.buffer(data=array('f', self.gen_initial_data(PARTICLE_COUNT, x2, y2)))

        # We also need to be able to visualize both versions (draw to the screen)
        buffer_description = BufferDescription(burst.buffer,
                                               '2f 2f f 3f',
                                               ['in_pos', 'in_vel', 'in_fade', 'in_color'])
        burst.vao = self.ctx.geometry([buffer_description])

        burst.start_time = time.time()
        self.burst_list.append(burst)


if __name__ == "__main__":
    window = MyWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.center_window()
    arcade.run()
