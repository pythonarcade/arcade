"""
Load a map stored in csv format, as exported by the program 'Tiled.'

Artwork from http://kenney.nl
"""
import random
import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40
RIGHT_MARGIN = 150

# Right edge of the map in pixels
END_OF_MAP = 5565

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 14
GRAVITY = 0.5

window = None


class PhysicsEngine():
    """
    This class will move everything, and take care of collisions.
    """
    def __init__(self, player_sprite, walls):
        """
        Constructor.
        """
        self.player_sprite = player_sprite
        self.walls = walls

    def can_jump(self):

        # --- Move in the y direction
        self.player_sprite.center_y -= 2

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.walls)

        result = False

        if len(hit_list) > 0:
            result = True

        self.player_sprite.center_y += 2
        return result

    def update(self):
        """
        Move everything and resolve collisions.
        """

        # Add gravity
        self.player_sprite.change_y -= GRAVITY

        # --- Move in the x direction
        self.player_sprite.center_x += self.player_sprite.change_x

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            change_x = self.player_sprite.change_x
            if change_x > 0:
                for item in hit_list:
                    # See if we can "run up" a ramp
                    self.player_sprite.center_y += change_x
                    if arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.center_y -= change_x
                        self.player_sprite.right = \
                            min(item.left, self.player_sprite.right)
            elif change_x < 0:
                for item in hit_list:
                    # See if we can "run up" a ramp
                    self.player_sprite.center_y += change_x
                    if arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.center_y -= change_x
                        self.player_sprite.left = min(item.right,
                                                      self.player_sprite.left)
            else:
                print("Error, collision while player wasn't moving.")

        # --- Move in the y direction
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            if self.player_sprite.change_y > 0:
                for item in hit_list:
                    self.player_sprite.top = min(item.bottom,
                                                 self.player_sprite.top)
            elif self.player_sprite.change_y < 0:
                for item in hit_list:
                    while arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.bottom += 0.5
            else:
                print("Error, collision while player wasn't moving.")
            self.player_sprite.change_y = 0


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


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("images/character.png",
                                           SPRITE_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 270
        self.all_sprites_list.append(self.player_sprite)

        map_array = get_map()

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

        self.physics_engine = PhysicsEngine(self.player_sprite, self.wall_list)

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
        self.all_sprites_list.draw()

        # Put the text on the screen.
        # Adjust the text position based on the viewport so that we don't
        # scroll the text too.
        distance = self.view_left + self.player_sprite.right
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
        Called whenever the mouse moves.
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
        Called when the user presses a mouse button.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def animate(self, delta_time):
        """ Movement and game logic """

        if self.view_left + self.player_sprite.right >= END_OF_MAP:
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


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()
