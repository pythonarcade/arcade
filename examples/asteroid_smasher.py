import random
import math
import arcade

SCALE = 0.0015


class ShipSprite(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.thrust = 0
        self.speed = 0
        self.max_speed = 0.007
        self.drag = 0.0001
        self.respawning = 1

    def respawn(self):
        self.respawning = 1
        self.center_x = 0
        self.center_y = 0
        self.angle = 0

    def update(self):
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

        super().update()


class AsteroidSprite(arcade.Sprite):

    def update(self):
        super().update()
        if self.center_x < -2:
            self.center_x = 2
        if self.center_x > 2:
            self.center_x = -2
        if self.center_y > 2:
            self.center_y = -2
        if self.center_y < -2:
            self.center_y = 2


class BulletSprite(arcade.TurningSprite):

    def update(self):
        super().update()
        if self.center_x < -2.5 or self.center_x > 2.5 or self.center_y > 2.5 \
                or self.center_y < -2.5:
            self.kill()


class MyApplication(arcade.ArcadeApplication):
    """ Main application class. """

    def __init__(self):
        pass

    def setup_game(self):
        self.game_over = False

        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        self.score = 0
        self.player_sprite = ShipSprite("images/playerShip1_orange.png", SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = 3

        cur_pos = -1
        for i in range(self.lives):
            life = arcade.Sprite("images/playerLife1_orange.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = -1 + life.height
            cur_pos -= life.width
            self.all_sprites_list.append(life)
            self.ship_life_list.append(life)

        image_list = ("images/meteorGrey_big1.png",
                      "images/meteorGrey_big2.png",
                      "images/meteorGrey_big3.png",
                      "images/meteorGrey_big4.png")
        for i in range(3):
            image_no = random.randrange(4)
            enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)

            enemy_sprite.center_y = (random.random() - 0.5) * 4
            enemy_sprite.center_x = (random.random() - 0.5) * 4

            enemy_sprite.change_x = (random.random() - 0.5) * 0.005
            enemy_sprite.change_y = (random.random() - 0.5) * 0.005

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.all_sprites_list.append(enemy_sprite)
            self.asteroid_list.append(enemy_sprite)

    def render(self):
        arcade.start_render()

        self.all_sprites_list.render()
        output = "Score: {}".format(self.score)
        arcade.draw_text(output, -1.0, 0.95, arcade.color.WHITE)

        output = "Asteroid Count: {}".format(len(self.asteroid_list))
        arcade.draw_text(output, -1.0, 0.9, arcade.color.WHITE)
        arcade.swap_buffers()

    def key_pressed(self, key, x, y):
        if not self.player_sprite.respawning and key == b' ':
            bullet_sprite = BulletSprite("images/laserBlue01.png", SCALE)

            bullet_speed = 0.02
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

    def special_pressed(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif key == arcade.key.UP:
            self.player_sprite.thrust = .0005
        elif key == arcade.key.DOWN:
            self.player_sprite.thrust = -.0002

    def special_released(self, key, x, y):
        if key == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif key == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid):
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1
        print(self.score)

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = ["images/meteorGrey_med1.png",
                              "images/meteorGrey_med2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = (random.random() - 0.5) * 0.0065
                enemy_sprite.change_y = (random.random() - 0.5) * 0.0065

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

                enemy_sprite.change_x = (random.random() - 0.5) * 0.008
                enemy_sprite.change_y = (random.random() - 0.5) * 0.008

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

                enemy_sprite.change_x = (random.random() - 0.5) * 0.010
                enemy_sprite.change_y = (random.random() - 0.5) * 0.010

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)

    def animate(self):

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

        arcade.redisplay()

    def run(self):

        self.open_window()
        self.setup_game()

        arcade.run()

app = MyApplication()
app.run()
