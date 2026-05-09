"""
Easing Example 2

Demonstrate angle and position easing on a ship sprite that turns and moves
toward the mouse cursor.  Press number keys to switch between modes:

- **1**: Instant angle (no easing)
- **2-5**: Angle easing (LINEAR, QUAD_IN, QUAD_OUT, SINE)
- **6-9**: Position easing (LINEAR, QUAD_IN, QUAD_OUT, SINE)

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.easing_example_2
"""

import math
import arcade
from arcade.anim import ease, Easing

# --- Constants ---
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Easing Example 2"

SHIP_SPEED = 5.0
EASE_DURATION = 1.0

# Mode descriptions shown in the HUD.
MODE_DESCRIPTIONS = {
    1: "Instant (teleport + face mouse)",
    2: "Angle ease: LINEAR",
    3: "Angle ease: QUAD_IN",
    4: "Angle ease: QUAD_OUT",
    5: "Angle ease: SINE",
    6: "Position ease: LINEAR",
    7: "Position ease: QUAD_IN",
    8: "Position ease: QUAD_OUT",
    9: "Position ease: SINE",
}

# Mapping from mode number to easing function (modes 2-9).
MODE_EASING = {
    2: Easing.LINEAR,
    3: Easing.QUAD_IN,
    4: Easing.QUAD_OUT,
    5: Easing.SINE,
    6: Easing.LINEAR,
    7: Easing.QUAD_IN,
    8: Easing.QUAD_OUT,
    9: Easing.SINE,
}


def shortest_angle_delta(from_angle: float, to_angle: float) -> float:
    """Return the shortest signed rotation from *from_angle* to *to_angle*.

    Both angles are in degrees.  The result is in the range (-180, 180].
    """
    delta = (to_angle - from_angle) % 360
    if delta > 180:
        delta -= 360
    return delta


class GameView(arcade.View):
    """Main view with a ship that eases toward the mouse."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK

        self.ship_sprite: arcade.Sprite | None = None
        self.mode = 1
        self.time_elapsed = 0.0

        # Mouse target
        self.target_x = WINDOW_WIDTH / 2
        self.target_y = WINDOW_HEIGHT / 2

        # Angle easing state
        self.angle_start = 0.0
        self.angle_end = 0.0
        self.angle_ease_start_time = 0.0

        # Position easing state
        self.pos_start_x = WINDOW_WIDTH / 2
        self.pos_start_y = WINDOW_HEIGHT / 2
        self.pos_end_x = WINDOW_WIDTH / 2
        self.pos_end_y = WINDOW_HEIGHT / 2
        self.pos_ease_start_time = 0.0

    def setup(self):
        """Set up the game."""
        self.ship_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png",
            scale=0.5,
        )
        self.ship_sprite.center_x = WINDOW_WIDTH / 2
        self.ship_sprite.center_y = WINDOW_HEIGHT / 2
        self.time_elapsed = 0.0

    def on_draw(self):
        """Render the scene."""
        self.clear()

        # Draw the ship
        arcade.draw_sprite(self.ship_sprite)

        # Draw a crosshair at the target
        arcade.draw_circle_outline(
            self.target_x, self.target_y, 10, arcade.color.RED, 2,
        )

        # HUD
        description = MODE_DESCRIPTIONS.get(self.mode, "")
        arcade.draw_text(
            f"Mode {self.mode}: {description}",
            10, WINDOW_HEIGHT - 30,
            color=arcade.color.WHITE,
            font_size=16,
        )
        arcade.draw_text(
            "Press 1-9 to change mode.  Click to set target.",
            10, WINDOW_HEIGHT - 55,
            color=arcade.color.GRAY,
            font_size=12,
        )

    def _target_angle(self) -> float:
        """Compute the angle from the ship to the target in degrees.

        Arcade uses clockwise-positive angles and the ship sprite
        points up at angle 0, so we negate atan2 and add 90.
        """
        diff_x = self.target_x - self.ship_sprite.center_x
        diff_y = self.target_y - self.ship_sprite.center_y
        return -math.degrees(math.atan2(diff_y, diff_x)) + 90

    def _start_angle_ease(self):
        """Record the current angle as the start and set up the ease."""
        self.angle_start = self.ship_sprite.angle
        target = self._target_angle()
        delta = shortest_angle_delta(self.angle_start, target)
        self.angle_end = self.angle_start + delta
        self.angle_ease_start_time = self.time_elapsed

    def _start_position_ease(self):
        """Record the current position as the start and set up the ease."""
        self.pos_start_x = self.ship_sprite.center_x
        self.pos_start_y = self.ship_sprite.center_y
        self.pos_end_x = self.target_x
        self.pos_end_y = self.target_y
        self.pos_ease_start_time = self.time_elapsed

    def on_update(self, delta_time: float):
        """Update ship angle and/or position based on current mode."""
        self.time_elapsed += delta_time
        ease_func = MODE_EASING.get(self.mode)

        if self.mode == 1:
            # Instant angle — always face the target directly
            self.ship_sprite.angle = self._target_angle()

        elif 2 <= self.mode <= 5:
            # Angle easing
            eased_angle = ease(
                self.angle_start, self.angle_end,
                self.angle_ease_start_time,
                self.angle_ease_start_time + EASE_DURATION,
                self.time_elapsed,
                func=ease_func,
            )
            self.ship_sprite.angle = eased_angle

        elif 6 <= self.mode <= 9:
            # Position easing — also face the target instantly
            self.ship_sprite.angle = self._target_angle()

            eased_x = ease(
                self.pos_start_x, self.pos_end_x,
                self.pos_ease_start_time,
                self.pos_ease_start_time + EASE_DURATION,
                self.time_elapsed,
                func=ease_func,
            )
            eased_y = ease(
                self.pos_start_y, self.pos_end_y,
                self.pos_ease_start_time,
                self.pos_ease_start_time + EASE_DURATION,
                self.time_elapsed,
                func=ease_func,
            )
            self.ship_sprite.center_x = eased_x
            self.ship_sprite.center_y = eased_y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Set a new target and begin an easing animation."""
        self.target_x = x
        self.target_y = y

        if self.mode == 1:
            self.ship_sprite.center_x = x
            self.ship_sprite.center_y = y
        elif 2 <= self.mode <= 5:
            self._start_angle_ease()
        elif 6 <= self.mode <= 9:
            self._start_position_ease()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Update target for instant-angle mode."""
        if self.mode == 1:
            self.target_x = x
            self.target_y = y

    def on_key_press(self, key: int, modifiers: int):
        """Switch modes with number keys 1-9."""
        key_map = {
            arcade.key.KEY_1: 1, arcade.key.KEY_2: 2, arcade.key.KEY_3: 3,
            arcade.key.KEY_4: 4, arcade.key.KEY_5: 5, arcade.key.KEY_6: 6,
            arcade.key.KEY_7: 7, arcade.key.KEY_8: 8, arcade.key.KEY_9: 9,
        }
        new_mode = key_map.get(key)
        if new_mode is not None:
            self.mode = new_mode
            if 2 <= new_mode <= 5:
                self._start_angle_ease()
            elif 6 <= new_mode <= 9:
                self._start_position_ease()


def main():
    """Main function."""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
