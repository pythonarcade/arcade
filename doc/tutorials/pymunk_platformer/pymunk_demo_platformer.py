"""
Example of Pymunk Physics Engine

Platformer
"""
import math
import arcade
from typing import Optional
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

import logging
LOG = logging.getLogger(__name__)

SCREEN_TITLE = "PyMunk Top-Down"
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_TILES = 0.5


SPRITE_IMAGE_SIZE = 128
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

SCREEN_WIDTH = SPRITE_SIZE * 25
SCREEN_HEIGHT = SPRITE_SIZE * 15

# --- Physics forces. Higher number, faster accelerating.

GRAVITY = 1500

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1800

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# How much force to put on the bullet
BULLET_MOVE_FORCE = 4500

# Make bullet less affected by gravity
BULLET_GRAVITY = 300

# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


class PlayerSprite(arcade.Sprite):
    def __init__(self):
        # Let parent initialize
        super().__init__(scale=SPRITE_SCALING_PLAYER)

        # Images from Kenney.nl's Character pack
        # main_path = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"
        main_path = ":resources:images/animated_characters/female_person/femalePerson"
        # main_path = ":resources:images/animated_characters/male_person/malePerson"
        # main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"
        # main_path = ":resources:images/animated_characters/zombie/zombie"
        # main_path = ":resources:images/animated_characters/robot/robot"

        idle_texture = arcade.load_texture(f"{main_path}_idle.png")
        jump_texture = arcade.load_texture(f"{main_path}_jump.png")
        fall_texture = arcade.load_texture(f"{main_path}_fall.png")

        # Load textures for idle standing
        self.idle_texture_pair = idle_texture, idle_texture.flip_left_right()
        self.jump_texture_pair = jump_texture, jump_texture.flip_left_right()
        self.fall_texture_pair = fall_texture, fall_texture.flip_left_right()

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture(f"{main_path}_walk{i}.png")
            self.walk_textures.append((texture, texture.flip_left_right()))

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        # self.set_hit_box(self.texture.hit_box_points)

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        self.is_on_ladder = False
        self.climbing = False
        self.cur_texture = 0

        self.x_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):

        # Figure out if we need to face left or right
        if dx < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        """
        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(dy) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return
        """

        # Jumping animation
        if not is_on_ground:
            if dy > DEAD_ZONE and not self.is_on_ladder:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE and not self.is_on_ladder:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return

        # Idle animation
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        self.x_odometer += dx

        if abs(self.x_odometer) > 8:
            self.x_odometer = 0

            # Walking animation
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]


class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """

        # Init the parent class
        super().__init__(width, height, title)

        # Player sprite
        self.player_sprite: Optional[arcade.Sprite] = None

        # Sprite lists we need
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        # The PyMunk physics engine!
        self.physics_engine: Optional[PymunkPhysicsEngine] = None

        # Set background color
        self.background_color = arcade.color.AMAZON

        # # Turn on logging
        # format = '%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s()] %(message)s'
        # logging.basicConfig(format=format,
        #                     datefmt='%H:%M:%S',
        #                     level=logging.DEBUG)

    def setup(self):
        """ Set up everything with the game """

        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = PlayerSprite()
        self.player_sprite.center_x = 250
        self.player_sprite.center_y = 250
        self.player_list.append(self.player_sprite)

        map_name = ":resources:/tiled_maps/pymunk_test_map.json"

        # Read in the tiled map
        my_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)

        # --- Read in layers ---
        self.wall_list = my_map.sprite_lists["Platforms"]
        self.item_list = my_map.sprite_lists["Dynamic Items"]
        # --- Pymunk Physics Engine Setup ---

        # The default damping for every object controls the percent of velocity
        # the object will keep each second. A value of 1.0 is no speed loss,
        # 0.9 is 10% per second, 0.1 is 90% per second.
        # For top-down games, this is basically the friction for moving objects.
        # For platformers with gravity, this should probably be set to 1.0.
        # Default value is 1.0 if not specified.
        damping = 1.0

        # Set the gravity. (0, 0) is good for outer space and top-down.
        gravity = (0, -GRAVITY)

        # Create the physics engine
        self.physics_engine = PymunkPhysicsEngine(damping=damping,
                                                  gravity=gravity)

        def wall_hit_handler(bullet_sprite, wall_sprite, arbiter, space, data):
            """ Called for bullet/wall collision """
            # bullet_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "wall", post_handler=wall_hit_handler)

        def item_hit_handler(bullet_sprite, item_sprite, arbiter, space, data):
            """ Called for bullet/wall collision """
            # bullet_sprite.remove_from_sprite_lists()
            # item_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "item", post_handler=item_hit_handler)

        # Add the player.
        # For the player, we set the damping to a lower value, which increases
        # the damping rate. This prevents the character from traveling too far
        # after the player lets off the movement keys.
        # Setting the moment of intertia to PymunkPhysicsEngine.MOMENT_INF prevents it from
        # rotating.
        # Friction normally goes between 0 (no friction) and 1.0 (high friction)
        # Friction is between two objects in contact. It is important to remember
        # in top-down games that friction moving along the 'floor' is controlled
        # by damping.
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=1.0,
                                       damping=0.4,
                                       mass=2,
                                       moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

        # Create the walls.
        # By setting the body type to PymunkPhysicsEngine.STATIC the walls can't
        # move.
        # Movable objects that respond to forces are PymunkPhysicsEngine.DYNAMIC
        # PymunkPhysicsEngine.KINEMATIC objects will move, but are assumed to be
        # repositioned by code and don't respond to physics forces.
        # Dynamic is default.
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=0.6,
                                            collision_type="wall",
                                            body_type=PymunkPhysicsEngine.STATIC)

        # Create the items
        self.physics_engine.add_sprite_list(self.item_list,
                                            friction=0.7,
                                            collision_type="item")

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """

        bullet = arcade.SpriteSolidColor(width=20, height=5, color=arcade.color.DARK_YELLOW)
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # What is the 1/2 size of this sprite, so we can figure out how far
        # away to spawn the bullet
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to to spawn bullet away from player in proper direction
        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)

        # Set angle of bullet
        bullet.angle = math.degrees(angle)

        # Gravity to use for the bullet
        # If we don't use custom gravity, bullet drops too fast, or we have
        # to make it go too fast.
        # Force is in relation to bullet's angle.
        bullet_gravity = (0, -BULLET_GRAVITY)

        # Add the sprite. This needs to be done AFTER setting the fields above.
        self.physics_engine.add_sprite(bullet,
                                       mass=0.1,
                                       damping=1.0,
                                       friction=0.6,
                                       collision_type="bullet",
                                       gravity=bullet_gravity,
                                       elasticity=0.9)

        # Add force to bullet
        force = (BULLET_MOVE_FORCE, 0)
        self.physics_engine.apply_force(bullet, force)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            # find out if player is standing on ground
            if self.physics_engine.is_on_ground(self.player_sprite):
                # She is! Go ahead and jump
                physics_object = self.physics_engine.get_physics_object(self.player_sprite)
                physics_object.body.apply_impulse_at_local_point((0, PLAYER_JUMP_IMPULSE))

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.left_pressed and not self.right_pressed:
            grounding = self.physics_engine.check_grounding(self.player_sprite)
            if grounding['body'] is not None:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)

            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)

        elif self.right_pressed and not self.left_pressed:
            grounding = self.physics_engine.check_grounding(self.player_sprite)
            if grounding['body'] is not None:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)

            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # --- Move items in the physics engine
        self.physics_engine.step()

    def on_draw(self):
        """ Draw everything """
        self.clear()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.item_list.draw()
        self.player_list.draw()

def main():
    """ Main function """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
