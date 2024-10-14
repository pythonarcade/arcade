"""
Sprite Explosion

Simple program to show how to make explosions with a series of bitmaps.

Artwork from https://kenney.nl
Explosion graphics from https://www.explosiongenerator.com/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_explosion_bitmapped
"""
import random
import arcade

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
SPRITE_SCALING_LASER = 0.8
COIN_COUNT = 50

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Explosion Example"

BULLET_SPEED = 5

EXPLOSION_TEXTURE_COUNT = 60


class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__(texture_list[0])
        # How long the explosion has been around.
        self.time_elapsed = 0

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self, delta_time=1 / 60):
        self.time_elapsed += delta_time
        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture = int(self.time_elapsed * 60)
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()

        # Set up the player info
        # Image from kenney.nl
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70
        self.player_list.append(self.player_sprite)

        # Player score
        self.score = 0

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Pre-load the animation frames. We don't do this in the __init__
        # of the explosion sprite because it
        # takes too long and would cause the game to pause.
        self.explosion_texture_list = []

        # Load the explosion from a sprite sheet
        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        # Load the explosions from a sprite sheet
        spritesheet = arcade.load_spritesheet(file_name)
        self.explosion_texture_list = spritesheet.get_texture_grid(
            size=(sprite_width, sprite_height),
            columns=columns,
            count=count,
        )

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")

        self.background_color = arcade.color.AMAZON
        self.spawn_enemies()

    def reset(self):
        """Restart the game."""

        # Clear out the sprite lists
        self.enemy_list.clear()
        self.bullet_list.clear()
        self.explosions_list.clear()

        # Reset the score
        self.score = 0

        self.spawn_enemies()

    def spawn_enemies(self):
        for coin_index in range(COIN_COUNT):
            # Create the enemy instance. Image from kenney.nl
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                scale=SPRITE_SCALING_COIN,
                center_x=random.randrange(25, WINDOW_WIDTH - 25),
                center_y=random.randrange(150, WINDOW_HEIGHT),
            )
            # Add the coin to enemy list
            self.enemy_list.append(coin)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()

        # Render the text
        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        # Gunshot sound
        arcade.sound.play_sound(self.gun_sound)

        # Create a bullet
        bullet = arcade.Sprite(
            ":resources:images/space_shooter/laserBlue01.png",
            scale=SPRITE_SCALING_LASER,
        )

        # The image points to the right, and we want it to point up. So
        # rotate it.
        bullet.angle = 270

        # Give it a speed
        bullet.change_y = BULLET_SPEED

        # Position the bullet
        bullet.center_x = self.player_sprite.center_x
        bullet.bottom = self.player_sprite.top

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.reset()
        # Close the window
        elif symbol == arcade.key.ESCAPE:
            self.window.close()

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Call update on bullet sprites
        self.bullet_list.update()
        self.explosions_list.update()

        # Loop through each bullet
        for bullet in self.bullet_list:

            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # If it did...
            if len(hit_list) > 0:

                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)

                # Move it to the location of the coin
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                # Call update() because it sets which image we start on
                explosion.update()

                # Add to a list of sprites that are explosions
                self.explosions_list.append(explosion)

                # Get rid of the bullet
                bullet.remove_from_sprite_lists()

            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.sound.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > WINDOW_HEIGHT:
                bullet.remove_from_sprite_lists()



def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()
