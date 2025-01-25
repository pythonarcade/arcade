import arcade
from arcade.experimental import Shadertoy


# Derive an application window from Arcade's parent Window class
class MyGame(arcade.Window):

    def __init__(self, width=1920, height=1080, glow_color=arcade.color.LIGHT_BLUE):
        # Call the parent constructor
        super().__init__(width=width, height=height)

        # Load a file and create a shader from it
        shader_file_path = "circle_6.glsl"
        window_size = self.get_size()
        self.shadertoy = Shadertoy.create_from_file(window_size, shader_file_path)
        # Set uniform light color data to send to the GLSL shader
        # from the normalized RGB components of the color.
        self.shadertoy.program['color'] = glow_color.normalized[:3]

    def on_draw(self):
        # Set uniform position data to send to the GLSL shader
        self.shadertoy.program['pos'] = self.mouse["x"], self.mouse["y"]
        # Run the GLSL code
        self.shadertoy.render()

if __name__ == "__main__":
    MyGame()
    arcade.run()
