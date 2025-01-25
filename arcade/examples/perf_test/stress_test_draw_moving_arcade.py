"""
Moving Sprite Stress Test

Simple program to test how fast we can draw sprites that are moving

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.stress_test_draw_moving
"""
import random
import arcade
import timeit
import time
import collections
import pyglet

# --- Constants ---
SPRITE_SCALING_COIN = 0.25
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_COIN)
COIN_COUNT_INCREMENT = 1000

STOP_COUNT = 15000
RESULTS_FILE = "stress_test_draw_moving_arcade.csv"

WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1000
WINDOW_TITLE = "Moving Sprite Stress Test"


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)


class Coin(arcade.Sprite):

    def update(self, delta_times):
        """
        Update the sprite.
        """
        self.position = (self.position[0] + self.change_x, self.position[1] + self.change_y)


class GameView(arcade.View):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.coin_list = None

        self.processing_time = 0
        self.draw_time = 0
        self.program_start_time = timeit.default_timer()
        self.sprite_count_list = []
        self.fps_list = []
        self.processing_time_list = []
        self.drawing_time_list = []
        self.last_fps_reading = 0
        self.fps = FPSCounter()

        self.background_color = arcade.color.AMAZON

        # Open file to save timings
        self.results_file = open(RESULTS_FILE, "w")

    def add_coins(self):

        # Create the coins
        for i in range(COIN_COUNT_INCREMENT):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SPRITE_SIZE, WINDOW_WIDTH - SPRITE_SIZE)
            coin.center_y = random.randrange(SPRITE_SIZE, WINDOW_HEIGHT - SPRITE_SIZE)

            coin.change_x = random.randrange(-3, 4)
            coin.change_y = random.randrange(-3, 4)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList(use_spatial_hash=False)

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        self.clear()
        self.coin_list.draw()

        # Display info on sprites
        # output = f"Sprite count: {len(self.coin_list):,}"
        # arcade.draw_text(output, 20, WINDOW_HEIGHT - 20, arcade.color.BLACK, 16)
        #
        # # Display timings
        # output = f"Processing time: {self.processing_time:.3f}"
        # arcade.draw_text(output, 20, WINDOW_HEIGHT - 40, arcade.color.BLACK, 16)
        #
        # output = f"Drawing time: {self.draw_time:.3f}"
        # arcade.draw_text(output, 20, WINDOW_HEIGHT - 60, arcade.color.BLACK, 16)
        #
        # fps = self.fps.get_fps()
        # output = f"FPS: {fps:3.0f}"
        # arcade.draw_text(output, 20, WINDOW_HEIGHT - 80, arcade.color.BLACK, 16)

        self.draw_time = timeit.default_timer() - draw_start_time
        self.fps.tick()

    def on_update(self, delta_time):
        # Start update timer
        start_time = timeit.default_timer()

        self.coin_list.update()

        for sprite in self.coin_list:

            if sprite.position[0] < 0:
                sprite.change_x *= -1
            elif sprite.position[0] > WINDOW_WIDTH:
                sprite.change_x *= -1
            if sprite.position[1] < 0:
                sprite.change_y *= -1
            elif sprite.position[1] > WINDOW_HEIGHT:
                sprite.change_y *= -1

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time

        # Total time program has been running
        total_program_time = int(timeit.default_timer() - self.program_start_time)

        # Print out stats, or add more sprites
        if total_program_time > self.last_fps_reading:
            self.last_fps_reading = total_program_time

            # It takes the program a while to "warm up", so the first
            # few seconds our readings will be off. So wait some time
            # before taking readings
            if total_program_time > 5:

                # We want the program to run for a while before taking
                # timing measurements. We don't want the time it takes
                # to add new sprites to be part of that measurement. So
                # make sure we have a clear second of nothing but
                # running the sprites, and not adding the sprites.
                if total_program_time % 2 == 1:

                    # Take timings
                    output = (
                        f"{total_program_time}, "
                        f"{len(self.coin_list)}, "
                        f"{self.fps.get_fps():.1f}, "
                        f"{self.processing_time:.4f}, "
                        f"{self.draw_time:.4f}\n"
                    )

                    self.results_file.write(output)
                    print(output, end="")
                    if len(self.coin_list) >= STOP_COUNT:
                        pyglet.app.exit()
                        return

                    self.sprite_count_list.append(len(self.coin_list))
                    self.fps_list.append(round(self.fps.get_fps(), 1))
                    self.processing_time_list.append(self.processing_time)
                    self.drawing_time_list.append(self.draw_time)

                    # Now add the coins
                    self.add_coins()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
