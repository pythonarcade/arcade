""" 
A simple example that demonstrates using multiple cameras to allow a split 
screen using Arcade's 3.0 Camera2D.

The left screen follows the player that is controlled by WASD, and the right
follows the player controlled by the keyboard.

If Python and Arcade are installed, this example can be run
from the command line with:
python -m arcade.examples.camera2d_splitscreen
"""

from typing import List, Optional, Tuple

import pymunk

import arcade


TITLE = "Split Screen Example"
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
BACKGROUND_COLOR = arcade.color.SPACE_CADET
BACKGROUND_IMAGE = ":resources:images/backgrounds/stars.png"

DEFAULT_DAMPING = 1.0

GRAVITY = 0.0
SHIP_MASS = 1.0
SHIP_FRICTION = 0.0
SHIP_ELASTICITY = 0.1

SHIP_FRICTION = 0.0
ROTATION_SPEED = 0.05
THRUSTER_FORCE = 200.0

SHIP_SCALING = 0.5

PLAYER_ONE = 0
PLAYER_TWO = 1

CAMERA_ONE = 0
CAMERA_TWO = 1


class Player(arcade.Sprite):
    def __init__(self, main,
                 start_position: Tuple,
                 player_num: int):
        self.shape = None

        if player_num == PLAYER_ONE:
            self.sprite_filename = ":resources:images/space_shooter/playerShip1_orange.png"
        else:
            self.sprite_filename = ":resources:images/space_shooter/playerShip1_blue.png"

        self.player_num = player_num
        self.dx = 0.0
        self.dy = 0.0
        self.body : pymunk.Body
        self.start_position = start_position
        self.friction = SHIP_FRICTION

        self.w_pressed = 0.0
        self.s_pressed = 0.0
        self.a_pressed = 0.0
        self.d_pressed = 0.0

        self.left_pressed = 0.0
        self.right_pressed = 0.0
        self.up_pressed = 0.0
        self.down_pressed = 0.0

        super().__init__(self.sprite_filename)
        self.position = start_position
        self.mass = SHIP_MASS
        self.friction = SHIP_FRICTION
        self.elasticity = SHIP_ELASTICITY
        self.texture = arcade.load_texture(self.sprite_filename,
                                           hit_box_algorithm=arcade.hitbox.PymunkHitBoxAlgorithm())
        self.main = main
        self.scale = SHIP_SCALING

    def setup(self):
        self.body = self.main.physics_engine.get_physics_object(self).body
        self.shape = self.main.physics_engine.get_physics_object(self).shape

    def apply_angle_damping(self):
        self.body.angular_velocity /= 1.05

    def update(self, delta_time: float = 1/60):
        super().update(delta_time)

        if self.player_num == PLAYER_ONE:
            self.dx = self.a_pressed + self.d_pressed
            self.dy = self.w_pressed + self.s_pressed

        elif self.player_num == PLAYER_TWO:
            self.dx = self.right_pressed + self.left_pressed
            self.dy = self.up_pressed + self.down_pressed
        
        self.body.apply_force_at_world_point((self.dx, -self.dy), (self.center_x, self.center_y))

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.W:
            self.w_pressed = -THRUSTER_FORCE
        elif key == arcade.key.S:
            self.s_pressed = THRUSTER_FORCE
        elif key == arcade.key.A:
            self.a_pressed = -THRUSTER_FORCE
        elif key == arcade.key.D:
            self.d_pressed = THRUSTER_FORCE
        elif key == arcade.key.LEFT:
            self.left_pressed = -THRUSTER_FORCE
        elif key == arcade.key.RIGHT:
            self.right_pressed = THRUSTER_FORCE
        elif key == arcade.key.UP:
            self.up_pressed = -THRUSTER_FORCE
        elif key == arcade.key.DOWN:
            self.down_pressed = THRUSTER_FORCE

    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.W:
            self.w_pressed = 0.0
        elif key == arcade.key.S:
            self.s_pressed = 0.0
        elif key == arcade.key.A:
            self.a_pressed = 0.0
        elif key == arcade.key.D:
            self.d_pressed = 0.0
        elif key == arcade.key.LEFT:
            self.left_pressed = 0.0
        elif key == arcade.key.RIGHT:
            self.right_pressed = 0.0
        elif key == arcade.key.UP:
            self.up_pressed = 0.0
        elif key == arcade.key.DOWN:
            self.down_pressed = 0.0


class Game(arcade.Window):
    def __init__(self):

        self.screen_width: int = SCREEN_WIDTH
        self.screen_height: int = SCREEN_HEIGHT

        super().__init__(self.screen_width,
                         self.screen_height,
                         TITLE,
                         resizable=True)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.background_image: str = BACKGROUND_IMAGE
        self.physics_engine: arcade.PymunkPhysicsEngine

        self.players: arcade.SpriteList
        self.players_list = []

        self.cameras: List[arcade.Camera2D] = []
        self.divider: arcade.SpriteList

    def setup(self):
        self.setup_spritelists()
        self.setup_physics_engine()
        self.setup_players()
        self.setup_players_cameras()
        self.setup_divider()
        self.background = arcade.load_texture(self.background_image)

    def setup_divider(self):
        # It is helpful to have a divider, else the area between
        # the two splits can be hard to see.
        self.divider = arcade.SpriteList()
        self.divider_sprite = arcade.sprite.SpriteSolidColor(
            center_x = self.screen_width / 2,
            center_y = self.screen_height / 2,
            width=3,
            height=self.screen_height,
            color=arcade.color.WHITE
        )
        self.divider.append(self.divider_sprite)

    def setup_spritelists(self):
        self.players = arcade.SpriteList()

    def setup_physics_engine(self):
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=DEFAULT_DAMPING,
                                                         gravity=(0, 0))

    def setup_players(self):
        self.players.append(Player(self, 
                                   (500, 450),
                                   PLAYER_ONE))
        self.players.append(Player(self, 
                                   (750, 500),
                                   PLAYER_TWO))

        self.players_list = [self.players[PLAYER_ONE], self.players[PLAYER_TWO]]

        self.physics_engine.add_sprite(self.players[PLAYER_ONE],
                                       friction=self.players[PLAYER_ONE].friction,
                                       elasticity=self.players[PLAYER_ONE].elasticity,
                                       mass=self.players[PLAYER_ONE].mass,
                                       moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="SHIP")

        self.physics_engine.add_sprite(self.players[PLAYER_TWO],
                                       friction=self.players[PLAYER_TWO].friction,
                                       elasticity=self.players[PLAYER_TWO].elasticity,
                                       mass=self.players[PLAYER_TWO].mass,
                                       moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="SHIP")

        for player in self.players:
            player.setup()

    def setup_players_cameras(self):
        half_width = self.screen_width // 2

        # We will make two cameras for each of our players.
        player_one_camera = arcade.camera.Camera2D()
        player_two_camera = arcade.camera.Camera2D()

        # We can adjust each camera's viewport to create our split screens
        player_one_camera.viewport = arcade.LBWH(0, 0, half_width, self.screen_height)
        player_two_camera.viewport = arcade.LBWH(half_width, 0, half_width, self.screen_height)

        # Calling equalise will equalise/equalize the Camera's projection
        # to match the viewport. If we don't call equalise, proportions
        # of our sprites can appear off.
        player_one_camera.equalize()
        player_two_camera.equalize()

        # Save a list of our cameras for later use
        self.cameras.append(player_one_camera)
        self.cameras.append(player_two_camera)

        self.center_camera_on_player(PLAYER_ONE)
        self.center_camera_on_player(PLAYER_TWO)

    def on_key_press(self, key: int, modifiers: int):
        for player in self.players:
            player.on_key_press(key, modifiers)

        if key == arcade.key.MINUS:
            self.zoom_cameras_out()
        elif key == arcade.key.EQUAL:
            self.zoom_cameras_in()

    def on_key_release(self, key: int, modifers: int):
        for player in self.players:
            player.on_key_release(key, modifers)

    def zoom_cameras_out(self):
        for camera in self.cameras:
            camera.zoom -= 0.1

    def zoom_cameras_in(self):
        for camera in self.cameras:
            camera.zoom += 0.1

    def center_camera_on_player(self, player_num):
        self.cameras[player_num].position = (self.players_list[player_num].center_x,
                                             self.players_list[player_num].center_y)

    def on_update(self, delta_time: float):
        self.players.update(delta_time)
        self.physics_engine.step()
        for player in range(len(self.players_list)):
            # After the player moves, center the camera on the player.
            self.center_camera_on_player(player)

    def on_draw(self):
        # Loop through our cameras, and then draw our objects.
        #
        # If an object should be drawn on both splits, we will
        # need to draw it for each camera, thus the draw functions 
        # will be called twice (because of our loop). 
        #
        # However, if desired, we could draw elements specific to
        # each camera, like a player HUD.
        for camera in range(len(self.cameras)):
            # Activate each players camera, clear it, then draw 
            # the things we want to display on it.
            self.cameras[camera].use()
            self.clear()

            # We want both players to appear in each splitscreen,
            # so draw them for each camera.
            self.players.draw()

            # Likewise, we want the background to appear on
            # both splitscreens.
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(0, 0, self.screen_width, self.screen_height)
            )

        # The default_camera is a property of arcade.Window and we
        # can use it do draw our divider, or other shared elements,
        # such as a score, or other GUIs.
        self.default_camera.use()
        self.divider.draw()

    def on_resize(self, width: float, height: float):
        # We can easily resize the window with split screens by adjusting
        # the viewport in a similar manner to how we created them. Just
        # remember to call equalise!
        half_width = width // 2 

        self.cameras[PLAYER_ONE].viewport = arcade.LBWH(0, 0, half_width, height)
        self.cameras[PLAYER_TWO].viewport = arcade.LBWH(half_width, 0, half_width, height)
        self.cameras[PLAYER_ONE].equalize()
        self.cameras[PLAYER_TWO].equalize()

        # Our divider sprite location will need to be adjusted as
        # we used the screen's width and height to set it's location 
        # earlier
        self.divider_sprite.height = height
        self.divider_sprite.center_x = width / 2
        self.divider_sprite.center_y = height / 2


if __name__ == "__main__":
    window = Game()
    window.setup()
    arcade.run()
