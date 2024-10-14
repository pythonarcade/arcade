"""
Show how to have enemies shoot bullets aimed at the player.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_enemy_aims
"""

import arcade
import math

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprites and Bullets Enemy Aims Example"
BULLET_SPEED = 4


class GameView(arcade.View):
    """ Main application class """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK

        self.frame_count = 0

        self.enemy_list = None
        self.bullet_list = None
        self.player_list = None
        self.player = None

    def setup(self):
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Add player ship
        self.player = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png",
            scale=0.5,
        )
        self.player_list.append(self.player)

        # Add top-left enemy ship
        enemy = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_green.png",
            scale=0.5,
        )
        enemy.center_x = 120
        enemy.center_y = WINDOW_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

        # Add top-right enemy ship
        enemy = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_green.png",
            scale=0.5,
        )
        enemy.center_x = WINDOW_WIDTH - 120
        enemy.center_y = WINDOW_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

    def on_draw(self):
        """Render the screen. """

        self.clear()

        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        """All the logic to move, and the game logic goes here. """

        self.frame_count += 1

        # Loop through each enemy that we have
        for enemy in self.enemy_list:

            # First, calculate the angle to the player. We could do this
            # only when the bullet fires, but in this case we will rotate
            # the enemy to face the player each frame, so we'll do this
            # each frame.

            # Position the start at the enemy's current location
            start_x = enemy.center_x
            start_y = enemy.center_y

            # Get the destination location for the bullet
            dest_x = self.player.center_x
            dest_y = self.player.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = -math.atan2(y_diff, x_diff) + 3.14 / 2

            # Set the enemy to face the player.
            enemy.angle = math.degrees(angle)

            # Shoot every 60 frames change of shooting each frame
            if self.frame_count % 60 == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = start_x
                bullet.center_y = start_y

                # Angle the bullet sprite
                bullet.angle = math.degrees(angle) - 90

                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the bullet travels.
                bullet.change_x = math.sin(angle) * BULLET_SPEED
                bullet.change_y = math.cos(angle) * BULLET_SPEED

                self.bullet_list.append(bullet)

        # Get rid of the bullet when it flies off-screen
        for bullet in self.bullet_list:
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        self.bullet_list.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """Called whenever the mouse moves. """
        self.player.position = x, y


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
