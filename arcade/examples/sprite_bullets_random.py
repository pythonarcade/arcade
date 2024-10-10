"""
Show how to have enemies shoot bullets at random intervals.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_random
"""
import arcade
import random

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprites and Random Bullets Example"


class GameView(arcade.View):
    """ Main application class """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK

        self.frame_count = 0
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None

        self.player = None

    def setup(self):
        """ Setup the variables for the game. """
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

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

        # Loop through each enemy that we have
        for enemy in self.enemy_list:

            # Have a random 1 in 200 change of shooting each 1/60th of a second
            odds = 200

            # Adjust odds based on delta-time
            adj_odds = int(odds * (1 / 60) / delta_time)

            if random.randrange(adj_odds) == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = enemy.center_x
                bullet.angle = 90
                bullet.top = enemy.bottom
                bullet.change_y = -2
                self.bullet_list.append(bullet)

        # Get rid of the bullet when it flies off-screen
        for bullet in self.bullet_list:
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        self.bullet_list.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Called whenever the mouse moves. """
        self.player.center_x = x
        self.player.center_y = 20


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
