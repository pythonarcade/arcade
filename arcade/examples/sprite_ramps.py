"""
Load a map stored in csv format, as exported by the program 'Tiled.'

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_ramps
"""
import arcade
import os

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite with Ramps Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40
RIGHT_MARGIN = 150

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 14
GRAVITY = 0.5


def get_map():
    map_file = open("map_with_ramps_2.csv")
    map_array = []
    for line in map_file:
        line = line.strip()
        map_row = line.split(",")
        for index, item in enumerate(map_row):
            map_row[index] = int(item)
        map_array.append(map_row)
    return map_array


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """

        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.all_sprites_list = None
        self.coin_list = None
        self.player_list = None

        # Set up the player
        self.player_sprite = None
        self.wall_list = None
        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.game_over = False

    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite("images/character.png",
                                           SPRITE_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)
        self.all_sprites_list.append(self.player_sprite)

        map_array = get_map()

        # Right edge of the map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        map_items = ["images/boxCrate_double.png",
                     "images/grassCenter.png",
                     "images/grassCorner_left.png",
                     "images/grassCorner_right.png",
                     "images/grassHill_left.png",
                     "images/grassHill_right.png",
                     "images/grassLeft.png",
                     "images/grassMid.png",
                     "images/grassRight.png",
                     "images/stoneHalf.png"
                     ]
        for row_index, row in enumerate(map_array):
            for column_index, item in enumerate(row):

                if item == -1:
                    continue
                else:
                    wall = arcade.Sprite(map_items[item],
                                         SPRITE_SCALING)

                    # Change the collision polygon to be a ramp instead of
                    # a rectangle
                    if item == 4:
                        wall.points = ((-wall.width // 2, wall.height // 2),
                                       (wall.width // 2, -wall.height // 2),
                                       (-wall.width // 2, -wall.height // 2))
                    elif item == 5:
                        wall.points = ((-wall.width // 2, -wall.height // 2),
                                       (wall.width // 2, -wall.height // 2),
                                       (wall.width // 2, wall.height // 2))

                wall.right = column_index * 64
                wall.top = (7 - row_index) * 64
                self.all_sprites_list.append(wall)
                self.wall_list.append(wall)

        self.physics_engine = \
            arcade.PhysicsEnginePlatformer(self.player_sprite,
                                           self.wall_list,
                                           gravity_constant=GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        # Adjust the text position based on the viewport so that we don't
        # scroll the text too.
        distance = self.player_sprite.right
        output = "Distance: {}".format(distance)
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20,
                         arcade.color.WHITE, 14)

        if self.game_over:
            output = "Game Over"
            arcade.draw_text(output, self.view_left + 200,
                             self.view_bottom + 200,
                             arcade.color.WHITE, 30)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed down.
        """
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= int(left_bndry - self.player_sprite.left)
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += int(self.player_sprite.right - right_bndry)
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += int(self.player_sprite.top - top_bndry)
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= int(bottom_bndry - self.player_sprite.bottom)
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()
