"""
Work with a mini-map

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.minimap_texture
"""

import random
from uuid import uuid4

import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Minimap Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 220

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

# How fast the character moves
PLAYER_MOVEMENT_SPEED = 7

MINIMAP_BACKGROUND_COLOR = arcade.color.ALMOND
MINIMAP_WIDTH = 256
MINIMAP_HEIGHT = 256
MAP_WIDTH = 2048
MAP_HEIGHT = 2048


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.wall_list = None

        # Mini-map related
        # List of all our minimaps (there's just one)
        self.minimap_sprite_list = None
        # Texture and associated sprite to render our minimap to
        self.minimap_texture = None
        self.minimap_sprite = None

        # Set up the player
        self.player_sprite = None

        self.physics_engine = None

        # Camera for sprites, and one for our GUI
        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/"
            "femalePerson_idle.png",
            scale=0.4,
        )
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 512
        self.player_list.append(self.player_sprite)

        # -- Set up several columns of walls
        for x in range(0, MAP_WIDTH, 210):
            for y in range(0, MAP_HEIGHT, 64):
                # Randomly skip a box so the player can find a way through
                if random.randrange(5) > 0:
                    wall = arcade.Sprite(
                        ":resources:images/tiles/grassCenter.png",
                        scale=SPRITE_SCALING,
                    )
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        self.background_color = arcade.color.AMAZON

        # Construct the minimap
        size = (MINIMAP_WIDTH, MINIMAP_HEIGHT)
        self.minimap_texture = arcade.Texture.create_empty(str(uuid4()), size)
        self.minimap_sprite = arcade.Sprite(
            self.minimap_texture,
            center_x=MINIMAP_WIDTH / 2,
            center_y=self.height - MINIMAP_HEIGHT / 2,
        )

        self.minimap_sprite_list = arcade.SpriteList()
        self.minimap_sprite_list.append(self.minimap_sprite)

    def update_minimap(self):
        proj = 0, MAP_WIDTH, 0, MAP_HEIGHT
        atlas = self.minimap_sprite_list.atlas
        with atlas.render_into(self.minimap_texture, projection=proj) as fbo:
            fbo.clear(color=MINIMAP_BACKGROUND_COLOR)
            self.wall_list.draw()
            arcade.draw_sprite(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        with self.camera_sprites.activate():
            # Draw all the sprites.
            self.wall_list.draw()
            self.player_list.draw()

        # Select the (unscrolled) camera for our GUI
        with self.camera_gui.activate():
            # Update the minimap
            self.update_minimap()

            # Draw the minimap
            self.minimap_sprite_list.draw()

            # Draw the GUI
            arcade.draw_rect_filled(
                arcade.rect.XYWH(self.width // 2, 20, self.width, 40),
                color=arcade.color.ALMOND,
            )

            text = (
                f"Scroll value: "
                f"{self.camera_sprites.position[0]:4.1f}, "
                f"{self.camera_sprites.position[1]:4.1f}"
            )
            arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)

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

        # Scroll the screen to the player
        self.scroll_to_player()

    def scroll_to_player(self):
        """
        Scroll the window to the player.
        """

        # Scroll to the proper location
        position = (self.player_sprite.center_x, self.player_sprite.center_y)
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position,
            position,
            CAMERA_SPEED,
        )

    def on_resize(self, width: int, height: int):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        super().on_resize(width, height)
        self.camera_sprites.match_window()
        self.camera_gui.match_window()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
