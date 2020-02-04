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

        self.texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")
        assert self.texture.width == 99
        assert self.texture.height == 75

        print(self.texture.image.width, self.texture.image.height)

    def on_draw(self):
        arcade.start_render()

        self.texture.draw_scaled(50, 50, 1)
        self.texture.draw_sized(150, 50, 99, 75)



def test_textures():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Textures")
    window.test()
    window.close()
    arcade.cleanup_texture_cache()