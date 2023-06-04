"""
Light demo
"""
import arcade
from arcade.experimental.lights import Light, LightLayer

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Lighting Demo"
VIEWPORT_MARGIN = 200
MOVEMENT_SPEED = 5

class MyGame(arcade.Window):
    """ Main Game Window """

    def __init__(self, width, height, title) -> None:
        """ Set up the class. """
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.background_sprite_list = None
        self.player_list = None
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # Used for scrolling
        self.view_left = 0
        self.view_bottom = 0

    def setup(self):
        """ Create everything """

        # Create sprite lists
        self.background_sprite_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Create player sprite
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", 0.4)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)

        for x in range(-128, 2000, 128):
            for y in range(-128, 1000, 128):
                sprite = arcade.Sprite(":resources:images/tiles/brickTextureWhite.png")
                sprite.position = x, y
                self.background_sprite_list.append(sprite)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """ Draw everything. """
        self.clear()

        self.background_sprite_list.draw()
        self.player_list.draw()

    def on_key_press(self, key, _):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, _):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def scroll_screen(self):
        """ Manage Scrolling """

        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left

        # Scroll right
        right_boundary = self.view_left + self.width - VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary

        # Scroll up
        top_boundary = self.view_bottom + self.height - VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom

        # Make sure our boundaries are integer values. While the viewport does
        # support floating point numbers, for this application we want every pixel
        # in the view port to map directly onto a pixel on the screen. We don't want
        # any rounding errors.
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        arcade.set_viewport(self.view_left,
                            self.width + self.view_left,
                            self.view_bottom,
                            self.height + self.view_bottom)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # Scroll the screen so we can see the player
        self.scroll_screen()


if __name__ == "__main__":
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
