"""
Rotating Sprites Around Points

A simple program to show how someone could implement sprites rotating around points.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_rotate_around_point
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Rotating Sprite Example"


class RotatingSprite(arcade.Sprite):
    """
    This is an example sprite subclass which implements a generic rotate_around_point method.

    The change_angle keyword could be removed if you know that sprites will always / never change angle.
    """
    def rotate_around_point(self, point, degrees, change_angle=True):
        """
        Rotates the sprite around a point by the set amount of degrees

        :param point: The point that the sprite will rotate about
        :param degrees: How many degrees to rotate the sprite
        :param change_angle: whether the sprite's angle should also be adjusted.
        """

        if change_angle:
            # This is so the direction the sprite faces changes when rotating.
            self.angle += degrees

        # use arcade.rotate_point to rotate the sprites center x and y by the point.
        self.position = arcade.rotate_point(self.center_x, self.center_y, point[0], point[1], degrees)


class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # The first example is similar to the spinning lines of fireballs from the Super Mario series
        # See https://www.mariowiki.com/Fire_Bar for more information
        self.left_rotating_laser_sprite = RotatingSprite(":resources:images/space_shooter/laserBlue01.png",
                                                         center_x=SCREEN_WIDTH // 4 + 26, center_y=SCREEN_HEIGHT // 2)

        # This second example shows how the method can be used to make rotating platforms.
        self.right_rotating_platform_sprite = RotatingSprite(":resources:images/tiles/grassHalf.png", scale=0.25,
                                                             center_x=3 * SCREEN_WIDTH // 4 + 50,
                                                             center_y=SCREEN_HEIGHT // 2)

        self.laser_base_sprite = arcade.Sprite(":resources:images/tiles/boxCrate.png", scale=0.25,
                                               center_x=SCREEN_WIDTH // 4, center_y=SCREEN_HEIGHT // 2)
        self.platform_base_sprite = arcade.Sprite(":resources:images/tiles/boxCrate.png", scale=0.25,
                                                  center_x=3 * SCREEN_WIDTH // 4, center_y=SCREEN_HEIGHT // 2)

        self.sprites = arcade.SpriteList()
        self.sprites.extend([self.laser_base_sprite, self.left_rotating_laser_sprite,
                             self.platform_base_sprite, self.right_rotating_platform_sprite])

        self.laser_text = arcade.Text("change_angle = True", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 150,
                                      anchor_x='center')
        self.platform_text = arcade.Text("change_angle = False", 3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 150,
                                         anchor_x='center')

    def on_update(self, delta_time: float):
        # Rotate the laser sprite and change its angle
        self.left_rotating_laser_sprite.rotate_around_point((self.laser_base_sprite.center_x,
                                                             self.laser_base_sprite.center_y),
                                                            120 * delta_time)

        # Rotate the platform sprite but don't change its angle
        self.right_rotating_platform_sprite.rotate_around_point((self.platform_base_sprite.center_x,
                                                                 self.platform_base_sprite.center_y),
                                                                60 * delta_time, False)

    def on_draw(self):
        # Draw the sprite list.
        self.clear()
        self.sprites.draw()

        self.laser_text.draw()
        self.platform_text.draw()


def main():
    window = ExampleWindow()
    window.run()


if __name__ == '__main__':
    main()
