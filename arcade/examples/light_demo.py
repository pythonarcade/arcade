"""
Show how to use lights.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.light_demo
"""
import arcade
from arcade.experimental.lights import Light, LightLayer

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Lighting Demo"
VIEWPORT_MARGIN = 200
MOVEMENT_SPEED = 5

# This is the color used for 'ambient light'. If you don't want any
# ambient light, set it to black.
AMBIENT_COLOR = (10, 10, 10)


class MyGame(arcade.Window):
    """ Main Game Window """

    def __init__(self, width, height, title):
        """ Set up the class. """
        super().__init__(width, height, title, resizable=True)

        # Sprite lists
        self.background_sprite_list = None
        self.player_list = None
        self.wall_list = None
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # Used for scrolling
        self.view_left = 0
        self.view_bottom = 0

        # --- Light related ---
        # List of all the lights
        self.light_layer = None
        # Individual light we move with player, and turn on/off
        self.player_light = None

    def setup(self):
        """ Create everything """

        # Create sprite lists
        self.background_sprite_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Create player sprite
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png",
                                           0.4)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)

        # --- Light related ---
        # Lights must shine on something. If there is no background sprite or color,
        # you will just see black. Therefore, we use a loop to create a whole bunch of brick tiles to go in the
        # background.
        for x in range(-128, 2000, 128):
            for y in range(-128, 1000, 128):
                sprite = arcade.Sprite(":resources:images/tiles/brickTextureWhite.png")
                sprite.position = x, y
                self.background_sprite_list.append(sprite)

        # Create a light layer, used to render things to, then post-process and
        # add lights. This must match the screen size.
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.light_layer.set_background_color(arcade.color.BLACK)

        # Here we create a bunch of lights.

        # Create a small white light
        x = 100
        y = 200
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.WHITE
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create an overlapping, large white light
        x = 300
        y = 150
        radius = 200
        color = arcade.csscolor.WHITE
        mode = 'soft'
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create three, non-overlapping RGB lights
        x = 50
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.RED
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 250
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.GREEN
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 450
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.BLUE
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create three, overlapping RGB lights
        x = 650
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.RED
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 750
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.GREEN
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 850
        y = 450
        radius = 100
        mode = 'soft'
        color = arcade.csscolor.BLUE
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create three, overlapping RGB lights
        # But 'hard' lights that don't fade out.
        x = 650
        y = 150
        radius = 100
        mode = 'hard'
        color = arcade.csscolor.RED
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 750
        y = 150
        radius = 100
        mode = 'hard'
        color = arcade.csscolor.GREEN
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        x = 850
        y = 150
        radius = 100
        mode = 'hard'
        color = arcade.csscolor.BLUE
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create a light to follow the player around.
        # We'll position it later, when the player moves.
        # We'll only add it to the light layer when the player turns the light
        # on. We start with the light off.
        radius = 150
        mode = 'soft'
        color = arcade.csscolor.WHITE
        self.player_light = Light(0, 0, radius, color, mode)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """ Draw everything. """
        self.clear()

        # --- Light related ---
        # Everything that should be affected by lights gets rendered inside this
        # 'with' statement. Nothing is rendered to the screen yet, just the light
        # layer.
        with self.light_layer:
            self.background_sprite_list.draw()
            self.player_list.draw()

        # Draw the light layer to the screen.
        # This fills the entire screen with the lit version
        # of what we drew into the light layer above.
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        # Now draw anything that should NOT be affected by lighting.
        arcade.draw_text("Press SPACE to turn character light on/off.",
                         10 + self.view_left, 10 + self.view_bottom,
                         arcade.color.WHITE, 20)

    def on_resize(self, width, height):
        """ User resizes the screen. """

        # --- Light related ---
        # We need to resize the light layer to
        self.light_layer.resize(width, height)

        # Scroll the screen so the user is visible
        self.scroll_screen()

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
        elif key == arcade.key.SPACE:
            # --- Light related ---
            # We can add/remove lights from the light layer. If they aren't
            # in the light layer, the light is off.
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)

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

        # --- Light related ---
        # We can easily move the light by setting the position,
        # or by center_x, center_y.
        self.player_light.position = self.player_sprite.position

        # Scroll the screen so we can see the player
        self.scroll_screen()


if __name__ == "__main__":
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
