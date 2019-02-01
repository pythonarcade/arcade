import arcade

class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        super().__init__(800, 600, "t_2")

        self.coin_list = arcade.SpriteList()

        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        arcade.start_render()


MyGame()
arcade.run()
