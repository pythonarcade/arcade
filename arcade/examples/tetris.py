"""
Tetris

Tetris clone, with some ideas from silvasur's code:
https://gist.github.com/silvasur/565419/d9de6a84e7da000797ac681976442073045c74a4

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.tetris
"""
# flake8: noqa: E241
import arcade
import random
import PIL
import pyglet
import time

# Set how many rows and columns we will have
ROW_COUNT = 24
COLUMN_COUNT = 10

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 30
HEIGHT = 30

# This sets the margin between each cell and on the edges of the screen.
MARGIN = 2

WINDOW_TITLE = "Tetris"

colors = [
    # RGB
    (0,   0,   0, 255),
    (255, 0,   0, 255),
    (0,   150, 0, 255),
    (0,   0,   255, 255),
    (255, 120, 0, 255),
    (255, 255, 0, 255),
    (180, 0,   255, 255),
    (0,   220, 220, 255)
]

# Define the shapes of the single parts
tetris_shapes = [
    # From https://www.joe.co.uk/gaming/tetris-block-names-221127
    [[1, 1, 1],         # Teewee
     [0, 1, 0]],

    [[0, 2, 2],         # RhodeIslandZ
     [2, 2, 0]],

    [[3, 3, 0],         # ClevelandZ
     [0, 3, 3]],

    [[4, 0, 0],         # Blue Ricky
     [4, 4, 4]],

    [[0, 0, 5],         # Orange Ricky
     [5, 5, 5]],

    [[6, 6, 6, 6]],     # Hero

    [[7, 7],            # Smashboy
     [7, 7]]
]


def rotate_counter_clockwise(shape):
    """ Rotates a matrix counter clockwise """
    return [[
        shape[y][x] for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def rotate_clockwise(shape):
    """ Rotates a matrix clockwise """
    return [list(l[::-1]) for l in zip(*shape)]


def create_texture(color):
    """ Create a texture for sprites based on the global colors. """
    # noinspection PyUnresolvedReferences
    image = PIL.Image.new('RGBA', (WIDTH, HEIGHT), color)
    return arcade.Texture(str(color), image=image)


#
# List of images per color in colors
#
texture_list = [create_texture(color) for color in colors]


class Board:
    """
    This is Model and View in MVC
    """

    def __init__(self, rows, columns, height):
        """
        Create a grid of 0's.
        Add 1's to the bottom for easier collision detection.
        """
        self._rows = rows
        self._columns = columns
        self._height = height
        self._mw = MARGIN + WIDTH
        self._mh = MARGIN + HEIGHT
        # Create the main board of 0's
        self.board = [[0 for _x in range(columns)] for _y in range(rows)]
        # Add a bottom border of 1's
        self.board += [[1 for _x in range(columns)]]
        self.sprite_list = arcade.SpriteList()
        return

    def setup(self):
        # self.sprite_list = arcade.SpriteList()
        for row in range(self._rows):
            for column in range(self._columns):
                sprite = arcade.Sprite()
                for texture in texture_list:
                    sprite.append_texture(texture)
                sprite.set_texture(0)
                sprite.center_x = self._mw * column + self._mw // 2
                sprite.center_y = self._height - self._mh * row + self._mh // 2

                self.sprite_list.append(sprite)

        self.update()
        return

    def remove_row(self, row) -> None:
        """ Remove a row from the board, add a blank row on top. """
        del self.board[row]
        self.board = [[0 for _ in range(self._columns)]] + self.board
        return

    def check_collision(self, stone, stone_x, stone_y) -> bool:
        """
        See if the stone intersects with anything on the board.
        """
        if stone_x + len(stone[0]) > self._columns:
            # collision with the vertical wall
            return True
        for cy, row in enumerate(stone):
            for cx, cell in enumerate(row):
                if cell and self.board[cy + stone_y][cx + stone_x]:
                    return True
        return False

    def join_stone(self, stone, stone_x, stone_y) -> None:
        """
        Copy stone onto the board based on the passed in x, y offset coordinate
        """
        for cy, row in enumerate(stone):
            for cx, val in enumerate(row):
                self.board[cy + stone_y - 1][cx + stone_x] += val
        return

    def fold_it(self) -> None:
        while True:
            for i, row in enumerate(self.board[:-1]):
                if 0 not in row:
                    self.remove_row(i)
                    break
            else:
                break
        return

    def update(self):
        """
        Update the sprite list to reflect the contents of the 2D grid
        """
        for row in range(self._rows):
            for column in range(self._columns):
                v = self.board[row][column]
                i = row * self._columns + column
                self.sprite_list[i].set_texture(v)
        return


class MyGame(arcade.Window):
    """
    Main application class.
    This is Controller (and View?) in MVC
    """

    def __init__(self, cols, rows, title):
        """ Set up the application. """
        # Do the math to figure out our screen dimensions
        width = (WIDTH + MARGIN) * cols + MARGIN
        height = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN

        self._time_next_update = 0.0
        self._desired_update_rate_per_sec = 3
        self._desired_update_delay = 1/self._desired_update_rate_per_sec
        self.board = Board(rows, cols, height)
        self.game_over = False
        self.paused = False

        self.stone = None
        self.stone_x = 0
        self.stone_y = 0

        super().__init__(width, height, title)
        self.center_the_window()

        arcade.set_background_color(arcade.color.GRAY_BLUE)
        return

    def change_update_rate(self, incr: int) -> None:
        self._desired_update_rate_per_sec += incr
        if self._desired_update_rate_per_sec > 10:
            self._desired_update_rate_per_sec = 10
        elif self._desired_update_rate_per_sec < 1:
            self._desired_update_rate_per_sec = 1
        self._desired_update_delay = 1/self._desired_update_rate_per_sec
        return

    def center_the_window(self) -> None:
        """Centers the window on the screen."""
        SCREEN_NUM = 0
        screen = pyglet.canvas.Display().get_screens()[SCREEN_NUM]
        self.set_location(
            screen.width // 2 - self.width // 2,
            screen.height // 2 - self.height // 2)
        return

    def new_stone(self):
        """
        Randomly grab a new stone and set the stone location to the top.
        If we immediately collide, then game-over.
        """
        self.stone = random.choice(tetris_shapes)
        self.stone_x = int(self.board._columns / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if self.board.check_collision(self.stone, self.stone_x, self.stone_y):
            self.game_over = True
        return

    def setup(self):
        self.board.setup()
        self.new_stone()
        return

    def drop_stone(self) -> bool:
        """
        Drop the stone down one place.
        Check for collision.
        If collided, then
          join matrixes
          Check for rows we can remove
          Update sprite list with stones
          Create a new stone
        Returns True if case of NO collision
        """
        if self.game_over or self.paused:
            return False

        self.stone_y += 1
        if not self.board.check_collision(
                self.stone, self.stone_x, self.stone_y):
            return True

        self.board.join_stone(self.stone, self.stone_x, self.stone_y)
        self.board.fold_it()
        self.board.update()
        self.new_stone()
        return False

    def drop_stone_hard(self) -> None:
        while self.drop_stone():
            pass
        return

    def rotate_stone_cw(self):
        """ Rotate the stone clockwise, check collision. """
        if not self.game_over:      # and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not self.board.check_collision(
                    new_stone, self.stone_x, self.stone_y):
                self.stone = new_stone
        return

    def rotate_stone_ccw(self):
        """ Rotate the stone counter-clockwise, check collision. """
        if not self.game_over:      # and not self.paused:
            new_stone = rotate_counter_clockwise(self.stone)
            if not self.board.check_collision(
                    new_stone, self.stone_x, self.stone_y):
                self.stone = new_stone
        return

    def on_update(self, dt):
        """ Update, drop stone if warranted """
        now = time.time()
        if now >= self._time_next_update:
            self._time_next_update = now + self._desired_update_delay
            self.drop_stone()
        # super().on_update(dt)
        return

    def move_stone(self, delta_x):
        """ Move the stone back and forth based on delta x. """
        if not self.game_over:  # and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            elif new_x > self.board._columns - len(self.stone[0]):
                new_x = self.board._columns - len(self.stone[0])
            if not self.board.check_collision(self.stone, new_x, self.stone_y):
                self.stone_x = new_x
        return

    def on_key_press(self, key, modifiers):
        """
        Handle user key presses
        as in https://strategywiki.org/wiki/Tetris/Controls#General_controls
        User goes left, move -1
        User goes right, move 1
        Rotate stone,
        or drop down
        """
        if key in (arcade.key.LEFT, arcade.key.NUM_LEFT):
            self.move_stone(-1)
        elif key in (arcade.key.RIGHT, arcade.key.NUM_RIGHT):
            self.move_stone(1)
        elif key in (arcade.key.UP, arcade.key.X, arcade.key.NUM_UP):
            self.rotate_stone_cw()
        elif key in (arcade.key.LCTRL, arcade.key.RCTRL, arcade.key.Z):
            self.rotate_stone_ccw()
        elif key in (arcade.key.DOWN, arcade.key.NUM_DOWN):
            self.drop_stone()
        elif key == arcade.key.SPACE:
            self.drop_stone_hard()
        elif key == arcade.key.P:
            self.paused = not self.paused
        elif key in (arcade.key.PLUS, arcade.key.NUM_ADD):
            self.change_update_rate(1)
        elif key in (arcade.key.MINUS, arcade.key.NUM_SUBTRACT):
            self.change_update_rate(-1)
        return

    # noinspection PyMethodMayBeStatic
    def draw_stone(self):
        """
        Draw the stone. Used to draw the falling stones. The board is drawn
        by the sprite list.
        """
        # Draw the grid
        MW = MARGIN + WIDTH
        MH = MARGIN + HEIGHT
        for row in range(len(self.stone)):
            for column in range(len(self.stone[0])):
                # Figure out what color to draw the box
                if self.stone[row][column]:
                    # Do the math to figure out where the box is
                    x = MW * (column + self.stone_x) + MW // 2
                    y = self.height - MH * (row + self.stone_y) + MH // 2
                    # Draw the box
                    arcade.draw_rectangle_filled(
                        x, y, WIDTH, HEIGHT, colors[self.stone[row][column]])
        return

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        self.clear()
        self.board.sprite_list.draw()
        self.draw_stone()
        return


def main():
    """ Create the game window, setup, run """
    my_game = MyGame(COLUMN_COUNT, ROW_COUNT, WINDOW_TITLE)
    my_game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
