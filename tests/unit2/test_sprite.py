import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5

class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite("../../arcade/examples/images/character.png", CHARACTER_SCALING)
        sprite.center_x = SCREEN_WIDTH / 2
        sprite.center_y = SCREEN_HEIGHT / 2
        sprite.change_x = 1
        sprite.change_y = 1
        self.sprite_list.append(sprite)

    def on_draw(self):
        arcade.start_render()
        self.sprite_list.draw()

    def update(self, delta_time):
        self.sprite_list.update()


def test_text():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
    window.test()
    # arcade.run()
