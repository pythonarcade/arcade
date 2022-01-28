"""
This example procedurally develops a random cave based on
Binary Space Partitioning (BSP)

For more information, see:
https://roguebasin.roguelikedevelopment.org/index.php?title=Basic_BSP_Dungeon_generation
https://github.com/DanaL/RLDungeonGenerator

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.procedural_caves_bsp
"""

import random
import arcade
import timeit
import math
import os

# Sprite scaling. Make this larger, like 0.5 to zoom in and add
# 'mystery' to what you can see. Make it smaller, like 0.1 to see
# more of the map.
WALL_SPRITE_SCALING = 0.5
PLAYER_SPRITE_SCALING = 0.25

WALL_SPRITE_SIZE = int(128 * WALL_SPRITE_SCALING)

# How big the grid is
GRID_WIDTH = 100
GRID_HEIGHT = 100

AREA_WIDTH = GRID_WIDTH * WALL_SPRITE_SIZE
AREA_HEIGHT = GRID_HEIGHT * WALL_SPRITE_SIZE

# How fast the player moves
MOVEMENT_SPEED = 5

# How close the player can get to the edge before we scroll.
VIEWPORT_MARGIN = 300

# How big the window is
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Procedural Caves BSP Example"

MERGE_SPRITES = False


class Room:
    """ A room """
    def __init__(self, r, c, h, w):
        self.row = r
        self.col = c
        self.height = h
        self.width = w


class RLDungeonGenerator:
    """ Generate the dungeon """
    def __init__(self, w, h):
        """ Create the board """
        self.MAX = 15  # Cutoff for when we want to stop dividing sections
        self.width = w
        self.height = h
        self.leaves = []
        self.dungeon = []
        self.rooms = []

        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append('#')

            self.dungeon.append(row)

    def random_split(self, min_row, min_col, max_row, max_col):
        # We want to keep splitting until the sections get down to the threshold
        seg_height = max_row - min_row
        seg_width = max_col - min_col

        if seg_height < self.MAX and seg_width < self.MAX:
            self.leaves.append((min_row, min_col, max_row, max_col))
        elif seg_height < self.MAX <= seg_width:
            self.split_on_vertical(min_row, min_col, max_row, max_col)
        elif seg_height >= self.MAX > seg_width:
            self.split_on_horizontal(min_row, min_col, max_row, max_col)
        else:
            if random.random() < 0.5:
                self.split_on_horizontal(min_row, min_col, max_row, max_col)
            else:
                self.split_on_vertical(min_row, min_col, max_row, max_col)

    def split_on_horizontal(self, min_row, min_col, max_row, max_col):
        split = (min_row + max_row) // 2 + random.choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, split, max_col)
        self.random_split(split + 1, min_col, max_row, max_col)

    def split_on_vertical(self, min_row, min_col, max_row, max_col):
        split = (min_col + max_col) // 2 + random.choice((-2, -1, 0, 1, 2))
        self.random_split(min_row, min_col, max_row, split)
        self.random_split(min_row, split + 1, max_row, max_col)

    def carve_rooms(self):
        for leaf in self.leaves:
            # We don't want to fill in every possible room or the
            # dungeon looks too uniform
            if random.random() > 0.80:
                continue
            section_width = leaf[3] - leaf[1]
            section_height = leaf[2] - leaf[0]

            # The actual room's height and width will be 60-100% of the
            # available section.
            room_width = round(random.randrange(60, 100) / 100 * section_width)
            room_height = round(random.randrange(60, 100) / 100 * section_height)

            # If the room doesn't occupy the entire section we are carving it from,
            # 'jiggle' it a bit in the square
            if section_height > room_height:
                room_start_row = leaf[0] + random.randrange(section_height - room_height)
            else:
                room_start_row = leaf[0]

            if section_width > room_width:
                room_start_col = leaf[1] + random.randrange(section_width - room_width)
            else:
                room_start_col = leaf[1]

            self.rooms.append(Room(room_start_row, room_start_col, room_height, room_width))
            for r in range(room_start_row, room_start_row + room_height):
                for c in range(room_start_col, room_start_col + room_width):
                    self.dungeon[r][c] = '.'

    @staticmethod
    def are_rooms_adjacent(room1, room2):
        """ See if two rooms are next to each other. """
        adj_rows = []
        adj_cols = []
        for r in range(room1.row, room1.row + room1.height):
            if room2.row <= r < room2.row + room2.height:
                adj_rows.append(r)

        for c in range(room1.col, room1.col + room1.width):
            if room2.col <= c < room2.col + room2.width:
                adj_cols.append(c)

        return adj_rows, adj_cols

    @staticmethod
    def distance_between_rooms(room1, room2):
        """ Get the distance between two rooms """
        centre1 = (room1.row + room1.height // 2, room1.col + room1.width // 2)
        centre2 = (room2.row + room2.height // 2, room2.col + room2.width // 2)

        return math.sqrt((centre1[0] - centre2[0]) ** 2 + (centre1[1] - centre2[1]) ** 2)

    def carve_corridor_between_rooms(self, room1, room2):
        """ Make a corridor between rooms """
        if room2[2] == 'rows':
            row = random.choice(room2[1])
            # Figure out which room is to the left of the other
            if room1.col + room1.width < room2[0].col:
                start_col = room1.col + room1.width
                end_col = room2[0].col
            else:
                start_col = room2[0].col + room2[0].width
                end_col = room1.col
            for c in range(start_col, end_col):
                self.dungeon[row][c] = '.'

            if end_col - start_col >= 4:
                self.dungeon[row][start_col] = '+'
                self.dungeon[row][end_col - 1] = '+'
            elif start_col == end_col - 1:
                self.dungeon[row][start_col] = '+'
        else:
            col = random.choice(room2[1])
            # Figure out which room is above the other
            if room1.row + room1.height < room2[0].row:
                start_row = room1.row + room1.height
                end_row = room2[0].row
            else:
                start_row = room2[0].row + room2[0].height
                end_row = room1.row

            for r in range(start_row, end_row):
                self.dungeon[r][col] = '.'

            if end_row - start_row >= 4:
                self.dungeon[start_row][col] = '+'
                self.dungeon[end_row - 1][col] = '+'
            elif start_row == end_row - 1:
                self.dungeon[start_row][col] = '+'

    def find_closest_unconnect_groups(self, groups, room_dict):
        """
        Find two nearby rooms that are in difference groups, draw
        a corridor between them and merge the groups
        """

        shortest_distance = 99999
        start = None
        start_group = None
        nearest = None

        for group in groups:
            for room in group:
                key = (room.row, room.col)
                for other in room_dict[key]:
                    if not other[0] in group and other[3] < shortest_distance:
                        shortest_distance = other[3]
                        start = room
                        nearest = other
                        start_group = group

        self.carve_corridor_between_rooms(start, nearest)

        # Merge the groups
        other_group = None
        for group in groups:
            if nearest[0] in group:
                other_group = group
                break

        start_group += other_group
        groups.remove(other_group)

    def connect_rooms(self):
        """
        Build a dictionary containing an entry for each room. Each bucket will
        hold a list of the adjacent rooms, weather they are adjacent along rows or
        columns and the distance between them.

        Also build the initial groups (which start of as a list of individual rooms)
        """
        groups = []
        room_dict = {}
        for room in self.rooms:
            key = (room.row, room.col)
            room_dict[key] = []
            for other in self.rooms:
                other_key = (other.row, other.col)
                if key == other_key:
                    continue
                adj = self.are_rooms_adjacent(room, other)
                if len(adj[0]) > 0:
                    room_dict[key].append((other, adj[0], 'rows', self.distance_between_rooms(room, other)))
                elif len(adj[1]) > 0:
                    room_dict[key].append((other, adj[1], 'cols', self.distance_between_rooms(room, other)))

            groups.append([room])

        while len(groups) > 1:
            self.find_closest_unconnect_groups(groups, room_dict)

    def generate_map(self):
        """ Make the map """
        self.random_split(1, 1, self.height - 1, self.width - 1)
        self.carve_rooms()
        self.connect_rooms()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.grid = None
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None
        self.view_bottom = 0
        self.view_left = 0
        self.physics_engine = None

        self.processing_time = 0
        self.draw_time = 0

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game """
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()

        # Create cave system using a 2D grid
        dg = RLDungeonGenerator(GRID_WIDTH, GRID_HEIGHT)
        dg.generate_map()

        # Create sprites based on 2D grid
        if not MERGE_SPRITES:
            # This is the simple-to-understand method. Each grid location
            # is a sprite.
            for row in range(dg.height):
                for column in range(dg.width):
                    value = dg.dungeon[row][column]
                    if value == '#':
                        wall = arcade.Sprite(":resources:images/tiles/grassCenter.png", WALL_SPRITE_SCALING)
                        wall.center_x = column * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                        wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                        self.wall_list.append(wall)
        else:
            # This uses new Arcade 1.3.1 features, that allow me to create a
            # larger sprite with a repeating texture. So if there are multiple
            # cells in a row with a wall, we merge them into one sprite, with a
            # repeating texture for each cell. This reduces our sprite count.
            for row in range(dg.height):
                column = 0
                while column < dg.width:
                    while column < dg.width and dg.dungeon[row][column] != '#':
                        column += 1
                    start_column = column
                    while column < dg.width and dg.dungeon[row][column] == '#':
                        column += 1
                    end_column = column - 1

                    column_count = end_column - start_column + 1
                    column_mid = (start_column + end_column) / 2

                    wall = arcade.Sprite(":resources:images/tiles/grassCenter.png", WALL_SPRITE_SCALING,
                                         repeat_count_x=column_count)
                    wall.center_x = column_mid * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.width = WALL_SPRITE_SIZE * column_count
                    self.wall_list.append(wall)

        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png",
                                           PLAYER_SPRITE_SCALING)
        self.player_list.append(self.player_sprite)

        # Randomly place the player. If we are in a wall, repeat until we aren't.
        placed = False
        while not placed:

            # Randomly position
            self.player_sprite.center_x = random.randrange(AREA_WIDTH)
            self.player_sprite.center_y = random.randrange(AREA_HEIGHT)

            # Are we in a wall?
            walls_hit = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)
            if len(walls_hit) == 0:
                # Not in a wall! Success!
                placed = True

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)

    def on_draw(self):
        """ Render the screen. """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Draw the sprites
        self.wall_list.draw()
        self.player_list.draw()

        # Draw info on the screen
        sprite_count = len(self.wall_list)

        output = f"Sprite Count: {sprite_count}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 20 + self.view_bottom,
                         arcade.color.WHITE, 16)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 40 + self.view_bottom,
                         arcade.color.WHITE, 16)

        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 60 + self.view_bottom,
                         arcade.color.WHITE, 16)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        start_time = timeit.default_timer()

        # Move the player
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + WINDOW_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + WINDOW_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                WINDOW_WIDTH + self.view_left,
                                self.view_bottom,
                                WINDOW_HEIGHT + self.view_bottom)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    """ Main function, start up window and run """
    game = MyGame(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
