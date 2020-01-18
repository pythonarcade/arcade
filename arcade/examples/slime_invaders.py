"""
Slime Invaders

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.slime_invaders
"""
import random
import arcade
import os

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_enemy = 0.5
SPRITE_SCALING_LASER = 0.8
enemy_COUNT = 50

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Slime Invaders"

BULLET_SPEED = 5
ENEMY_SPEED = 2

ENEMY_VERTICAL_MARGIN = 20
RIGHT_ENEMY_BORDER = SCREEN_WIDTH - ENEMY_VERTICAL_MARGIN
LEFT_ENEMY_BORDER = ENEMY_VERTICAL_MARGIN

ENEMY_MOVE_DOWN_AMOUNT = 30

GAME_OVER = 1
PLAY_GAME = 0

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None

        self.enemy_textures = None

        self.game_state = PLAY_GAME

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Enemy movement
        self.enemy_change_x = -ENEMY_SPEED

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

        arcade.set_background_color(arcade.color.AMAZON)

    def setup_level_one(self):
        # Load the textures for the enemies, one facing left, one right
        self.enemy_textures = []
        texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png", mirrored=True, scale=SPRITE_SCALING_enemy)
        self.enemy_textures.append(texture)
        texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png", scale=SPRITE_SCALING_enemy)
        self.enemy_textures.append(texture)

        # Create rows and columns of enemies
        x_start = 380
        x_spacing = 60
        x_count = 7
        y_start = 420
        y_spacing = 40
        y_count = 5
        for x in range(x_start, x_spacing * x_count + x_start, x_spacing):
            for y in range(y_start, y_spacing * y_count + y_start, y_spacing):

                # Create the enemy instance
                # enemy image from kenney.nl
                enemy = arcade.Sprite()
                enemy.texture = self.enemy_textures[1]

                # Position the enemy
                enemy.center_x = x
                enemy.center_y = y

                # Add the enemy to the lists
                self.enemy_list.append(enemy)

    def make_shield(self, x_start):
        """ Make a shield """
        shield_block_width = 5
        shield_block_height = 10
        shield_width_count = 20
        shield_height_count = 5
        y_start = 150
        for x in range(x_start, x_start + shield_width_count * shield_block_width, shield_block_width):
            for y in range(y_start, y_start + shield_height_count * shield_block_height, shield_block_height):
                shield_sprite = arcade.SpriteSolidColor(shield_block_width, shield_block_height, arcade.color.WHITE)
                shield_sprite.center_x = x
                shield_sprite.center_y = y
                self.shield_list.append(shield_sprite)

    def setup(self):
        """ Set up the game and initialize the variables. """

        self.game_state = PLAY_GAME

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        # Set up the player
        self.score = 0

        # Image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 40
        self.player_list.append(self.player_sprite)

        for x in range(75, 800, 190):
            self.make_shield(x)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.setup_level_one()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()
        self.player_list.draw()

        # Render the text
        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        if self.game_state == GAME_OVER:
            return

        self.player_sprite.center_x = x

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """

        if len(self.player_bullet_list) < 3:

            # Gunshot sound
            arcade.play_sound(self.gun_sound)

            # Create a bullet
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)

            # The image points to the right, and we want it to point up. So
            # rotate it.
            bullet.angle = 90

            # Give the bullet a speed
            bullet.change_y = BULLET_SPEED

            # Position the bullet
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top

            # Add the bullet to the appropriate lists
            self.player_bullet_list.append(bullet)

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.game_state == GAME_OVER:
            return

        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x

        move_down = False
        for enemy in self.enemy_list:
            if enemy.right > RIGHT_ENEMY_BORDER and self.enemy_change_x > 0:
                self.enemy_change_x *= -1
                move_down = True
            if enemy.left < LEFT_ENEMY_BORDER and self.enemy_change_x < 0:
                self.enemy_change_x *= -1
                move_down = True

        if move_down:
            for enemy in self.enemy_list:
                enemy.center_y -= ENEMY_MOVE_DOWN_AMOUNT
                if self.enemy_change_x > 0:
                    enemy.texture = self.enemy_textures[0]
                else:
                    enemy.texture = self.enemy_textures[1]

        x_spawn = []
        for enemy in self.enemy_list:
            chance = 4 + len(self.enemy_list) * 4
            if random.randrange(chance) == 0 and enemy.center_x not in x_spawn:
                # Create a bullet
                bullet = arcade.Sprite(":resources:images/space_shooter/laserRed01.png", SPRITE_SCALING_LASER)

                # The image points to the right, and we want it to point up. So
                # rotate it.
                bullet.angle = 180

                # Give the bullet a speed
                bullet.change_y = -BULLET_SPEED

                # Position the bullet
                bullet.center_x = enemy.center_x
                bullet.top = enemy.bottom

                # Add the bullet to the appropriate lists
                self.enemy_bullet_list.append(bullet)

            x_spawn.append(enemy.center_x)

        # Call update on bullet sprites
        self.player_bullet_list.update()
        self.enemy_bullet_list.update()

        # Loop through each bullet
        for bullet in self.enemy_bullet_list:
            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

        # Loop through each bullet
        for bullet in self.player_bullet_list:

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # For every enemy we hit, add to the score and remove the enemy
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

        if len(self.enemy_list) == 0:
            self.setup_level_one()

        # See if the player got hit with a bullet
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
            self.game_state = GAME_OVER


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
