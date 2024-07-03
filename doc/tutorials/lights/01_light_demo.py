"""
Light demo
"""
import arcade
from arcade.future.light import Light, LightLayer

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Lighting Demo"
VIEWPORT_MARGIN = 200
MOVEMENT_SPEED = 5

class MyGame(arcade.Window):
    """ Main Game Window """

    def __init__(self, width, height, title):
        """ Set up the class. """
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.background_sprite_list = None
        self.player_list = None
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # camera for scrolling
        self.camera = None

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

        # setup camera
        self.camera = arcade.camera.Camera2D()

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
        position = self.camera.position

        top_left = self.camera.top_left
        bottom_right = self.camera.bottom_right

        # Scroll left
        left_boundary = top_left[0] + VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            position = position[0] + (self.player_sprite.left - left_boundary), position[1]

        # Scroll right
        right_boundary = bottom_right[0] - VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            position = position[0] + (self.player_sprite.right - right_boundary), position[1]

        # Scroll up
        top_boundary = top_left[1] - VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            position = position[0], position[1] + (self.player_sprite.top - top_boundary)

        # Scroll down
        bottom_boundary = bottom_right[1] + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            position = position[0], position[1] + (self.player_sprite.bottom - bottom_boundary)

        self.camera.position = position

        # Make sure our boundaries are integer values. While the viewport does
        # support floating point numbers, for this application we want every pixel
        # in the view port to map directly onto a pixel on the screen. We don't want
        # any rounding errors.
        bottom_left = self.camera.bottom_left
        self.camera.bottom_left = int(bottom_left[0]), int(bottom_left[1])

        self.camera.use()

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
