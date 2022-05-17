import arcade
from arcade.experimental import Shadertoy


# Derive an application window from Arcade's parent Window class
class MyGame(arcade.Window):

    def __init__(self):
        # Call the parent constructor
        super().__init__(width=1920, height=1080)

        # Used to track run-time
        self.time = 0.0

        # Load a file and create a shader from it
        file_name = "explosion.glsl"
        self.shadertoy = Shadertoy(size=self.get_size(),
                                   main_source=open(file_name).read())

    def on_draw(self):
        self.clear()
        # Set uniform data to send to the GLSL shader
        self.shadertoy.program['pos'] = self.mouse["x"], self.mouse["y"]

        # Run the GLSL code
        self.shadertoy.render(time=self.time)

    def on_update(self, delta_time: float):
        # Track run time
        self.time += delta_time


if __name__ == "__main__":
    window = MyGame()
    window.center_window()
    arcade.run()
