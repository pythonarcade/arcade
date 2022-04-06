"""
Rotating Sprites Around Points

A simple program to show how someone could implement sprites rotating around points.

Artwork from https://kenney.nl
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Rotating Sprite Example"


class RotatingSprite(arcade.Sprite):

    def rotate_around_point(self, point, degrees, change_angle=True):
        """
        rotates the sprite around a defined point by the set amount of degrees
        """

        if change_angle:
            # This is so the direction the sprite faces changes when rotating.
            # It isn't necessary to have this. For example, you would want a rotating platform to always face upwards.
            self.angle += degrees

        # use arcade.rotate_point to rotate the sprites center x and y by the point.
        self.center_x, self.center_y = arcade.rotate_point(self.center_x, self.center_y, point[0], point[1], degrees)


class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # This first example is similar to the spinning fireballs from mario.
        self.example_sprite_1 = RotatingSprite(":resources:images/space_shooter/laserBlue01.png",
                                               center_x=SCREEN_WIDTH // 4 + 26, center_y=SCREEN_HEIGHT // 2)

        # This second example shows how the method can be use to make rotating platforms.
        self.example_sprite_2 = RotatingSprite(":resources:images/tiles/grassHalf.png", scale=0.25,
                                               center_x=3 * SCREEN_WIDTH // 4 + 50, center_y=SCREEN_HEIGHT // 2)

        self.base_sprite_1 = arcade.Sprite(":resources:images/tiles/boxCrate.png", scale=0.25,
                                           center_x=SCREEN_WIDTH // 4, center_y=SCREEN_HEIGHT // 2)
        self.base_sprite_2 = arcade.Sprite(":resources:images/tiles/boxCrate.png", scale=0.25,
                                           center_x=3 * SCREEN_WIDTH // 4, center_y=SCREEN_HEIGHT // 2)

        self.sprites = arcade.SpriteList()
        self.sprites.extend([self.base_sprite_1, self.example_sprite_1, self.base_sprite_2, self.example_sprite_2])

    def on_update(self, delta_time: float):
        # Rotate the first sprite and change its angle
        self.example_sprite_1.rotate_around_point((self.base_sprite_1.center_x, self.base_sprite_1.center_y),
                                                  120 * delta_time)

        # Rotate the second sprite but don't change its angle
        self.example_sprite_2.rotate_around_point((self.base_sprite_2.center_x, self.base_sprite_2.center_y),
                                                  60 * delta_time, False)

    def on_draw(self):
        # Draw the sprite list.
        self.clear()
        self.sprites.draw()


if __name__ == '__main__':
    window = ExampleWindow()
    window.run()
