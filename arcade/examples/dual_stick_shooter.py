"""
Dual-stick Shooter Example

A dual-analog stick joystick is the preferred method of input. If a joystick is
not present, the game will fail back to use keyboard controls (WASD to move, arrows to shoot)

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.dual_stick_shooter
"""
import arcade
import random
import math
import os
import pprint

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Dual-stick Shooter Example"
MOVEMENT_SPEED = 4
BULLET_SPEED = 10
BULLET_COOLDOWN_TICKS = 10
ENEMY_SPAWN_INTERVAL = 1
ENEMY_SPEED = 1
JOY_DEADZONE = 0.2


def dump_obj(obj):
    for key in sorted(vars(obj)):
        val = getattr(obj, key)
        print("{:30} = {} ({})".format(key, val, type(val).__name__))

def dump_joystick(joy):
    print("========== {}".format(joy))
    print("x       {}".format(joy.x))
    print("y       {}".format(joy.y))
    print("z       {}".format(joy.z))
    print("rx      {}".format(joy.rx))
    print("ry      {}".format(joy.ry))
    print("rz      {}".format(joy.rz))
    print("hat_x   {}".format(joy.hat_x))
    print("hat_y   {}".format(joy.hat_y))
    print("buttons {}".format(joy.buttons))
    print("========== Extra joy")
    dump_obj(joy)
    print("========== Extra joy.device")
    dump_obj(joy.device)
    print("========== pprint joy")
    pprint.pprint(joy)
    print("========== pprint joy.device")
    pprint.pprint(joy.device)

def dump_joystick_state(ticks, joy):
    # print("{:5.2f} {:5.2f} {:>20} {:5}_".format(1.234567, -8.2757272903, "hello", str(True)))
    fmt_str = "{:6d} "
    num_fmts = ["{:5.2f}"] * 6
    fmt_str += " ".join(num_fmts)
    fmt_str += " {:2d} {:2d} {}"
    buttons = " ".join(["{:5}".format(str(b)) for b in joy.buttons])
    print(fmt_str.format(ticks,
                         joy.x,
                         joy.y,
                         joy.z,
                         joy.rx,
                         joy.ry,
                         joy.rz,
                         joy.hat_x,
                         joy.hat_y,
                         buttons))

def get_joy_position(x, y):
    """Given position of joystick axes, return (x, y, angle_in_degrees).
    If movement is not outside of deadzone, return (None, None, None)"""
    if x > JOY_DEADZONE or x < -JOY_DEADZONE or y > JOY_DEADZONE or y < -JOY_DEADZONE:
        y = -y
        rad = math.atan2(y, x)
        angle = math.degrees(rad)
        return x, y, angle
    return None, None, None


class Player(arcade.sprite.Sprite):
    def __init__(self, filename):
        super().__init__(filename=filename, scale=0.4, center_x=SCREEN_WIDTH/2, center_y=SCREEN_HEIGHT/2)
        self.shoot_up_pressed = False
        self.shoot_down_pressed = False
        self.shoot_left_pressed = False
        self.shoot_right_pressed = False


class Enemy(arcade.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(filename='images/bumper.png', scale=0.5, center_x=x, center_y=y)

    def follow_sprite(self, player_sprite):
        """
        This function will move the current sprite towards whatever
        other sprite is specified as a parameter.

        We use the 'min' function here to get the sprite to line up with
        the target sprite, and not jump around if the sprite is not off
        an exact multiple of ENEMY_SPEED.
        """

        if self.center_y < player_sprite.center_y:
            self.center_y += min(ENEMY_SPEED, player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min(ENEMY_SPEED, self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min(ENEMY_SPEED, player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min(ENEMY_SPEED, self.center_x - player_sprite.center_x)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)
        self.game_over = False
        self.score = 0
        self.tick = 0
        self.bullet_cooldown = 0
        self.player = Player("images/playerShip2_orange.png")
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.joy = None
        joys = arcade.get_joysticks()
        for joy in joys:
            dump_joystick(joy)
        if joys:
            self.joy = joys[0]
            self.joy.open()
            print("Using joystick controls: {}".format(self.joy.device))
            arcade.window_commands.schedule(self.debug_joy_state, 0.1)
        if not self.joy:
            print("No joystick present, using keyboard controls")
        arcade.window_commands.schedule(self.spawn_enemy, ENEMY_SPAWN_INTERVAL)

    def debug_joy_state(self, delta_time):
        dump_joystick_state(self.tick, self.joy)

    def spawn_enemy(self, elapsed):
        if self.game_over:
            return
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        self.enemy_list.append(Enemy(x, y))

    def update(self, delta_time):
        self.tick += 1
        if self.game_over:
            return

        self.bullet_cooldown += 1

        for enemy in self.enemy_list:
            enemy.follow_sprite(self.player)

        if self.joy:
            # Joystick input - movement
            move_x, move_y, move_angle = get_joy_position(self.joy.x, self.joy.y)
            if move_angle:
                self.player.change_x = move_x * MOVEMENT_SPEED
                self.player.change_y = move_y * MOVEMENT_SPEED
                # An angle of "0" means "right", but the player's image is drawn in the "up" direction. So an offset is needed.
                self.player.angle = move_angle - 90
            else:
                self.player.change_x = 0
                self.player.change_y = 0
            # Joystick input - shooting
            shoot_x, shoot_y, shoot_angle = get_joy_position(self.joy.z, self.joy.rz)
            if shoot_angle:
                self.spawn_bullet(shoot_angle)
        else:
            # Keyboard input - shooting
            if self.player.shoot_right_pressed and self.player.shoot_up_pressed:
                self.spawn_bullet(0+45)
            elif self.player.shoot_up_pressed and self.player.shoot_left_pressed:
                self.spawn_bullet(90+45)
            elif self.player.shoot_left_pressed and self.player.shoot_down_pressed:
                self.spawn_bullet(180+45)
            elif self.player.shoot_down_pressed and self.player.shoot_right_pressed:
                self.spawn_bullet(270+45)
            elif self.player.shoot_right_pressed:
                self.spawn_bullet(0)
            elif self.player.shoot_up_pressed:
                self.spawn_bullet(90)
            elif self.player.shoot_left_pressed:
                self.spawn_bullet(180)
            elif self.player.shoot_down_pressed:
                self.spawn_bullet(270)

        self.enemy_list.update()
        self.player.update()
        self.bullet_list.update()
        ship_death_hit_list = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        if len(ship_death_hit_list) > 0:
            self.game_over = True
        for bullet in self.bullet_list:
            bullet_killed = False
            enemy_shot_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            # Loop through each colliding sprite, remove it, and add to the score.
            for enemy in enemy_shot_list:
                enemy.kill()
                bullet.kill()
                bullet_killed = True
                self.score += 1
            if bullet_killed:
                continue

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = MOVEMENT_SPEED
            self.player.angle = 0
        elif key == arcade.key.A:
            self.player.change_x = -MOVEMENT_SPEED
            self.player.angle = 90
        elif key == arcade.key.S:
            self.player.change_y = -MOVEMENT_SPEED
            self.player.angle = 180
        elif key == arcade.key.D:
            self.player.change_x = MOVEMENT_SPEED
            self.player.angle = 270
        elif key == arcade.key.RIGHT:
            self.player.shoot_right_pressed = True
        elif key == arcade.key.UP:
            self.player.shoot_up_pressed = True
        elif key == arcade.key.LEFT:
            self.player.shoot_left_pressed = True
        elif key == arcade.key.DOWN:
            self.player.shoot_down_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.D:
            self.player.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player.shoot_right_pressed = False
        elif key == arcade.key.UP:
            self.player.shoot_up_pressed = False
        elif key == arcade.key.LEFT:
            self.player.shoot_left_pressed = False
        elif key == arcade.key.DOWN:
            self.player.shoot_down_pressed = False

    def spawn_bullet(self, angle_in_deg):
        # only allow bullet to spawn on an interval
        if self.bullet_cooldown < BULLET_COOLDOWN_TICKS:
            return
        self.bullet_cooldown = 0

        bullet = arcade.Sprite("images/laserBlue01.png", 0.75)

        # Position the bullet at the player's current location
        start_x = self.player.center_x
        start_y = self.player.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # angle the bullet visually
        bullet.angle = angle_in_deg
        angle_in_rad = math.radians(angle_in_deg)

        # set bullet's movement direction
        bullet.change_x = math.cos(angle_in_rad) * BULLET_SPEED
        bullet.change_y = math.sin(angle_in_rad) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def on_draw(self):
        # clear screen and start render process
        arcade.start_render()

        # draw game items
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.player.draw()

        # Put the score on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        # Game over message
        if self.game_over:
            arcade.draw_text("Game Over", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 100, width=SCREEN_WIDTH,
                             align="center", anchor_x="center", anchor_y="center")


if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
