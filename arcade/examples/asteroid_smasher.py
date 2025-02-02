"""
Asteroid Smasher

Shoot space rocks in this demo program created with Python and the
Arcade library.

Artwork from https://kenney.nl

For a fancier example of this game, see:
https://github.com/pythonarcade/asteroids

If Python and Arcade are installed, this example can be run from
the command line with:
python -m arcade.examples.asteroid_smasher
"""
import random
import math
import arcade

from typing import cast

WINDOW_TITLE = "Asteroid Smasher"
STARTING_ASTEROID_COUNT = 3
SCALE = 0.5

# Screen dimensions and limits
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
OFFSCREEN_SPACE = 300
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = WINDOW_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = WINDOW_HEIGHT + OFFSCREEN_SPACE

# Control player speed
TURN_SPEED = 3
THRUST_AMOUNT = 0.2

# Asteroid types
ASTERIOD_TYPE_BIG = 4
ASTERIOD_TYPE_MEDIUM = 3
ASTERIOD_TYPE_SMALL = 2
ASTERIOD_TYPE_TINY = 1


class TurningSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self, delta_time=1 / 60):
        """ Move the sprite """
        super().update(delta_time)
        self.angle = -math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(arcade.Sprite):
    """ Sprite that represents our spaceship. """
    def __init__(self, filename, scale):
        """ Set up the spaceship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale=scale)

        # Info on the space ship.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.05
        self.respawning = 0

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.alpha = 0
        self.center_x = WINDOW_WIDTH / 2
        self.center_y = WINDOW_HEIGHT / 2
        self.angle = 0

    def update(self, delta_time=1 / 60):
        """ Update our position and other particulars. """

        # Is the user spawning
        if self.respawning:
            # Increase spawn counter, setting alpha to that amount
            self.respawning += 1
            self.alpha = self.respawning
            # Once we are close enough, set alpha to 255 and clear
            # respawning flag
            if self.respawning > 230:
                self.respawning = 0
                self.alpha = 255

        # Apply drag forward
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0
        # Apply drag reverse
        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        # Apply thrust
        self.speed += self.thrust

        # Enforce speed limit
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # Calculate movement vector based on speed/angle
        self.change_x = math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        # Apply movement vector
        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = WINDOW_WIDTH
        if self.left > WINDOW_WIDTH:
            self.right = 0
        if self.bottom < 0:
            self.top = WINDOW_HEIGHT
        if self.top > WINDOW_HEIGHT:
            self.bottom = 0

        """ Call the parent class. """
        super().update()


class AsteroidSprite(arcade.Sprite):
    """Sprite that represents an asteroid."""

    def __init__(self, image_file_name, scale, type):
        super().__init__(image_file_name, scale=scale)
        self.type = type

    def update(self, delta_time=1 / 60):
        """ Move the asteroid around. """
        super().update(delta_time)
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        self.game_over = False

        # Create sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.lives = 3

        # Load sounds
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

        # Text fields
        self.text_score = arcade.Text(
            f"Score: {self.score}",
            x=10,
            y=70,
            font_size=13,
        )
        self.text_asteroid_count = arcade.Text(
            f"Asteroid Count: {len(self.asteroid_list)}",
            x=10,
            y=50,
            font_size=13,
        )

    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite(
            ":resources:images/space_shooter/playerShip1_orange.png",
            scale=SCALE,
        )
        self.player_sprite_list.append(self.player_sprite)
        self.lives = 3

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite(
                ":resources:images/space_shooter/playerLife1_orange.png",
                scale=SCALE,
            )
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)

        # Make the asteroids
        image_list = (
            ":resources:images/space_shooter/meteorGrey_big1.png",
            ":resources:images/space_shooter/meteorGrey_big2.png",
            ":resources:images/space_shooter/meteorGrey_big3.png",
            ":resources:images/space_shooter/meteorGrey_big4.png",
            )
        for i in range(STARTING_ASTEROID_COUNT):
            # Pick one of four random rock images
            image_no = random.randrange(4)

            enemy_sprite = AsteroidSprite(
                image_list[image_no],
                scale=SCALE,
                type=ASTERIOD_TYPE_BIG,
            )

            # Set position
            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            # Set speed / rotation
            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1
            enemy_sprite.change_angle = (random.random() - 0.5) * 2

            self.asteroid_list.append(enemy_sprite)

        self.text_score.text = f"Score: {self.score}"
        self.text_asteroid_count.text = f"Asteroid Count: {len(self.asteroid_list)}"

    def on_draw(self):
        """ Render the screen """

        # Clear the screen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.asteroid_list.draw()
        self.ship_life_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()

        # Draw the text
        self.text_score.draw()
        self.text_asteroid_count.draw()

    def on_key_press(self, symbol, modifiers):
        """ Called whenever a key is pressed. """
        # Shoot if the player hit the space bar and we aren't respawning.
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            bullet_sprite = TurningSprite(":resources:images/space_shooter/laserBlue01.png",
                                          scale=SCALE)

            # Set bullet vector
            bullet_speed = 13
            angle_radians = math.radians(self.player_sprite.angle)
            bullet_sprite.change_y = math.cos(angle_radians) * bullet_speed
            bullet_sprite.change_x = math.sin(angle_radians) * bullet_speed

            # Set bullet position
            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y

            # Add to our sprite list
            self.bullet_list.append(bullet_sprite)

            # Go ahead and move it a frame
            bullet_sprite.update()

            # Pew pew
            arcade.play_sound(self.laser_sound, speed=random.random() * 3 + 0.5)

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = -TURN_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = TURN_SPEED
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = THRUST_AMOUNT
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -THRUST_AMOUNT
        # Restart the game if the player hits 'R'
        elif symbol == arcade.key.R:
            self.start_new_game()
        # Quit if the player hits escape
        elif symbol == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a key is released. """
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.type == ASTERIOD_TYPE_BIG:
            # Split large asteroid into 2 medium ones
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_med1.png",
                              ":resources:images/space_shooter/meteorGrey_med2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              scale=SCALE * 1.5,
                                              type=ASTERIOD_TYPE_MEDIUM)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.asteroid_list.append(enemy_sprite)
                self.hit_sound1.play()

        elif asteroid.type == ASTERIOD_TYPE_MEDIUM:
            # Split medium asteroid into 2 small ones
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_small1.png",
                              ":resources:images/space_shooter/meteorGrey_small2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              scale=SCALE * 1.5,
                                              type=ASTERIOD_TYPE_SMALL)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.asteroid_list.append(enemy_sprite)
                self.hit_sound2.play()

        elif asteroid.type == ASTERIOD_TYPE_SMALL:
            # Split small asteroid into 2 tiny ones
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_tiny1.png",
                              ":resources:images/space_shooter/meteorGrey_tiny2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              scale=SCALE * 1.5,
                                              type=ASTERIOD_TYPE_TINY)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2

                self.asteroid_list.append(enemy_sprite)
                self.hit_sound3.play()

        elif asteroid.type == ASTERIOD_TYPE_TINY:
            # Do nothing. The tiny asteroid just goes away.
            self.hit_sound4.play()

    def on_update(self, x):
        """ Move everything """

        if not self.game_over:
            self.asteroid_list.update()
            self.bullet_list.update()
            self.player_sprite_list.update()

            for bullet in self.bullet_list:
                asteroids = arcade.check_for_collision_with_list(bullet,
                                                                 self.asteroid_list)

                for asteroid in asteroids:
                    # expected AsteroidSprite, got Sprite instead
                    self.split_asteroid(cast(AsteroidSprite, asteroid))
                    asteroid.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()

                # Remove bullet if it goes off-screen
                size = max(bullet.width, bullet.height)
                if bullet.center_x < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_x > WINDOW_WIDTH + size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y < 0 - size:
                    bullet.remove_from_sprite_lists()
                if bullet.center_y > WINDOW_HEIGHT + size:
                    bullet.remove_from_sprite_lists()

            if not self.player_sprite.respawning:
                asteroids = arcade.check_for_collision_with_list(self.player_sprite,
                                                                 self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
                        asteroids[0].remove_from_sprite_lists()
                        self.ship_life_list.pop().remove_from_sprite_lists()
                        print("Crash")
                    else:
                        self.game_over = True
                        print("Game over")

        # Update the text objects
        self.text_score.text = f"Score: {self.score}"
        self.text_asteroid_count.text = f"Asteroid Count: {len(self.asteroid_list)}"


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.start_new_game()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
