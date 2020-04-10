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

        self.sprite_1 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
        self.sprite_1.center_x = 150
        self.sprite_1.center_y = 150
        self.character_list.append(self.sprite_1)

        self.sprite_2 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
        self.sprite_2.center_x = 250
        self.sprite_2.center_y = 250
        self.character_list.append(self.sprite_2)

        self.sprite_3 = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", CHARACTER_SCALING)
        self.sprite_3.center_x = 250
        self.sprite_3.center_y = 250
        self.character_list.append(self.sprite_3)

        self.frame = 0

    def on_draw(self):
        arcade.start_render()
        self.character_list.draw()

    def update(self, delta_time):
        self.frame += 1

        if self.frame == 3:
            self.sprite_2.remove_from_sprite_lists()

        if self.frame == 5:
            self.character_list.remove(self.sprite_3)

        if self.frame == 7:
            self.sprite_2.center_x += 5

        if self.frame == 9:
            self.sprite_3.center_x += 5


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
    window.test()
    window.close()
    arcade.cleanup_texture_cache()
