from pathlib import Path
import arcade
from arcade.experimental.shadertoy import Shadertoy


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.shadertoy = Shadertoy.create_from_file(
            self.get_framebuffer_size(),
            Path(__file__).parent / "star_nest.glsl"
        )

    def on_draw(self):
        self.clear()
        self.shadertoy.render()

    def on_update(self, dt):
        # Update the internal time in shadertoy
        self.shadertoy.time += dt

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.shadertoy.mouse_position = x, y

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.shadertoy.resize((width, height))


if __name__ == "__main__":
    MyGame(800, 600, "Shadertoy Demo")
    arcade.run()
