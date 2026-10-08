"""
Fast Bullets and Thin Walls

Lasers move so far each frame that they can jump right over a thin wall.

In the top lane, each laser moves and then checks for a collision with
arcade.check_for_collision_with_list(). A laser that lands on the far side
of a wall never overlaps it, so many pass straight through.

In the bottom lane, each laser uses arcade.sweep_sprite() to check its
whole path before it moves, so it always stops at the first wall.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_sweep
"""

import random

import arcade
from pyglet.math import Vec2

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Fast Bullets and Thin Walls Example"

# Pixels per frame. Much more than a wall plus a laser is wide.
LASER_SPEED = 80
LASER_SCALE = 0.5
# Fire a laser in each lane this often, in frames
FIRE_INTERVAL = 4

WALL_WIDTH = 6
WALL_X_POSITIONS = (500, 760, 1020)

# Each lane is (bottom, top)
TOP_LANE = (390, 640)
BOTTOM_LANE = (40, 290)


class Lane:
    """One lane of walls and lasers, and its counts."""

    def __init__(self, bottom: int, top: int, use_sweep: bool):
        self.bottom = bottom
        self.top = top
        self.use_sweep = use_sweep
        self.hits = 0
        self.passed = 0

        self.walls: arcade.SpriteList[arcade.SpriteSolidColor] = arcade.SpriteList()
        for x in WALL_X_POSITIONS:
            wall = arcade.SpriteSolidColor(
                WALL_WIDTH,
                top - bottom,
                center_x=x,
                center_y=(bottom + top) / 2,
                color=arcade.color.LIGHT_GRAY,
            )
            self.walls.append(wall)

        self.lasers: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()

    def fire(self):
        """Add a laser at the left edge, at a random height."""
        laser = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", scale=LASER_SCALE)
        # A random start, so lasers don't all land on the same spots
        x = random.uniform(0, LASER_SPEED)
        laser.position = x, random.uniform(self.bottom + 10, self.top - 10)
        laser.change_x = LASER_SPEED
        self.lasers.append(laser)

    def update(self, sparks: arcade.SpriteList):
        """Move the lasers, removing any that hit a wall or leave the screen."""
        for laser in list(self.lasers):
            move = Vec2(laser.change_x, laser.change_y)
            if self.use_sweep:
                # Check the whole path before moving
                hit = arcade.sweep_sprite(laser, move.x, move.y, self.walls)
                if hit:
                    laser.position += move * hit.fraction
                    self.hit(laser, laser.right, sparks)
                    continue
                laser.position += move
            else:
                # Move, then check where the laser ended up
                laser.position += move
                if arcade.check_for_collision_with_list(laser, self.walls):
                    self.hit(laser, laser.center_x, sparks)
                    continue

            if laser.left > WINDOW_WIDTH:
                self.passed += 1
                laser.remove_from_sprite_lists()

    def hit(self, laser: arcade.Sprite, x: float, sparks: arcade.SpriteList):
        """Remove a laser that hit a wall, leaving a spark where it hit."""
        self.hits += 1
        spark = arcade.SpriteCircle(5, arcade.color.ORANGE_RED)
        spark.position = x, laser.center_y
        sparks.append(spark)
        laser.remove_from_sprite_lists()


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_MIDNIGHT_BLUE
        self.lanes = [
            Lane(*TOP_LANE, use_sweep=False),
            Lane(*BOTTOM_LANE, use_sweep=True),
        ]
        self.sparks = arcade.SpriteList()
        self.frame = 0

        self.titles = [
            arcade.Text(
                "check_for_collision_with_list() after moving: lasers can pass through",
                20,
                TOP_LANE[1] + 30,
                arcade.color.WHITE,
                16,
            ),
            arcade.Text(
                "sweep_sprite() before moving: every laser hits the first wall",
                20,
                BOTTOM_LANE[1] + 30,
                arcade.color.WHITE,
                16,
            ),
        ]
        self.counts = [
            arcade.Text("", 20, TOP_LANE[1] + 6, arcade.color.LIGHT_GRAY, 12),
            arcade.Text("", 20, BOTTOM_LANE[1] + 6, arcade.color.LIGHT_GRAY, 12),
        ]

    def on_update(self, delta_time):
        """Movement and game logic"""
        self.frame += 1
        for lane in self.lanes:
            if self.frame % FIRE_INTERVAL == 0:
                lane.fire()
            lane.update(self.sparks)

        # Fade the sparks out
        for spark in list(self.sparks):
            spark.alpha = max(0, spark.alpha - 8)
            if spark.alpha == 0:
                spark.remove_from_sprite_lists()

        for lane, text in zip(self.lanes, self.counts):
            text.text = f"Hit a wall: {lane.hits}    Passed through every wall: {lane.passed}"

    def on_draw(self):
        """Render the screen."""
        self.clear()
        for lane in self.lanes:
            lane.walls.draw()
            lane.lasers.draw()
        self.sparks.draw()
        for text in self.titles + self.counts:
            text.draw()


def main():
    """Main function"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.show_view(GameView())
    arcade.run()


if __name__ == "__main__":
    main()
