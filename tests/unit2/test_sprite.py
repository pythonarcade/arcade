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
        self.character_sprite = arcade.Sprite("../../arcade/examples/images/character.png", CHARACTER_SCALING)
        self.character_sprite.center_x = 50
        self.character_sprite.center_y = 50
        self.character_sprite.change_x = 5
        self.character_sprite.change_y = 5
        self.character_list.append(self.character_sprite)

        self.coin_list = arcade.SpriteList()
        sprite = arcade.Sprite("../../arcade/examples/images/coin_01.png", CHARACTER_SCALING)
        sprite.position = (130, 130)
        sprite.angle = 90
        self.coin_list.append(sprite)

    def on_draw(self):
        arcade.start_render()
        self.coin_list.draw()
        self.character_list.draw()

    def update(self, delta_time):
        self.coin_list.update()
        self.character_list.update()

        coin_hit_list = arcade.check_for_collision_with_list(self.character_sprite, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()


# def test_sprite():
#     window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Text")
#     window.test()
