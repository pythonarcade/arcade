"""
Performance Statistic Display Example

This example demonstrates how to use a few performance profiling tools
built into Arcade:

* arcade.enable_timings
* arcade.PerfGraph
* arcade.get_fps
* arcade.print_timings
* arcade.clear_timings

A large number of sprites bounce around the screen to produce load. You
can adjust the number of sprites by changing the COIN_COUNT constant.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.performance_statistics
"""
import random

import arcade

# --- Constants ---
SPRITE_SCALING_COIN = 0.25
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_COIN)

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Performance Statistics Display Example"

# Size of performance graphs and distance between them
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

COIN_COUNT = 1500

# Turn on tracking for the number of event handler
# calls and the average execution time of each type.
arcade.enable_timings()


class Coin(arcade.BasicSprite):
    """ Our coin sprite class """
    def __init__(self, texture: arcade.Texture, scale: float):
        super().__init__(texture, scale=scale)
        # Add a velocity to the coin
        self.change_x = 0
        self.change_y = 0

    def update(self, delta_time: float = 1/60):
        """ Update the sprite. """
        # Setting the position is faster than setting x & y individually
        self.position = (
            self.position[0] + self.change_x,
            self.position[1] + self.change_y
        )

        # Bounce the coin on the edge of the window
        if self.position[0] < 0:
            self.change_x *= -1
        elif self.position[0] > WINDOW_WIDTH:
            self.change_x *= -1
        if self.position[1] < 0:
            self.change_y *= -1
        elif self.position[1] > WINDOW_HEIGHT:
            self.change_y *= -1


class GameView(arcade.View):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables to hold game objects and performance info
        self.coin_list: arcade.SpriteList | None = None
        self.perf_graph_list: arcade.SpriteList | None = None
        self.fps_text: arcade.Text | None = None
        self.frame_count: int = 0  # for tracking the reset interval

        self.coin_texture = arcade.load_texture(":resources:images/items/coinGold.png")
        self.background_color = arcade.color.AMAZON

    def add_coins(self, amount):

        # Create the coins
        for i in range(amount):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin(self.coin_texture, scale=SPRITE_SCALING_COIN)

            # Position the coin
            coin.position = (
                random.randrange(SPRITE_SIZE, WINDOW_WIDTH - SPRITE_SIZE),
                random.randrange(SPRITE_SIZE, WINDOW_HEIGHT - SPRITE_SIZE)
            )

            coin.change_x = random.randrange(-3, 4)
            coin.change_y = random.randrange(-3, 4)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList(use_spatial_hash=False)

        # Create some coins
        self.add_coins(COIN_COUNT)

        # Create a sprite list to put the performance graphs into
        self.perf_graph_list = arcade.SpriteList()

        # Calculate position helpers for the row of 3 performance graphs
        row_y = self.height - GRAPH_HEIGHT / 2
        starting_x = GRAPH_WIDTH / 2
        step_x = GRAPH_WIDTH + GRAPH_MARGIN

        # Create the FPS performance graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.position = starting_x, row_y
        self.perf_graph_list.append(graph)

        # Create the on_update graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="on_update")
        graph.position = starting_x + step_x, row_y
        self.perf_graph_list.append(graph)

        # Create the on_draw graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="on_draw")
        graph.position = starting_x + step_x * 2, row_y
        self.perf_graph_list.append(graph)

        # Create a Text object to show the current FPS
        self.fps_text = arcade.Text(
            f"FPS: {arcade.get_fps(60):5.1f}",
            10, 10, arcade.color.BLACK, 22
        )

    def on_draw(self):
        """ Draw everything """

        # Clear the screen
        self.clear()

        # Draw all the coin sprites
        self.coin_list.draw()

        # Draw the graphs
        self.perf_graph_list.draw()

        # Get & draw the FPS for the last 60 frames
        if arcade.timings_enabled():
            self.fps_text.value = f"FPS: {arcade.get_fps(60):5.1f}"
            self.fps_text.draw()

    def on_update(self, delta_time):
        """ Update method """
        self.frame_count += 1

        # Print and clear timings every 60 frames
        if self.frame_count % 60 == 0:
            arcade.print_timings()
            arcade.clear_timings()

        # Move the coins
        self.coin_list.update()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            if arcade.timings_enabled():
                arcade.disable_timings()
            else:
                arcade.enable_timings()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()
