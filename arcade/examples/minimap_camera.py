"""
Work with a mini-map

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.minimap_camera
"""

import random

import arcade

SPRITE_SCALING = 0.5

DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600
SCREEN_TITLE = "Minimap Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 220

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

# How fast the character moves
PLAYER_MOVEMENT_SPEED = 7

# Background color must include an alpha component
MINIMAP_BACKGROUND_COLOR = arcade.get_four_byte_color(arcade.color.ALMOND)
MINIMAP_WIDTH = 256
MINIMAP_HEIGHT = 256
MAP_WIDTH = 2048
MAP_HEIGHT = 2048

MAP_PROJECTION_WIDTH = 256
MAP_PROJECTION_HEIGHT = 256


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.player_list = None
        self.wall_list = None

        # Mini-map related
        minimap_viewport = (DEFAULT_SCREEN_WIDTH - MINIMAP_WIDTH,
                            DEFAULT_SCREEN_HEIGHT - MINIMAP_HEIGHT,
                            MINIMAP_WIDTH, MINIMAP_HEIGHT)
        minimap_projection = (0, MAP_PROJECTION_WIDTH, 0, MAP_PROJECTION_HEIGHT)
        self.camera_minimap = arcade.SimpleCamera(viewport=minimap_viewport, projection=minimap_projection)

        # Set up the player
        self.player_sprite = None

        self.physics_engine = None

        # Camera for sprites, and one for our GUI
        viewport = (0, 0, DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)
        projection = (0, DEFAULT_SCREEN_WIDTH, 0, DEFAULT_SCREEN_HEIGHT)
        self.camera_sprites = arcade.SimpleCamera(viewport=viewport, projection=projection)
        self.camera_gui = arcade.SimpleCamera(viewport=viewport)

        self.selected_camera = self.camera_minimap

        # texts
        text = 'Press "A" to select minimap camera. Press "B" to select main camera. Press "W" and "S" to increase ' \
               'or decrease zoom level on the selected camera.\nPress "I" and "K" to enlarge or reduce minimap.'
        self.instructions = arcade.Text(text, 10, 25, arcade.color.BLACK_BEAN, 10, multiline=True,
                                        width=DEFAULT_SCREEN_WIDTH)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png",
                                           scale=0.4)
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 512
        self.player_list.append(self.player_sprite)

        # -- Set up several columns of walls
        for x in range(0, MAP_WIDTH, 210):
            for y in range(0, MAP_HEIGHT, 64):
                # Randomly skip a box so the player can find a way through
                if random.randrange(5) > 0:
                    wall = arcade.Sprite(":resources:images/tiles/grassCenter.png", scale=SPRITE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()

        # Draw new minimap using the camera
        self.camera_minimap.use()
        self.clear(MINIMAP_BACKGROUND_COLOR)
        self.wall_list.draw()
        self.player_list.draw()

        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()

        # Draw the GUI
        arcade.draw_rectangle_filled(self.width // 2, 20, self.width, 40, arcade.color.ALMOND)
        self.instructions.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.A:
            self.selected_camera = self.camera_minimap
        elif key == arcade.key.B:
            self.selected_camera = self.camera_sprites
        elif key == arcade.key.W:
            self.selected_camera.zoom += 0.1
        elif key == arcade.key.S:
            if (self.selected_camera.zoom - 0.1) > 0:
                self.selected_camera.zoom -= 0.1
        elif key == arcade.key.I:
            l, b, w, h = self.camera_minimap.viewport
            self.camera_minimap.viewport = l + 100, b + 100, w - 100, h - 100
        elif key == arcade.key.K:
            l, b, w, h = self.camera_minimap.viewport
            self.camera_minimap.viewport = l - 100, b - 100, w + 100, h + 100

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # Center the screen to the player
        self.camera_sprites.center(self.player_sprite.position, CAMERA_SPEED)

        # Center the minimap viewport to the player in the minimap
        self.camera_minimap.center(self.player_sprite.position, CAMERA_SPEED)

    def on_resize(self, width: int, height: int):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        self.camera_sprites.resize(width, height, resize_projection=False)
        self.camera_gui.resize(width, height)
        self.camera_minimap.viewport = (width - self.camera_minimap.viewport_width,
                                        height - self.camera_minimap.viewport_height,
                                        self.camera_minimap.viewport_width,
                                        self.camera_minimap.viewport_height)


def main():
    """ Main function """
    window = MyGame(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
