import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Resources"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.AMAZON)

        self.sprite = arcade.Sprite(arcade.resources.image_male_adventurer_idle, center_x=50, center_y=50)
        self.sprite.velocity = 1, 1

    def on_draw(self):
        arcade.start_render()
        self.sprite.draw()

    def update(self, delta_time):
        self.sprite.update()


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
