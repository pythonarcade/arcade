"""
Slime Invaders

Artwork from https://kenney.nl

This example shows how to:

* Get sprites to move as a group
* Change texture of sprites as a group
* Only have the bottom sprite in the group fire lasers
* Create 'shields' like in space invaders

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.slime_invaders
"""
import random
import arcade

SPRITE_SCALING_PLAYER = 0.75
SPRITE_SCALING_enemy = 0.75
SPRITE_SCALING_LASER = 1.0

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Slime Invaders"

BULLET_SPEED = 5
ENEMY_SPEED = 2

MAX_PLAYER_BULLETS = 3

# This margin controls how close the enemy gets to the left or right side
# before reversing direction.
ENEMY_VERTICAL_MARGIN = 15
RIGHT_ENEMY_BORDER = WINDOW_WIDTH - ENEMY_VERTICAL_MARGIN
LEFT_ENEMY_BORDER = ENEMY_VERTICAL_MARGIN

# How many pixels to move the enemy down when reversing
ENEMY_MOVE_DOWN_AMOUNT = 30

# Game state
GAME_OVER = 1
PLAY_GAME = 0


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList()

        # State of the game
        self.game_state = PLAY_GAME

        # Set up the player info
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_list.append(self.player_sprite)

        self.score = 0

        # Enemy movement
        self.enemy_change_x = -ENEMY_SPEED

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")
        self.texture_enemy_left = arcade.load_texture(
            ":resources:images/enemies/slimeBlue.png",
        )
        self.texture_enemy_right = self.texture_enemy_left.flip_left_right()
        # The laser points right so we rotate it 270 clockwise to point up
        self.texture_blue_laser = arcade.load_texture(
            ":resources:images/space_shooter/laserBlue01.png",
        ).rotate_270()

        self.background_color = arcade.color.AMAZON
        self.score_text = arcade.Text("Score: 0", 10, 20, arcade.color.WHITE, 14)
        self.game_over_text = arcade.Text(
            "GAME OVER",
            x=self.width / 2,
            y=self.height / 2,
            color=arcade.color.WHITE,
            font_size=60,
            anchor_x="center",
        )

    def setup_level_one(self):
        # Load the textures for the enemies, one facing left, one right
        # Create rows and columns of enemies
        x_count = 7
        x_start = 380
        x_spacing = 80
        y_count = 5
        y_start = 470
        y_spacing = 60
        for x in range(x_start, x_spacing * x_count + x_start, x_spacing):
            for y in range(y_start, y_spacing * y_count + y_start, y_spacing):
                # Create the enemy instance
                # enemy image from kenney.nl
                enemy = arcade.Sprite(
                    self.texture_enemy_right,
                    scale=SPRITE_SCALING_enemy,
                    center_x=x,
                    center_y=y
                )
                # Add the enemy to the lists
                self.enemy_list.append(enemy)

    def make_shield(self, x_start):
        """
        Make a shield, which is just a 2D grid of solid color sprites
        stuck together with no margin so you can't tell them apart.
        """
        shield_block_width = 10
        shield_block_height = 20
        shield_width_count = 20
        shield_height_count = 5
        y_start = 150
        for x in range(x_start,
                       x_start + shield_width_count * shield_block_width,
                       shield_block_width):
            for y in range(y_start,
                           y_start + shield_height_count * shield_block_height,
                           shield_block_height):
                shield_sprite = arcade.SpriteSolidColor(shield_block_width,
                                                        shield_block_height,
                                                        color=arcade.color.WHITE)
                shield_sprite.center_x = x
                shield_sprite.center_y = y
                self.shield_list.append(shield_sprite)

    def reset(self):
        """
        Reset the game so it can be played again.
        This is not a standard Arcade method. It's simply an example of how
        you might reset the game.
        """
        self.game_state = PLAY_GAME

        # Clear the sprite lists
        self.enemy_list.clear()
        self.player_bullet_list.clear()
        self.enemy_bullet_list.clear()
        self.shield_list.clear()

        # Set up the player
        self.score = 0

        # Set default position for player
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70

        # Make each of the shields
        step = self.width // 4 - 50
        print("make_shield", step)
        for x in [step, step * 2, step * 3]:
            print(x)
            self.make_shield(x)

        # Set the background color
        self.background_color = arcade.color.AMAZON

        self.setup_level_one()

    def on_draw(self):
        """Render the screen."""
        # Clear the window / screen with the configured background color
        self.clear()

        # Draw all the sprites.
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw(pixelated=True)
        self.player_list.draw()

        # Update and draw the score
        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()

        # Draw game over if the game state is such
        if self.game_state == GAME_OVER:
            self.game_over_text.draw()
            self.window.set_mouse_visible(True)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        # Don't move the player if the game is over
        if self.game_state == GAME_OVER:
            return

        self.player_sprite.center_x = x

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        # Only allow the user so many bullets on screen at a time to prevent
        # them from spamming bullets.
        if len(self.player_bullet_list) < MAX_PLAYER_BULLETS:
            # Gunshot sound
            # arcade.play_sound(self.gun_sound)

            # Create a bullet
            bullet = arcade.Sprite(self.texture_blue_laser, scale=SPRITE_SCALING_LASER)

            # Give the bullet a speed
            bullet.change_y = BULLET_SPEED

            # Position the bullet
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top

            # Add the bullet to the appropriate lists
            self.player_bullet_list.append(bullet)

    def update_enemies(self):
        # Move the enemy vertically
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x

        # Check every enemy to see if any hit the edge. If so, reverse the
        # direction and flag to move down.
        move_down = False
        for enemy in self.enemy_list:
            if enemy.right > RIGHT_ENEMY_BORDER and self.enemy_change_x > 0:
                self.enemy_change_x *= -1
                move_down = True
            if enemy.left < LEFT_ENEMY_BORDER and self.enemy_change_x < 0:
                self.enemy_change_x *= -1
                move_down = True

        # Did we hit the edge above, and need to move t he enemy down?
        if move_down:
            # Yes
            for enemy in self.enemy_list:
                # Move enemy down
                enemy.center_y -= ENEMY_MOVE_DOWN_AMOUNT
                # Flip texture on enemy so it faces the other way
                if self.enemy_change_x > 0:
                    enemy.texture = self.texture_enemy_left
                else:
                    enemy.texture = self.texture_enemy_right

    def allow_enemies_to_fire(self):
        """
        See if any enemies will fire this frame.
        """
        # Track which x values have had a chance to fire a bullet.
        # Since enemy list is build from the bottom up, we can use
        # this to only allow the bottom row to fire.
        x_spawn = []
        for enemy in self.enemy_list:
            # Adjust the chance depending on the number of enemies. Fewer
            # enemies, more likely to fire.
            chance = 4 + len(self.enemy_list) * 4

            # Fire if we roll a zero, and no one else in this column has had
            # a chance to fire.
            if random.randrange(chance) == 0 and enemy.center_x not in x_spawn:
                # Create a bullet
                bullet = arcade.Sprite(
                    ":resources:images/space_shooter/laserRed01.png",
                    scale=SPRITE_SCALING_LASER,
                )

                # Angle down.
                bullet.angle = 180

                # Give the bullet a speed
                bullet.change_y = -BULLET_SPEED

                # Position the bullet so its top id right below the enemy
                bullet.center_x = enemy.center_x
                bullet.top = enemy.bottom

                # Add the bullet to the appropriate list
                self.enemy_bullet_list.append(bullet)

            # Ok, this column has had a chance to fire. Add to list so we don't
            # try it again this frame.
            x_spawn.append(enemy.center_x)

    def process_enemy_bullets(self):
        # Move the bullets
        self.enemy_bullet_list.update()

        # Loop through each bullet
        for bullet in self.enemy_bullet_list:
            # Check this bullet to see if it hit a shield
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)

            # If it did, get rid of the bullet and shield blocks
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # See if the player got hit with a bullet
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
                self.game_state = GAME_OVER

            # If the bullet falls off the screen get rid of it
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

    def process_player_bullets(self):
        # Move the bullets
        self.player_bullet_list.update()

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
            if bullet.bottom > WINDOW_HEIGHT:
                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time):
        """ Movement and game logic """
        if self.game_state == GAME_OVER:
            return

        self.update_enemies()
        self.allow_enemies_to_fire()
        self.process_enemy_bullets()
        self.process_player_bullets()

        if len(self.enemy_list) == 0:
            self.setup_level_one()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.reset()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
