"""
Minimal Sprite Example

Draws a single sprite in the middle screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_minimal
"""
import arcade


class WhiteSpriteCircleExample(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "White SpriteCircle Example")
        self.sprites = None
        self.setup()

    def setup(self):
        # 1. Create the SpriteList
        self.sprites = arcade.SpriteList()

        # 2. Create & append your Sprite instance to the SpriteList
        self.circle = arcade.SpriteCircle(30, arcade.color.WHITE)  # 30 pixel radius circle
        self.circle.position = self.width // 2, self.height // 2  # Put it in the middle
        self.sprites.append(self.circle)  # Append the instance to the SpriteList

    def on_draw(self):
        # 3. Call draw() on the SpriteList inside an on_draw() method
        self.sprites.draw()


if __name__ == "__main__":
    game = WhiteSpriteCircleExample()
    game.run()
