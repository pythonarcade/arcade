"""
Lasers and Mirrors

A laser shoots from the turret toward the mouse. It stops at the first crate
in its way, bounces off the rotating mirrors, and collects any coins it
touches.

The laser doesn't move like a bullet: it reaches as far as it goes the moment
it's fired. Each straight part of the beam uses arcade.sweep_line() to find
the first sprite in its way. The hit's normal points out of the surface it
hit, which is all a mirror needs to reflect the beam.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_laser_mirrors
"""

import random

from pyglet.math import Vec2

import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Lasers and Mirrors Example"

TURRET_POSITION = Vec2(WINDOW_WIDTH / 2, 40)
# How far the laser reaches, in total, after all its bounces
LASER_RANGE = 3000
MAX_BOUNCES = 20
COIN_COUNT = 12


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_SLATE_GRAY

        self.crates = arcade.SpriteList()
        self.mirrors = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        # Everything the laser can hit, so one sweep_line() call checks them all
        self.obstacles = arcade.SpriteList()

        for x, y in ((250, 300), (1030, 300), (640, 560), (450, 520), (830, 520)):
            crate = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", 0.5, x, y)
            self.crates.append(crate)

        positions = ((300, 150), (980, 150), (640, 350), (200, 620), (1080, 620), (640, 680))
        for i, (x, y) in enumerate(positions):
            mirror = arcade.SpriteSolidColor(8, 110, x, y, arcade.color.LIGHT_CYAN)
            mirror.angle = 45 if i % 2 else -45
            # Degrees per second
            mirror.change_angle = random.choice((-20, -12, 12, 20))
            self.mirrors.append(mirror)

        self.obstacles.extend(self.crates)
        self.obstacles.extend(self.mirrors)
        for _ in range(COIN_COUNT):
            self.add_coin()

        self.aim = Vec2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        # The points the beam passes through, from the turret to where it stops
        self.beam: list[Vec2] = []
        self.score = 0
        self.score_text = arcade.Text("", 10, 10, arcade.color.WHITE, 14)
        self.help_text = arcade.Text(
            "Aim with the mouse. Bounce the laser off the mirrors to collect the coins.",
            10,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            14,
        )

    def add_coin(self):
        """Put a coin somewhere it isn't touching a crate or a mirror"""
        coin = arcade.Sprite(":resources:images/items/coinGold.png", 0.4)
        while True:
            coin.position = random.uniform(60, WINDOW_WIDTH - 60), random.uniform(120, 650)
            if not arcade.check_for_collision_with_list(coin, self.obstacles):
                break
        self.coins.append(coin)
        self.obstacles.append(coin)

    def fire_laser(self):
        """Work out the beam's path, bouncing off mirrors"""
        position = TURRET_POSITION
        direction = (self.aim - TURRET_POSITION).normalize()
        remaining = LASER_RANGE
        self.beam = [position]
        for _ in range(MAX_BOUNCES):
            end = position + direction * remaining
            hit = arcade.sweep_line(position, end, self.obstacles)
            if hit is None:
                self.beam.append(end)
                return
            position = position + direction * hit.distance
            self.beam.append(position)
            remaining -= hit.distance

            if hit.sprite in self.coins:
                # Coins are collected, and the beam goes on
                hit.sprite.remove_from_sprite_lists()
                self.score += 1
                self.add_coin()
            elif hit.sprite in self.mirrors:
                # Reflect off the mirror's surface
                direction = direction - 2 * direction.dot(hit.normal) * hit.normal
            else:
                # Crates stop the beam
                return

            # Start the next part just off the surface, so rounding can't
            # leave it inside the sprite it just hit
            position = position + direction * 0.01

    def on_update(self, delta_time):
        for mirror in self.mirrors:
            mirror.angle += mirror.change_angle * delta_time
        self.fire_laser()
        self.score_text.text = f"Coins: {self.score}"

    def on_draw(self):
        self.clear()
        self.crates.draw()
        self.mirrors.draw()
        self.coins.draw()

        # A wide, faint line under a thin, bright one looks like a glow
        if len(self.beam) > 1:
            arcade.draw_line_strip(self.beam, (255, 60, 60, 90), 9)
            arcade.draw_line_strip(self.beam, arcade.color.WHITE, 2)
        arcade.draw_circle_filled(*TURRET_POSITION, 18, arcade.color.GRAY)

        self.score_text.draw()
        self.help_text.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        # Only aim upward, away from the turret's base
        self.aim = Vec2(x, max(y, TURRET_POSITION.y + 1))


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.show_view(GameView())
    arcade.run()


if __name__ == "__main__":
    main()
