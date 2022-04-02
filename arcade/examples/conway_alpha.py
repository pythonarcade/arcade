"""
Conway's Game of Life

This code shows how to set up sprites in a grid, and then use their
'alpha' value to quickly turn them on and off.

After installing the "arcade" package version 2.4.4+, this program can be run by
typing:
python -m arcade.examples.conway_alpha
"""
import arcade
import random

# Set how many rows and columns we will have
ROW_COUNT = 70
COLUMN_COUNT = 128

# This sets the WIDTH and HEIGHT of each grid location
CELL_WIDTH = 15
CELL_HEIGHT = 15

# This sets the margin between each cell
# and on the edges of the screen.
CELL_MARGIN = 0

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = (CELL_WIDTH + CELL_MARGIN) * COLUMN_COUNT + CELL_MARGIN
SCREEN_HEIGHT = (CELL_HEIGHT + CELL_MARGIN) * ROW_COUNT + CELL_MARGIN
SCREEN_TITLE = "Conway's Game of Life"

# Colors and alpha values
ALIVE_COLOR = arcade.color.BISTRE
BACKGROUND_COLOR = arcade.color.ANTIQUE_WHITE
ALPHA_ON = 255
ALPHA_OFF = 0


def create_grids():
    """
    Create a 2D and 1D grid of sprites. We use the 1D SpriteList for drawing,
    and the 2D list for accessing via grid. Both lists point to the same set of
    sprites.
    """
    # One dimensional list of all sprites in the two-dimensional sprite list
    grid_sprites_one_dim = arcade.SpriteList()

    # This will be a two-dimensional grid of sprites to mirror the two
    # dimensional grid of numbers. This points to the SAME sprites that are
    # in grid_sprite_list, just in a 2d manner.
    grid_sprites_two_dim = []

    # Create a list of sprites to represent each grid location
    for row in range(ROW_COUNT):
        grid_sprites_two_dim.append([])

        for column in range(COLUMN_COUNT):

            # Make the sprite as a soft circle
            sprite = arcade.SpriteCircle(CELL_WIDTH // 2, ALIVE_COLOR, soft=True)

            # Position the sprite
            x = column * (CELL_WIDTH + CELL_MARGIN) + (CELL_WIDTH / 2 + CELL_MARGIN)
            y = row * (CELL_HEIGHT + CELL_MARGIN) + (CELL_HEIGHT / 2 + CELL_MARGIN)
            sprite.center_x = x
            sprite.center_y = y

            # Add the sprite to both lists
            grid_sprites_one_dim.append(sprite)
            grid_sprites_two_dim[row].append(sprite)

    return grid_sprites_one_dim, grid_sprites_two_dim


def randomize_grid(grid: arcade.SpriteList):
    """ Randomize the grid to alive/dead """
    for cell in grid:
        pick = random.randrange(2)
        if pick:
            cell.alpha = ALPHA_ON
        else:
            cell.alpha = ALPHA_OFF


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width: int, height: int, title: str):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        self.background_color = BACKGROUND_COLOR

        # We need two layers. One holds the current state of our grid, the other
        # holds the next frame's state. We flip back and forth between the two.
        grid_sprites_one_dim1, grid_sprites_two_dim1 = create_grids()
        grid_sprites_one_dim2, grid_sprites_two_dim2 = create_grids()

        self.layers_grid_sprites_one_dim = [grid_sprites_one_dim1, grid_sprites_one_dim2]
        self.layers_grid_sprites_two_dim = [grid_sprites_two_dim1, grid_sprites_two_dim2]

        self.cur_layer = 0
        randomize_grid(self.layers_grid_sprites_one_dim[0])

    def on_draw(self):
        """ Render the screen. """
        # Clear all pixels in the window
        self.clear()
        self.layers_grid_sprites_one_dim[0].draw()

    def on_update(self, delta_time: float):
        """ Update the grid """

        # Flip layers
        if self.cur_layer == 0:
            layer1 = self.layers_grid_sprites_two_dim[0]
            layer2 = self.layers_grid_sprites_two_dim[1]
            self.cur_layer = 1
        else:
            layer1 = self.layers_grid_sprites_two_dim[1]
            layer2 = self.layers_grid_sprites_two_dim[0]
            self.cur_layer = 0

        # Count the neighbors that are alive
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                live_neighbors = 0
                # -1 -1
                if row > 0 and column > 0 \
                        and layer1[row - 1][column - 1].alpha == ALPHA_ON:
                    live_neighbors += 1
                # -1  0
                if row > 0 and layer1[row - 1][column].alpha == ALPHA_ON:
                    live_neighbors += 1
                # -1 +1
                if row > 0 and column < COLUMN_COUNT - 1\
                        and layer1[row - 1][column + 1].alpha == ALPHA_ON:
                    live_neighbors += 1
                #  0 +1
                if column < COLUMN_COUNT - 1 \
                        and layer1[row][column + 1].alpha == ALPHA_ON:
                    live_neighbors += 1
                # +1 +1
                if row < ROW_COUNT - 1 \
                        and column < COLUMN_COUNT - 1 \
                        and layer1[row + 1][column + 1].alpha == ALPHA_ON:
                    live_neighbors += 1
                # +1  0
                if row < ROW_COUNT - 1 and layer1[row + 1][column].alpha == ALPHA_ON:
                    live_neighbors += 1
                # +1 -1
                if row < ROW_COUNT - 1 and column > 0 \
                        and layer1[row + 1][column - 1].alpha == ALPHA_ON:
                    live_neighbors += 1
                #  0 -1
                if column > 0 and layer1[row][column - 1].alpha == ALPHA_ON:
                    live_neighbors += 1

                """
                Implement Conway's game of life rules

                Any live cell with two or three live neighbours survives.
                Any dead cell with three live neighbours becomes a live cell.
                All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                """
                if layer1[row][column].alpha == ALPHA_ON and (live_neighbors == 2 or live_neighbors == 3):
                    if layer2[row][column].alpha == ALPHA_OFF:
                        layer2[row][column].alpha = ALPHA_ON
                elif layer1[row][column].alpha == ALPHA_OFF and live_neighbors == 3:
                    if layer2[row][column].alpha == ALPHA_OFF:
                        layer2[row][column].alpha = ALPHA_ON
                else:
                    if layer2[row][column].alpha == ALPHA_ON:
                        layer2[row][column].alpha = ALPHA_OFF


def main():
    """ Main function - starting point to the program """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.center_window()
    arcade.run()


if __name__ == "__main__":
    main()
