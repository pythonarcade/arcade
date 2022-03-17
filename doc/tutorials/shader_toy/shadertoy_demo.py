import arcade
from arcade.experimental import Shadertoy


class MyGame(arcade.Window):

    def __init__(self):
        # Call the parent constructor
        super().__init__(width=1920, height=1080, title="Shader Demo", resizable=True)

        # Keep track of total run-time
        self.time = 0.0

        # Read in a GLSL program and create a shadertoy out of it
        # file_name = "fractal_pyramid.glsl"
        # file_name = "cyber_fuji_2020.glsl"
        file_name = "earth_planet_sky.glsl"
        # file_name = "flame.glsl"
        # file_name = "star_nest.glsl"
        file = open(file_name)
        shader_sourcecode = file.read()
        self.shadertoy = Shadertoy(size=self.get_size(), main_source=shader_sourcecode)

    def on_draw(self):
        self.clear()
        mouse_pos = self.mouse["x"], self.mouse["y"]
        self.shadertoy.render(time=self.time, mouse_position=mouse_pos)

    def on_update(self, dt):
        # Keep track of elapsed time
        self.time += dt


if __name__ == "__main__":
    MyGame()
    arcade.run()
