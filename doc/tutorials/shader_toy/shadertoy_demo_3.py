import arcade
from arcade.experimental import Shadertoy

# Derive an application window from Arcade's parent Window class
class MyGame(arcade.Window):

    def __init__(self):
        # Call the parent constructor
        super().__init__(width=1920, height=1080)

        # Read a GLSL program into a string
        file = open("circle_6.glsl")
        shader_sourcecode = file.read()
        # Create a shader from it
        self.shadertoy = Shadertoy(size=self.get_size(),
                                   main_source=shader_sourcecode)

    def on_draw(self):
        # Set uniform data to send to the GLSL shader
        self.shadertoy.program['pos'] = self.mouse["x"], self.mouse["y"]
        self.shadertoy.program['color'] = arcade.get_three_float_color(arcade.color.LIGHT_BLUE)
        # Run the GLSL code
        self.shadertoy.render()

if __name__ == "__main__":
    MyGame()
    arcade.run()
