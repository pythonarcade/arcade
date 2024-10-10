"""
Minimal Sprite Example

Draws a single sprite in the middle screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_minimal
"""
import arcade


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        # 1. Create the SpriteList
        self.sprites = arcade.SpriteList()

        # 2. Create & append your Sprite instance to the SpriteList
        self.circle = arcade.Sprite()  # Sprite with the default texture
        self.circle.position = self.center  # center sprite on screen
        self.sprites.append(self.circle)  # Append the instance to the SpriteList

    def on_draw(self):
        # 3. Clear the screen
        self.clear()

        # 4. Call draw() on the SpriteList inside an on_draw() method
        self.sprites.draw()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(1280, 720, "Minimal SPrite Example")

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
