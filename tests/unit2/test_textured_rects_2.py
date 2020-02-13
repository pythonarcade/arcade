import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Resources"


class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.texture = arcade.load_texture(":resources:images/items/coinGold.png")


    def on_draw(self):
        try:
            arcade.start_render()

            x = 50
            y = 50
            scale = 1.0

            assert arcade.get_pixel(50, 50) == (59, 122, 87)
            arcade.draw_scaled_texture_rectangle(x, y, self.texture, scale)
            assert arcade.get_pixel(50, 50) == (255, 204, 0)


        except Exception as e:
            assert e is None


def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.test(50)
    window.close()
