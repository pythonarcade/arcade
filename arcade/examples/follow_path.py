"""
Sprite Follow Path

This example has enemy sprites follow a set path.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.follow_path
"""

import arcade
import math

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_ENEMY = 0.5
ENEMY_SPEED = 5.0

WINDOW_WIDTH = 1289
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Follow Path Simple Example"


class Enemy(arcade.Sprite):
    """
    This class represents the Enemy on our screen.
    """

    def __init__(self, image, scale, position_list):
        super().__init__(image, scale=scale)
        self.position_list = position_list
        self.cur_position = 0
        self.speed = ENEMY_SPEED

    def update(self, delta_time: float = 1 / 60):
        """Have a sprite follow a path"""
        # Where are we
        start_x = self.center_x
        start_y = self.center_y

        # Where are we going
        dest_x = self.position_list[self.cur_position][0]
        dest_y = self.position_list[self.cur_position][1]

        # X and Y diff between the two
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y

        # Calculate angle to get there
        angle = math.atan2(y_diff, x_diff)

        # How far are we?
        distance = math.sqrt((self.center_x - dest_x) ** 2 + (self.center_y - dest_y) ** 2)

        # How fast should we go? If we are close to our destination,
        # lower our speed so we don't overshoot.
        speed = min(self.speed, distance)

        # Calculate vector to travel
        change_x = math.cos(angle) * speed
        change_y = math.sin(angle) * speed

        # Update our location
        self.center_x += change_x
        self.center_y += change_y

        # How far are we?
        distance = math.sqrt((self.center_x - dest_x) ** 2 + (self.center_y - dest_y) ** 2)

        # If we are there, head to the next point.
        if distance <= self.speed:
            self.cur_position += 1

            # Reached the end of the list, start over.
            if self.cur_position >= len(self.position_list):
                self.cur_position = 0


class GameView(arcade.View):

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None
        self.enemy_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Score
        self.score = 0

        # Set up the player
        # Character image from kenney.nl
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # List of points the enemy will travel too.
        position_list = [
            [50, 50],
            [self.width - 50, 50],
            [self.width - 50, self.height - 50],
            [50, self.height - 50],
        ]
        # Spawn a few enemies
        self.spawn_enemy((50, 50), position_list)
        self.spawn_enemy((50, 250), position_list)
        self.spawn_enemy((50, 450), position_list)
        self.spawn_enemy((50, 650), position_list)

    def spawn_enemy(self, position, position_list):
        # Spawn a new enemy
        enemy = Enemy(":resources:images/animated_characters/robot/robot_idle.png",
                      SPRITE_SCALING_ENEMY,
                      position_list)
        # Set initial location of the enemy at the first point
        enemy.position = position
        self.enemy_list.append(enemy)

    def on_draw(self):
        """ Draw everything """
        self.clear()
        self.enemy_list.draw()
        self.player_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.enemy_list.update()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.close()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
