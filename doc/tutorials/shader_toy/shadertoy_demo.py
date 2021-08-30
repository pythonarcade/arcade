import arcade
from arcade.experimental import Shadertoy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.time = 0
        # file_name = "fractal_pyramid.glsl"
        # file_name = "cyber_fuji_2020.glsl"
        # file_name = "flame.glsl"
        file_name = "star_nest.glsl"
        file = open(file_name)
        shader_sourcecode = file.read()
        size = width, height
        self.shadertoy = Shadertoy(size, shader_sourcecode)
        self.mouse_pos = 0, 0

    def on_draw(self):
        arcade.start_render()
        self.shadertoy.render(time=self.time, mouse_position=self.mouse_pos)

    def on_update(self, dt):
        # Keep track of elapsed time
        self.time += dt

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_pos = x, y


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
