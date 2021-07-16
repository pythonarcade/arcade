"""
Example showing how to create particle explosions via the GPU.
"""
import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "GPU Particle Explosion"


class MyWindow(arcade.Window):
    """ Main window"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    def on_draw(self):
        """ Draw everything """
        self.clear()

    def on_update(self, dt):
        """ Update everything """
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ User clicks mouse """
        pass


if __name__ == "__main__":
    window = MyWindow()
    window.center_window()
    arcade.run()
