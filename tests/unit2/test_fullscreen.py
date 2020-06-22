import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5


class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        pass

    def update(self, delta_time):
        pass


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
    window.center_window()
    window.set_fullscreen(True, width=1920, height=1080)
    window.test(10)
    window.set_fullscreen(False)
    window.test(10)
    window.close()
