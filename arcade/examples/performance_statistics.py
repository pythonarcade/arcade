"""
Performance Statistic Displays

Artwork from https://kenney.nl
"""

import random
import arcade

# --- Constants ---
SPRITE_SCALING_COIN = 0.25
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_COIN)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade - Moving Sprite Stress Test"

# Size of performance graphs and distance between them
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

COIN_COUNT = 1500

arcade.enable_timings()


class Coin(arcade.Sprite):
    """ Our coin sprite class """
    def update(self):
        """ Update the sprite. """
        # Updating the sprite this way is faster than x and y individually.
        self.position = (self.position[0] + self.change_x, self.position[1] + self.change_y)

        # Bounce the coin on the edge
        if self.position[0] < 0:
            self.change_x *= -1
        elif self.position[0] > SCREEN_WIDTH:
            self.change_x *= -1
        if self.position[1] < 0:
            self.change_y *= -1
        elif self.position[1] > SCREEN_HEIGHT:
            self.change_y *= -1


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.coin_list = None
        self.perf_graph_list = None

        self.frame_count = 0

        arcade.set_background_color(arcade.color.AMAZON)

    def add_coins(self, amount):

        # Create the coins
        for i in range(amount):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
            coin.center_y = random.randrange(SPRITE_SIZE, SCREEN_HEIGHT - SPRITE_SIZE)

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

        # Create a sprite list to put the performance graph into
        self.perf_graph_list = arcade.SpriteList()

        # Create the FPS performance graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.center_x = GRAPH_WIDTH / 2
        graph.center_y = self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

        # Create the on_update graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="update")
        graph.center_x = GRAPH_WIDTH / 2 + (GRAPH_WIDTH + GRAPH_MARGIN)
        graph.center_y = self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

        # Create the on_draw graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="on_draw")
        graph.center_x = GRAPH_WIDTH / 2 + (GRAPH_WIDTH + GRAPH_MARGIN) * 2
        graph.center_y = self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

    def on_draw(self):
        """ Draw everything """

        # Clear the screen
        self.clear()

        # Draw all the sprites
        self.coin_list.draw()

        # Draw the graphs
        self.perf_graph_list.draw()

        # Get FPS for the last 60 frames
        text = f"FPS: {arcade.get_fps(60):5.1f}"
        arcade.draw_text(text, 10, 10, arcade.color.BLACK, 22)

    def update(self, delta_time):
        """ Update method """
        self.frame_count += 1

        # Print and clear timings every 60 frames
        if self.frame_count % 60 == 0:
            arcade.print_timings()
            arcade.clear_timings()

        # Move the coins
        self.coin_list.update()


def main():
    """ Main function """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
