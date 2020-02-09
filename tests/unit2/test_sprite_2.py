import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Resources"
CHARACTER_SCALING = 1.0


class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.sprite = arcade.Sprite(":resources:images/items/coinGold.png", CHARACTER_SCALING)
        self.sprite.center_x = 50
        self.sprite.center_y = 50

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sprite)


    def on_draw(self):
        try:
            arcade.start_render()

            assert arcade.get_pixel(50, 50) == (59, 122, 87)
            self.sprite.draw()
            assert arcade.get_pixel(50, 50) == (255, 204, 0)

        except Exception as e:
            assert e is None



def test_sprite():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.test(50)
    window.close()
