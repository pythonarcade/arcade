"""
Rotating Sprites Around Points

Two minimal examples demonstrating how to rotate sprites around points
and how you might apply them in a game.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_rotate_around_point
"""
import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
QUARTER_WIDTH = SCREEN_WIDTH // 4
HALF_HEIGHT = SCREEN_HEIGHT // 2


SCREEN_TITLE = "Rotating Sprites Around Points"


class RotatingSprite(arcade.Sprite):
    """
    This sprite subclass implements a generic rotate_around_point method.
    """

    def rotate_around_point(self, point, degrees, change_angle=True):
        """
        Rotate the sprite around a point by the set amount of degrees

        You could remove the change_angle keyword and/or angle change
        if you know that sprites will always or never change angle.

        :param point: The point that the sprite will rotate about
        :param degrees: How many degrees to rotate the sprite
        :param change_angle: Whether the sprite's angle should also be adjusted.
        """

        # If changle_angle is true, change the sprite's angle
        if change_angle:
            self.angle += degrees

        # Move the sprite along a circle centered on the point by degrees 
        self.position = arcade.rotate_point(
            self.center_x, self.center_y,
            point[0], point[1], degrees)


class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.sprites = arcade.SpriteList()

        # This example is based off spinning lines of fire from Mario games
        # See https://www.mariowiki.com/Fire_Bar for more information
        self.left_rotating_laser_sprite = RotatingSprite(
            ":resources:images/space_shooter/laserBlue01.png",
            center_x=QUARTER_WIDTH + 26, center_y=HALF_HEIGHT)

        self.laser_base_sprite = arcade.Sprite(
            ":resources:images/tiles/boxCrate.png", scale=0.25,
            center_x=QUARTER_WIDTH, center_y=HALF_HEIGHT)

        self.laser_text = arcade.Text(
            "change_angle = True",
            QUARTER_WIDTH, SCREEN_HEIGHT // 2 - 150,
            anchor_x='center')

        # This example demonstrates how to make platforms rotate around a point
        self.right_rotating_platform_sprite = RotatingSprite(
            ":resources:images/tiles/grassHalf.png", scale=0.25,
            center_x=3 * QUARTER_WIDTH + 50, center_y=HALF_HEIGHT)

        self.platform_base_sprite = arcade.Sprite(
            ":resources:images/tiles/boxCrate.png", scale=0.25,
            center_x=3 * QUARTER_WIDTH, center_y=HALF_HEIGHT)

        self.platform_text = arcade.Text(
            "change_angle = False",
            3 * QUARTER_WIDTH, HALF_HEIGHT - 150,
            anchor_x='center')

        self.sprites.extend([
            self.laser_base_sprite,
            self.left_rotating_laser_sprite,
            self.platform_base_sprite,
            self.right_rotating_platform_sprite])

    def on_update(self, delta_time: float):
        # Rotate the laser sprite and change its angle
        self.left_rotating_laser_sprite.rotate_around_point(
            self.laser_base_sprite.position,
            120 * delta_time)

        # Rotate the platform sprite but don't change its angle
        self.right_rotating_platform_sprite.rotate_around_point(
            self.platform_base_sprite.position,
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
