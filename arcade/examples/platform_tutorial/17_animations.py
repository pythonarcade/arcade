"""
Platformer Game

python -m arcade.examples.platform_tutorial.17_animations
"""
import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Constants used to track the direction a character is facing
RIGHT_FACING = 0
LEFT_FACING = 1

class Character(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        self.facing_direction = RIGHT_FACING

        self.cur_texture = 0

        main_path = f":resources:images/animated_characters/{name_folder}/{name_file}"
        # Load textures for idle, jump, and fall states
        idle_texture = arcade.load_texture(f"{main_path}_idle.png")
        jump_texture = arcade.load_texture(f"{main_path}_jump.png")
        fall_texture = arcade.load_texture(f"{main_path}_fall.png")
        # Make pairs with left and right facing textures
        self.idle_texture_pair = idle_texture, idle_texture.flip_left_right()
        self.jump_texture_pair = jump_texture, jump_texture.flip_left_right()
        self.fall_texture_pair = fall_texture, fall_texture.flip_left_right()

        # Load textures for walking with left and right facing textures
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture(f"{main_path}_walk{i}.png")
            self.walk_textures.append((texture, texture.flip_left_right()))

        self.climbing_textures = (
            arcade.load_texture(f"{main_path}_climb0.png"),
            arcade.load_texture(f"{main_path}_climb1.png")
        )

        # This variable will change dynamically and will represent the currently
        # active texture.
        self.texture = self.idle_texture_pair[0]


class PlayerCharacter(Character):
    def __init__(self):
        super().__init__("female_adventurer", "femaleAdventurer")

        # Track extra state related to the player. We will use these for change
        # textures in animations
        self.climbing = False

    def update_animation(self, delta_time):
        # Figure out the direction the character is facing based on the movement
        # and previous direction.
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Handle animations for climbing on ladders. We use the absolute value
        # of change_y here because we don't care if the character is moving up
        # or down, the animation stays the same.
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return
        
        # Handling jumping animations
        if self.change_y > 0 and not self.climbing:
            self.texture = self.jump_texture_pair[self.facing_direction]
            return
        elif self.change_y < 0 and not self.climbing:
            self.texture = self.fall_texture_pair[self.facing_direction]
            return

        # Handle idle animations
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return
        
        # Handle walking
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
        

class GameView(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Track the current state of our input
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Variable to hold our texture for our player
        self.player_texture = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable to hold our Tiled Map
        self.tile_map = None

        # Replacing all of our SpriteLists with a Scene variable
        self.scene = None

        # A variable to store our camera object
        self.camera = None

        # A variable to store our gui camera object
        self.gui_camera = None

        # This variable will store our score as an integer.
        self.score = 0

        # This variable will store the text for score that we will draw to the screen.
        self.score_text = None

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Should we reset the score?
        self.reset_score = True

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True
            },
            "Moving Platforms": {
                "use_spatial_hash": False
            },
            "Ladders": {
                "use_spatial_hash": True
            }
        }

        # Load our TileMap
        self.tile_map = arcade.load_tilemap(
            ":resources:tiled_maps/map_with_ladders.json",
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Create our Scene Based on the TileMap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Create a Platformer Physics Engine, this will handle moving our
        # player as well as collisions between the player sprite and
        # whatever SpriteList we specify for the walls.
        # It is important to supply static to the walls parameter. There is a
        # platforms parameter that is intended for moving platforms.
        # If a platform is supposed to move, and is added to the walls list,
        # it will not be moved.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Platforms"],
            gravity_constant=GRAVITY,
            platforms=self.scene["Moving Platforms"],
            ladders=self.scene["Ladders"]
        )

        # Initialize our camera, setting a viewport the size of our window.
        self.camera = arcade.Camera2D()

        # Initialize our gui camera, initial settings are the same as our world camera.
        self.gui_camera = arcade.Camera2D()

        # Reset the score if we should
        if self.reset_score:
            self.score = 0
        self.reset_score = True

        # Initialize our arcade.Text object for score
        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Calculate the right edge of the map in pixels
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width)
        self.end_of_map *= self.tile_map.scaling 

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate our camera before drawing
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate our GUI camera
        self.gui_camera.use()

        # Draw our Score
        self.score_text.draw()

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Move the player using our physics engine
        self.physics_engine.update()

        # Update our characters animation state
        if self.physics_engine.is_on_ladder():
            self.player_sprite.climbing = True
        else:
            self.player_sprite.climbing = False

        # Actually trigger animation updates. We've added the Background and Coins layer
        # here as well. Our Tiled map has some animated tiles built-in, check out the flags
        # and torches on the map.
        self.scene.update_animation(
            delta_time,
            [
                "Coins",
                "Background",
                "Player"
            ]
        )

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75
            self.score_text.text = f"Score: {self.score}"

        # Center our camera on the player
        self.camera.position = self.player_sprite.position

    def process_keychange(self):
        # First handle the case where we have moved up. This needs to be handled
        # differently to move the player upwards if they are on a ladder, or
        # perform a jump if they are not on a ladder. This code might look
        # different if we had a separate button for jumping, we would only need
        # to handle moving upwards if we were on a ladder for the up key then.
        # Here we also handle the case where we have moved down while on a ladder.
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Now we need a special handling of our vertical movement while we are 
        # on a ladder, but have no input specified. When we jump, the physics
        # engine takes care of resetting our vertical movement to zero once we've
        # hit the ground. However for ladders, we need to ensure that we set the
        # vertical movement back to zero if the user does not give input, otherwise
        # once a user starts climbing a ladder, they will move upwards automatically
        # until they reach the end of the ladder. You can try commenting out this
        # block to see what that effect looks like.
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Now we just handle our horizontal movement, very similar to how we
        # did before, but now just combined in our new function.
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.ESCAPE:
            self.setup()

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

        self.process_keychange()


def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
