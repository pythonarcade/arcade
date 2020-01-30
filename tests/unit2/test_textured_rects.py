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

        self.texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")

    def on_draw(self):
        arcade.start_render()

        scale = .6
        arcade.draw_texture_rectangle(540, 120,
                                      self.texture.image.width * scale,
                                      self.texture.image.height * scale,
                                      self.texture, angle=45)

        arcade.draw_xywh_rectangle_textured(10, 400, 64, 64, self.texture)

        for i in range(15):
            arcade.draw_scaled_texture_rectangle(i * 50 + 20, 220,
                                                 scale,
                                                 self.texture, angle=45, alpha=i * 15)


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Textures")
    window.test()
    window.close()
