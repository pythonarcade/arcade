"""
Starting Template Simple

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template_simple
"""
import arcade
import arcade.gui

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template Simple"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.ALMOND)
        arcade.gui.UITextureBox

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        atlas: arcade.TextureAtlas = arcade.TextureAtlas(size=(200, 200))
        my_texture = arcade.Texture("fred")
        with atlas.render_texture(my_texture):
            arcade.draw_line(0, 0, 100, 100, arcade.color.RED, 3)

        image = atlas.to_image()
        texture = arcade.Texture(image=image)
        self.sprite = arcade.Sprite(texture)
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sprite)


    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.sprite_list.draw()


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
