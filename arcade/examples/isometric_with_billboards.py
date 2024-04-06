# flake8: noqa
"""
Using the Orthographic Projector to make a cool isometric scene.

By using a SpriteList and a BillboardList we can create the floor and a little character
to move around the scene.

The traditional isometric perspective comes from two effects. Firstly the camera rotates "upwards" by 30 degrees.
Then it is rotated by 45 degrees. Together with an orthographic camera allows you
to show all 3 dimensions, but depth and vertical height line up so you do loose some dimensionality.

Mathematically this is done using cos and sin of 45 and 60 degrees. We use 60 because it is 90 - 30
to get the "upwards" motion. These values can be represented by fractions so we can avoid using
the actual acos and asin methods.

first the 30 degree rotation forward vector
(0.0, 0.0, -1.0) -> (0.0, sin(60), -cos(60)) = (0.0, sqrt(3)/2, -0.5)
second the 45 degree rotation around the y-axis
(0.0, sqrt(3)/2, -0.5) -> (cos(45) * sqrt(3)/2, sin(45) * sqrt(3) / 2.0, -0.5)

this makes the final forward vector
(sqrt(2) * sqrt(3) / 4, sqrt(2) * sqrt(3) / 4, -0.5) = ((3.0 / 8.0)**0.5, (3.0 / 8.0)**0.5, -0.5)

The up vector is similarly calculated.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.isometric_with_billboards
"""

import arcade


PLAYER_WIDTH, PLAYER_HEIGHT = 32, 64

MAP_WIDTH, MAP_HEIGHT = 32, 32
TILE_SIZE = 32

PLAYER_JUMP_SPEED = 300.0
PLAYER_MOVE_SPEED = 200.0
GRAVITY = -800.0


class Isometric(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Isometric")

        # The math required to accurately find the up vector is complex so we just let arcade do it.
        # Though one difference is that we make the up vector sit along the +z axis. This makes sure that
        # the final up vector calculated by arcade is also roughly along the +z axis.
        self.camera_data = arcade.camera.CameraData(
            (0.0, 0.0, 0.0),  # Position
            (0.0, 0.0, 1.0),  # Up
            ((3.0 / 8.0)**0.5, (3.0 / 8.0)**0.5, -0.5),  # Forward
            1.0  # Zoom
        )
        arcade.camera.data_types.constrain_camera_data(self.camera_data, True)
        self.isometric_camera = arcade.camera.OrthographicProjector(view=self.camera_data)

        # Due to the fact that the sprites are now moving into and away from the screen we need to expand
        # the near and far planes as the sprites will get cut off if we don't
        self.isometric_camera.projection.near = -600
        self.isometric_camera.projection.far = 600

        self.player_sprite = arcade.SpriteSolidColor(PLAYER_WIDTH, PLAYER_HEIGHT, color=arcade.color.RADICAL_RED)

        self.player_vertical_velocity = 0.0

        # If the player is
        self.player_on_ground = True

        # Since the isometric perspective rotates the x and y axis we instead care about
        # Moving the player up/down or left/right along the screen.
        self.move_player_ns = 0
        self.move_player_ew = 0

        # By giving the player a shadow it becomes easier to place them in the world.
        # This is a very common trick used by 3D platformers.
        self.player_shadow = arcade.SpriteCircle(PLAYER_WIDTH, color=(0, 0, 0, 124))

        self.billboard_list = arcade.sprite_list.BillboardList()
        self.billboard_list.append(self.player_sprite)

        self.sprite_list = arcade.sprite_list.SpriteList()

        for x_idx in range(-MAP_WIDTH//2, MAP_WIDTH//2):
            for y_idx in range(-MAP_HEIGHT//2, MAP_HEIGHT//2):
                # We add one to the tile size so there is a 1 pixel gap between every tile.
                #
                x = x_idx * (TILE_SIZE + 1)
                y = y_idx * (TILE_SIZE + 1)
                tile = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, x, y, arcade.color.WHITE)
                self.sprite_list.append(tile)
        self.sprite_list.append(self.player_shadow)

    def on_update(self, delta_time: float):
        self.player_vertical_velocity += GRAVITY * delta_time
        self.player_sprite.depth += self.player_vertical_velocity * delta_time
        if self.player_sprite.depth <= 0.0:
            self.player_sprite.depth = 0.0
            self.player_vertical_velocity = 0.0
            self.player_on_ground = True
        else:
            self.player_on_ground = False

        # Because the camera is rotated 45 moving the player's y value doesn't actually represent going up and down
        # the screen. Instead, moving upward on the screen requires increasing both the x and y values.
        # Moving left or right requires increase on axis and decreasing the other.
        move_player_x = self.move_player_ns + self.move_player_ew
        move_player_y = self.move_player_ns - self.move_player_ew

        # We get the move speed so we can scale the final x and y speed. If we didn't it would be faster
        # To move diagonally that horizontally or vertically.
        move_player_speed = (move_player_x**2 + move_player_y**2)**0.5

        if move_player_speed == 0.0:
            move_player_speed = 1.0

        player_x_speed = move_player_x / move_player_speed * PLAYER_MOVE_SPEED * delta_time
        player_y_speed = move_player_y / move_player_speed * PLAYER_MOVE_SPEED * delta_time

        new_player_position = self.player_sprite.center_x + player_x_speed, self.player_sprite.center_y + player_y_speed

        # Because we are working with the center of the player sprite we need to shift the shadow position downwards
        # Normally we would use the bottom value of the player sprite, but because the player is being
        # Billboarded that value is not what is seen on screen. 0.6 was chosen because it looks right.
        new_shadow_position = new_player_position[0] - PLAYER_HEIGHT*0.6, new_player_position[1] - PLAYER_HEIGHT*0.6

        self.player_sprite.position = new_player_position
        self.player_shadow.position = new_shadow_position

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE and self.player_on_ground:
            self.player_vertical_velocity += PLAYER_JUMP_SPEED
        elif symbol == arcade.key.W:
            self.move_player_ns += 1
        elif symbol == arcade.key.S:
            self.move_player_ns += -1
        elif symbol == arcade.key.D:
            self.move_player_ew += 1
        elif symbol == arcade.key.A:
            self.move_player_ew += -1

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.move_player_ns += -1
        elif symbol == arcade.key.S:
            self.move_player_ns += 1
        elif symbol == arcade.key.D:
            self.move_player_ew += -1
        elif symbol == arcade.key.A:
            self.move_player_ew += 1

    def on_draw(self):
        self.clear()
        with self.isometric_camera.activate():
            self.sprite_list.draw()
            self.billboard_list.draw()


def main():
    window = Isometric()
    window.run()


if __name__ == '__main__':
    main()