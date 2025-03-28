"""
Depth-sort sprites using a depth buffer in the GL context.

Press the space bar to toggle depth testing during drawing.

During each update, the depth of each sprite is updated to follow a
cosine wave. Afterward, the following is drawn:

* All sprites in depth-sorted order
* A white square centered over each sprite along the x-axis, and moving
  with the wave along the y-axis

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_depth_cosine
"""

import math

from pyglet.graphics import Batch

import arcade

# All constants are in pixels
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

WINDOW_TITLE = "Sprite Depth Testing Example w/ a Cosine Wave"
NUM_SPRITES = 10

SPRITE_X_START = 150
SPRITE_X_STEP = 50
SPRITE_Y = WINDOW_HEIGHT // 2

DOT_SIZE = 10


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        texture = arcade.load_texture(":resources:images/test_textures/xy_square.png")
        self.text_batch = Batch()

        self.use_depth: bool = True
        self.text_use_depth = arcade.Text(
            "SPACE: Toggle depth testing (True)",
            x=10,
            y=30,
            font_size=15,
            color=arcade.color.WHITE,
            batch=self.text_batch,
        )

        self.sprite_list = arcade.SpriteList()

        for i in range(NUM_SPRITES):
            sprite = arcade.Sprite(
                texture, center_x=SPRITE_X_START + SPRITE_X_STEP * i, center_y=SPRITE_Y
            )
            self.sprite_list.append(sprite)

    def on_draw(self):
        self.clear()

        ctx = self.window.ctx
        if self.use_depth:
            # This with block temporarily enables depth testing
            with ctx.enabled(ctx.DEPTH_TEST):
                self.sprite_list.draw()
        else:
            self.sprite_list.draw()

        # Draw wave visualization markers over each sprite
        for i, sprite in enumerate(self.sprite_list):
            arcade.draw_point(
                SPRITE_X_START + SPRITE_X_STEP * i,
                SPRITE_Y + sprite.depth,
                arcade.color.WHITE,
                DOT_SIZE,
            )

        self.text_batch.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.use_depth = not self.use_depth
            self.text_use_depth.text = f"SPACE: Toggle depth testing ({self.use_depth})"

    def on_update(self, delta_time):
        # Using time from the window's clock simplifies the math below
        time = self.window.time
        for i, sprite in enumerate(self.sprite_list):
            sprite.depth = math.cos(time + i) * SPRITE_X_STEP


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
