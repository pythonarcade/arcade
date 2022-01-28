"""
Show how to have enemies shoot bullets at regular intervals.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_periodic
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprites and Periodic Bullets Example"


class EnemySprite(arcade.Sprite):
    """ Enemy ship class that tracks how long it has been since firing. """

    def __init__(self, image_file, scale, bullet_list, time_between_firing):
        """ Set up the enemy """
        super().__init__(image_file, scale)

        # How long has it been since we last fired?
        self.time_since_last_firing = 0.0

        # How often do we fire?
        self.time_between_firing = time_between_firing

        # When we fire, what list tracks the bullets?
        self.bullet_list = bullet_list

    def on_update(self, delta_time: float = 1 / 60):
        """ Update this sprite. """

        # Track time since we last fired
        self.time_since_last_firing += delta_time

        # If we are past the firing time, then fire
        if self.time_since_last_firing >= self.time_between_firing:

            # Reset timer
            self.time_since_last_firing = 0

            # Fire the bullet
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
            bullet.center_x = self.center_x
            bullet.angle = -90
            bullet.top = self.bottom
            bullet.change_y = -2
            self.bullet_list.append(bullet)


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

        self.player = None
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None

    def setup(self):
        """ Setup the variables for the game. """

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Add player ship
        self.player = arcade.Sprite(":resources:images/space_shooter/playerShip1_orange.png", 0.5)
        self.player_list.append(self.player)

        # Add top-left enemy ship
        enemy = EnemySprite(":resources:images/space_shooter/playerShip1_green.png",
                            scale=0.5,
                            bullet_list=self.bullet_list,
                            time_between_firing=2.0)
        enemy.center_x = 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

        # Add top-right enemy ship
        enemy = EnemySprite(":resources:images/space_shooter/playerShip1_green.png",
                            scale=0.5,
                            bullet_list=self.bullet_list,
                            time_between_firing=1.0)
        enemy.center_x = SCREEN_WIDTH - 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

    def on_draw(self):
        """Render the screen. """

        self.clear()

        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """

        # Call on_update for each enemy in  the list
        self.enemy_list.on_update(delta_time)

        # Get rid of the bullet when it flies off-screen
        for bullet in self.bullet_list:
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        self.bullet_list.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        self.player.center_x = x
        self.player.center_y = 20


def main():
    """ Run the game """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
