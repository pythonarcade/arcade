"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl
"""
import random
import math
import arcade
import pyglet
import pyglet.window.key

SCALE = 1

window = None

class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self, filename, scale):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 1.1
        self.drag = 0.01

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = window.width / 2
        self.center_y = window.height / 2
        self.angle = 0

    def update(self):
        """
        Update our position and other particulars.
        """
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning / 500.0
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 1
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        """ Call the parent class. """
        super().update()


class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """

    def update(self):
        """ Move the asteroid around. """
        super().update()
        if self.center_x < -window.width // 2:
            self.center_x = window.width + (window.width // 2)
        if self.center_x > window.width + (window.width // 2):
            self.center_x = -window.width // 2
        if self.center_y > window.height + (window.height // 2):
            self.center_y = -window.height // 2
        if self.center_y < -window.height // 2:
            self.center_y = window.height + (window.height // 2)


class BulletSprite(arcade.TurningSprite):
    """
    Class that represents a bullet.

    Derives from arcade.TurningSprite which is just a Sprite
    that aligns to its direction.
    """
    def update(self):
        super().update()
        if self.center_x < -100 or self.center_x > 1500 or self.center_y > 1100 \
                or self.center_y < -100:
            self.kill()


class MyApplication(pyglet.window.Window):
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """



        self.game_over = False

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite("images/playerShip1_orange.png", SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = 3

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite("images/playerLife1_orange.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.all_sprites_list.append(life)
            self.ship_life_list.append(life)

        # Make the asteroids
        image_list = ("images/meteorGrey_big1.png",
                      "images/meteorGrey_big2.png",
                      "images/meteorGrey_big3.png",
                      "images/meteorGrey_big4.png")
        for i in range(3):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)

            enemy_sprite.center_y = random.randrange(window.width)
            enemy_sprite.center_x = random.randrange(window.height)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.all_sprites_list.append(enemy_sprite)
            self.asteroid_list.append(enemy_sprite)

            pyglet.clock.schedule_interval(self.animate, 1/60)



    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Put the text on the screen.
        output = "Score: {}".format(self.score)
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 14)

        output = "Asteroid Count: {}".format(len(self.asteroid_list))
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 14)


    def on_key_press(self, symbol, modifiers):
        """ Called whenever a 'normal' key is pressed. """
        # Shoot if the player hit the space bar and we aren't respawning.
        if not self.player_sprite.respawning and symbol == pyglet.window.key.SPACE:
            bullet_sprite = BulletSprite("images/laserBlue01.png", SCALE)

            bullet_speed = 4
            bullet_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
            bullet_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * bullet_speed

            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()

            self.all_sprites_list.append(bullet_sprite)
            self.bullet_list.append(bullet_sprite)


        if symbol == pyglet.window.key.LEFT:
            self.player_sprite.change_angle = 3
        elif symbol == pyglet.window.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif symbol == pyglet.window.key.UP:
            self.player_sprite.thrust = 0.15
        elif symbol == pyglet.window.key.DOWN:
            self.player_sprite.thrust = -.2

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a 'special' key is released. """
        if symbol == pyglet.window.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == pyglet.window.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == pyglet.window.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == pyglet.window.key.DOWN:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["images/meteorGrey_med1.png",
                              "images/meteorGrey_med2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["images/meteorGrey_small1.png",
                              "images/meteorGrey_small2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["images/meteorGrey_tiny1.png",
                              "images/meteorGrey_tiny2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

    def animate(self, x):
        """ Move everything """
        if not self.game_over:
            self.all_sprites_list.update()

            for bullet in self.bullet_list:
                asteroids = \
                    arcade.check_for_collision_with_list(bullet,
                                                         self.asteroid_list)
                for asteroid in asteroids:
                    self.split_asteroid(asteroid)
                    asteroid.kill()
                    bullet.kill()

            if not self.player_sprite.respawning:
                asteroids = \
                    arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.asteroid_list)
                if len(asteroids) > 0:
                    if self.lives > 0:
                        self.lives -= 1
                        self.player_sprite.respawn()
                        self.split_asteroid(asteroids[0])
                        asteroids[0].kill()
                        self.ship_life_list.pop().kill()
                        print("Crash")
                    else:
                        self.game_over = True
                        print("Game over")


window = MyApplication()
window.set_size(1400, 1000)
window.setup()

pyglet.app.run()