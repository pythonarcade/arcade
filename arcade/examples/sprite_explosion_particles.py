"""
Sprite Explosion

Simple program to show creating explosions with particles

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_explosion_particles
"""
import random
import math
import arcade

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.3
SPRITE_SCALING_LASER = 0.8
COIN_COUNT = 50

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Explosion Example"

BULLET_SPEED = 5

# --- Explosion Particles Related

# How fast the particle will accelerate down. Make 0 if not desired
PARTICLE_GRAVITY = 0.05

# How fast to fade the particle
PARTICLE_FADE_RATE = 8

# How fast the particle moves. Range is from 2.5 <--> 5 with 2.5 and 2.5 set.
PARTICLE_MIN_SPEED = 2.5
PARTICLE_SPEED_RANGE = 2.5

# How many particles per explosion
PARTICLE_COUNT = 20

# How big the particle
PARTICLE_RADIUS = 3

# Possible particle colors
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.COQUELICOT,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]

# Chance we'll flip the texture to white and make it 'sparkle'
PARTICLE_SPARKLE_CHANCE = 0.02

# --- Smoke
# Note: Adding smoke trails makes for a lot of sprites and can slow things
# down. If you want a lot, it will be necessary to move processing to GPU
# using transform feedback. If to slow, just get rid of smoke.

# Start scale of smoke, and how fast is scales up
SMOKE_START_SCALE = 0.25
SMOKE_EXPANSION_RATE = 0.03

# Rate smoke fades, and rises
SMOKE_FADE_RATE = 7
SMOKE_RISE_RATE = 0.5

# Chance we leave smoke trail
SMOKE_CHANCE = 0.25


class Smoke(arcade.SpriteCircle):
    """ This represents a puff of smoke """
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = SMOKE_RISE_RATE
        self.scale = SMOKE_START_SCALE

    def update(self):
        """ Update this particle """
        if self.alpha <= PARTICLE_FADE_RATE:
            # Remove faded out particles
            self.remove_from_sprite_lists()
        else:
            # Update values
            self.alpha -= SMOKE_FADE_RATE
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.scale += SMOKE_EXPANSION_RATE


class Particle(arcade.SpriteCircle):
    """ Explosion particle """
    def __init__(self, my_list):
        # Choose a random color
        color = random.choice(PARTICLE_COLORS)

        # Make the particle
        super().__init__(PARTICLE_RADIUS, color)

        # Track normal particle texture, so we can 'flip' when we sparkle.
        self.normal_texture = self.texture

        # Keep track of the list we are in, so we can add a smoke trail
        self.my_list = my_list

        # Set direction/speed
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

        # Track original alpha. Used as part of 'sparkle' where we temp set the
        # alpha back to 255
        self.my_alpha = 255

        # What list do we add smoke particles to?
        self.my_list = my_list

    def update(self):
        """ Update the particle """
        if self.my_alpha <= PARTICLE_FADE_RATE:
            # Faded out, remove
            self.remove_from_sprite_lists()
        else:
            # Update
            self.my_alpha -= PARTICLE_FADE_RATE
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= PARTICLE_GRAVITY

            # Should we sparkle this?
            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width),
                                                          arcade.color.WHITE)
            else:
                self.texture = self.normal_texture

            # Leave a smoke particle?
            if random.random() <= SMOKE_CHANCE:
                smoke = Smoke(5)
                smoke.position = self.position
                self.my_list.append(smoke)


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None
        self.bullet_list = None
        self.explosions_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):

        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()

        # Set up the player
        self.score = 0

        # Image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/space_shooter/playerShip2_orange.png",
                                           SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70
        self.player_list.append(self.player_sprite)

        # Create the coins
        for coin_index in range(COIN_COUNT):

            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite(":resources:images/space_shooter/playerShip1_green.png",
                                 SPRITE_SCALING_COIN)
            coin.angle = 180

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(150, SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.coin_list.draw()
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
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)

        # The image points to the right, and we want it to point up. So
        # rotate it.
        bullet.angle = 90

        # Give it a speed
        bullet.change_y = BULLET_SPEED

        # Position the bullet
        bullet.center_x = self.player_sprite.center_x
        bullet.bottom = self.player_sprite.top

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on bullet sprites
        self.bullet_list.update()
        self.explosions_list.update()

        # Loop through each bullet
        for bullet in self.bullet_list:

            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            # If it did...
            if len(hit_list) > 0:

                # Get rid of the bullet
                bullet.remove_from_sprite_lists()

            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                # Make an explosion
                for i in range(PARTICLE_COUNT):
                    particle = Particle(self.explosions_list)
                    particle.position = coin.position
                    self.explosions_list.append(particle)

                smoke = Smoke(50)
                smoke.position = coin.position
                self.explosions_list.append(smoke)

                coin.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.sound.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()


def main():
    window = MyGame()
    window.center_window()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
