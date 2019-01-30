"""
Pyglet Sprite Stress Test

Simple program to test how fast we can draw sprites that aren't moving

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.performance_comparison.simple_sprite_draw_arcade
"""

import pyglet
import timeit

# --- Constants ---

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Pyglet Sprite Stress Test"


class MyGame(pyglet.window.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """

        # Call the parent class initializer
        super().__init__(height=SCREEN_HEIGHT, width=SCREEN_WIDTH, caption=SCREEN_TITLE)

        self.draw_time = 0

        ball_image = pyglet.image.load('../images/coin_01.png')

        # Sprite list
        self.batch = pyglet.graphics.Batch()
        self.all_sprites_list = []

        # Create the coins
        for x in range(0, SCREEN_WIDTH, 100):
            for y in range(0, SCREEN_HEIGHT, 100):

                # Create the coin instance
                # Coin image from kenney.nl
                coin = pyglet.sprite.Sprite(ball_image, x, y, batch=self.batch)

                # Add the coin to the list of sprites
                self.all_sprites_list.append(coin)

        pyglet.clock.schedule_interval(self.on_update, 1/60)

    def on_update(self, dtime):
        pass

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Clear the screen
        self.clear()

        # Draw all the sprites
        self.batch.draw()

        # Calculate time to draw
        self.draw_time = timeit.default_timer() - draw_start_time

        # Display timings
        sprite_count = len(self.all_sprites_list)
        output = f"Drawing time: {self.draw_time:.4f} for {sprite_count} sprites."
        label = pyglet.text.Label(output, x=20, y=SCREEN_HEIGHT - 20, color=(255,0,0,255), font_size=12, width=2000, align="left", font_name=('Calibri', 'Arial'), anchor_x="left", anchor_y="baseline")
        label.draw()


def main():
    """ Main method """
    window = MyGame()
    pyglet.app.run()


if __name__ == "__main__":
    main()
