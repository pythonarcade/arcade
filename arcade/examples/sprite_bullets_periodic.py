"""
Show how to have enemies shoot bullets at regular intervals.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_periodic
"""
import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprites and Periodic Bullets Example"


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.BLACK)

        # --- Keep track of a frame count.
        # --- This is important for doing things every x frames
        self.frame_count = 0

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Add player ship
        self.player = arcade.Sprite("images/playerShip1_orange.png", 0.5)
        self.player_list.append(self.player)

        # Add top-left enemy ship
        enemy = arcade.Sprite("images/playerShip1_green.png", 0.5)
        enemy.center_x = 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

        # Add top-right enemy ship
        enemy = arcade.Sprite("images/playerShip1_green.png", 0.5)
        enemy.center_x = SCREEN_WIDTH - 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)

    def on_draw(self):
        """Render the screen. """

        arcade.start_render()

        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

    def update(self, delta_time):
        """All the logic to move, and the game logic goes here. """

        # --- Add one to the frame count
        self.frame_count += 1

        # Loop through each enemy that we have
        for enemy in self.enemy_list:

            # --- Use the modulus to trigger doing something every 120 frames
            if self.frame_count % 120 == 0:
                bullet = arcade.Sprite("images/laserBlue01.png")
                bullet.center_x = enemy.center_x
                bullet.angle = -90
                bullet.top = enemy.bottom
                bullet.change_y = -2
                self.bullet_list.append(bullet)

        # Get rid of the bullet when it flies off-screen
        for bullet in self.bullet_list:
            if bullet.top < 0:
                bullet.kill()

        self.bullet_list.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        self.player.center_x = x
        self.player.center_y = 20


def main():
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
