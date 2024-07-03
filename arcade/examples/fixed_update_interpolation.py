"""
Interpolate a sprite's motion which is calculated in fixed update.

The bouncing done in this example is very bare-bones, and unstable.
The fixed update has been slowed down to highlight the value of interpolation,
the fixed update should be kept close to the nominal update rate, or even faster.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.fixed_update_interpolation.py
"""
import arcade

# --- Constants ---
GRAVITY = 98.1  # 98.1 px per second
CIRCLE_RADIUS = 30

SCREEN_WIDTH = 1289
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Sprite Follow Path Simple Example"


class Game(arcade.Window):

    def __init__(self):
        super().__init__(fixed_rate=1/120.0)
        self.unfixed_sprite = arcade.SpriteCircle(CIRCLE_RADIUS, arcade.color.RADICAL_RED)
        self.interpolated_sprite = arcade.SpriteCircle(CIRCLE_RADIUS, arcade.color.ORANGE)
        self.fixed_sprite = arcade.SpriteCircle(CIRCLE_RADIUS, arcade.color.GOLD)

        # We store the last position of the fixed sprite to find the interpolated sprite's position
        self.last_position = 0.0

        self.sprites = arcade.SpriteList()
        self.sprites.extend((self.unfixed_sprite, self.fixed_sprite, self.interpolated_sprite))

    def setup(self):
        self.unfixed_sprite.change_y = self.fixed_sprite.change_y = self.interpolated_sprite.change_y = 0.0

        self.unfixed_sprite.position = SCREEN_WIDTH / 4.0, SCREEN_HEIGHT / 2.0
        self.interpolated_sprite.position = 2.0 * SCREEN_WIDTH / 4.0, SCREEN_HEIGHT / 2.0
        self.fixed_sprite.position = 3.0 * SCREEN_WIDTH / 4.0, SCREEN_HEIGHT / 2.0

        self.last_position = self.fixed_sprite.center_y

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.setup()

    def on_fixed_update(self, delta_time: float):
        # Accelerate the sprite downward due to gravity
        self.fixed_sprite.change_y -= GRAVITY * delta_time

        # If the sprite is colliding with the ground then make it 'bounce' by flipping it's velocity
        if self.fixed_sprite.center_y <= CIRCLE_RADIUS and self.fixed_sprite.change_y <= 0.0:
            self.fixed_sprite.change_y *= -1

        # Move the sprite based on its velocity
        self.last_position = self.fixed_sprite.center_y
        self.fixed_sprite.center_y += self.fixed_sprite.change_y * delta_time

    def on_update(self, delta_time: float):
        # Accelerate the sprite downward due to gravity
        self.unfixed_sprite.change_y -= GRAVITY * delta_time

        # If the sprite is colliding with the ground then make it 'bounce' by flipping it's velocity
        if self.unfixed_sprite.center_y <= CIRCLE_RADIUS and self.unfixed_sprite.change_y <= 0.0:
            self.unfixed_sprite.change_y *= -1

        # Move the sprite based on its velocity
        self.unfixed_sprite.center_y += self.unfixed_sprite.change_y * delta_time

        self.interpolated_sprite.center_y = arcade.math.lerp(
            self.last_position, self.fixed_sprite.center_y, self.global_fixed_clock.fraction
        )

    def on_draw(self):
        self.clear()
        self.sprites.draw()


def main():
    win = Game()
    win.setup()
    win.run()


if __name__ == '__main__':
    main()
