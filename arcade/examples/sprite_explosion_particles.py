"""
Sprite Explosion

Simple program to show creating explosions with sprites.
There are more performant ways to do this, but for simple games this
is a good way to get started.

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
ENEMY_COUNT = 50

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Explosion Example"

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
    """Particle with smoke like behavior."""
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = SMOKE_RISE_RATE
        self.scale = SMOKE_START_SCALE

    def update(self, delta_time: float = 1/60):
        """Update this particle"""
        # Take delta_time into account
        time_step = 60 * delta_time

        if self.alpha <= PARTICLE_FADE_RATE:
            # Remove faded out particles
            self.remove_from_sprite_lists()
        else:
            # Update values
            self.alpha -= int(SMOKE_FADE_RATE * time_step)
            self.center_x += self.change_x * time_step
            self.center_y += self.change_y * time_step
            self.add_scale(SMOKE_EXPANSION_RATE * time_step)


class Particle(arcade.SpriteCircle):
    """ Explosion particle"""
    def __init__(self):
        """
        Simple particle sprite based on circle sprite.
        """
        # Make the particle
        super().__init__(PARTICLE_RADIUS, random.choice(PARTICLE_COLORS))

        # Set direction/speed
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

    def update(self, delta_time: float = 1 / 60):
        """Update the particle"""
        # Take delta_time into account
        time_step = 60 * delta_time

        if self.alpha == 0:
            # Faded out, remove
            self.remove_from_sprite_lists()
        else:
            # Gradually fade out the particle. Don't go below 0
            self.alpha = max(0, self.alpha - PARTICLE_FADE_RATE)
            # Move the particle
            self.center_x += self.change_x * time_step
            self.center_y += self.change_y * time_step
            self.change_y -= PARTICLE_GRAVITY * time_step

            # Should we sparkle this?
            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.color = arcade.color.WHITE

            # Leave a smoke particle?
            if random.random() <= SMOKE_CHANCE:
                smoke = Smoke(5)
                smoke.position = self.position
                # Add a smoke particle to the spritelist this sprite is in
                self.sprite_lists[0].append(smoke)


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

        # Set up the player info. Image from kenney.nl
        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip2_orange.png",
            scale=SPRITE_SCALING_PLAYER,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70
        self.player_list.append(self.player_sprite)

        self.score = 0

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")

        self.background_color = arcade.color.BLACK
        self.score_display = arcade.Text("", 10, 20, arcade.color.WHITE, 14)

        self.spawn_enemies()

    def reset(self):
        """Restart the game"""
        # Reset score
        self.score = 0

        self.enemy_list.clear()
        self.bullet_list.clear()
        self.explosions_list.clear()

        self.spawn_enemies()

    def spawn_enemies(self):
        # Spawn enemies
        for index in range(ENEMY_COUNT):
            # Create the coin instance. Image from kenney.nl
            enemy = arcade.Sprite(
                ":resources:images/space_shooter/playerShip1_green.png",
                scale=SPRITE_SCALING_COIN,
                angle=180,
                center_x=random.randrange(25, WINDOW_WIDTH - 25),
                center_y=random.randrange(150, WINDOW_HEIGHT)
            )
            # Add the ship to the lists
            self.enemy_list.append(enemy)

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
        self.score_display.text = f"Score: {self.score}"
        self.score_display.draw()

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
        """ Movement and game logic """

        # Call update on bullet sprites
        self.bullet_list.update(delta_time)
        self.explosions_list.update(delta_time)

        # Loop through each bullet
        for bullet in self.bullet_list:

            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # If it did...
            if len(hit_list) > 0:

                # Get rid of the bullet
                bullet.remove_from_sprite_lists()

            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                # Make an explosion
                for i in range(PARTICLE_COUNT):
                    particle = Particle()
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
