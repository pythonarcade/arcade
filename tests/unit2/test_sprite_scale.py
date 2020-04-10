import os
import arcade

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

        self.character_list = arcade.SpriteList()
        self.character_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
        self.character_sprite.center_x = 150
        self.character_sprite.center_y = 150
        self.character_list.append(self.character_sprite)

    def on_draw(self):
        arcade.start_render()
        self.character_list.draw()

    def update(self, delta_time):
        self.character_sprite.scale += 0.1


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
    window.test()
    window.close()
    arcade.cleanup_texture_cache()
