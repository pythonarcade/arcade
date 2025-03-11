"""
Dual-stick Shooter Example

A dual-analog stick controller is the preferred method of input. If a controller is
not present, the game will fail back to use keyboard controls (WASD to move, arrows to shoot)

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.dual_stick_shooter
"""
import math
import pprint
import random
from typing import cast

import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Dual-stick Shooter Example"
MOVEMENT_SPEED = 4
BULLET_SPEED = 10
BULLET_COOLDOWN_TICKS = 10
ENEMY_SPAWN_INTERVAL = 1
ENEMY_SPEED = 1
STICK_DEADZONE = 0.05
# An angle of "0" means "right", but the player's texture is oriented in the "up" direction.
# So an offset is needed.
ROTATE_OFFSET = -90


def dump_obj(obj):
    for key in sorted(vars(obj)):
        val = getattr(obj, key)
        print("{:30} = {} ({})".format(key, val, type(val).__name__))


def dump_controller(controller):
    print("========== {}".format(controller))
    print("Left X        {}".format(controller.leftx))
    print("Left Y        {}".format(controller.lefty))
    print("Left Trigger  {}".format(controller.lefttrigger))
    print("Right X       {}".format(controller.rightx))
    print("Right Y       {}".format(controller.righty))
    print("Right Trigger {}".format(controller.righttrigger))
    print("========== Extra controller")
    dump_obj(controller)
    print("========== Extra controller.device")
    dump_obj(controller.device)
    print("========== pprint controller")
    pprint.pprint(controller)
    print("========== pprint controller.device")
    pprint.pprint(controller.device)


def dump_controller_state(ticks, controller):
    # print("{:5.2f} {:5.2f} {:>20} {:5}_".format(1.234567, -8.2757272903, "hello", str(True)))
    fmt_str = "{:6d} "
    num_fmts = ["{:5.2f}"] * 6
    fmt_str += " ".join(num_fmts)
    print(fmt_str.format(ticks,
                         controller.leftx,
                         controller.lefty,
                         controller.lefttrigger,
                         controller.rightx,
                         controller.righty,
                         controller.righttrigger,
                         ))


def get_stick_position(x, y):
    """Given position of stick axes, return (x, y, angle_in_degrees).
    If movement is not outside of deadzone, return (None, None, None)"""
    if x > STICK_DEADZONE or x < -STICK_DEADZONE or y > STICK_DEADZONE or y < -STICK_DEADZONE:
        rad = math.atan2(y, x)
        angle = math.degrees(rad)
        return x, y, angle
    return None, None, None


class Player(arcade.sprite.Sprite):
    def __init__(self, filename):
        super().__init__(
            filename,
            scale=0.4,
            center_x=WINDOW_WIDTH / 2,
            center_y=WINDOW_HEIGHT / 2,
        )
        self.shoot_up_pressed = False
        self.shoot_down_pressed = False
        self.shoot_left_pressed = False
        self.shoot_right_pressed = False
        self.start_pressed = False


class Enemy(arcade.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(
            ':resources:images/pinball/bumper.png',
            scale=0.5,
            center_x=x,
            center_y=y,
        )

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


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.game_over = False
        self.score = 0
        self.tick = 0
        self.bullet_cooldown = 0
        self.player = Player(":resources:images/space_shooter/playerShip2_orange.png")
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.controller_manager = arcade.ControllerManager()
        self.controller = None

        self.background_color = arcade.color.DARK_MIDNIGHT_BLUE
        controllers = self.controller_manager.get_controllers()
        for controller in controllers:
            dump_controller(controller)
        if controllers:
            self.connect_controller(controllers[0])
            arcade.window_commands.schedule(self.debug_controller_state, 0.1)

        arcade.window_commands.schedule(self.spawn_enemy, ENEMY_SPAWN_INTERVAL)

        @self.controller_manager.event
        def on_connect(controller):
            if not self.controller:
                self.connect_controller(controller)

        @self.controller_manager.event
        def on_disconnect(controller):
            if self.controller == controller:
                controller.close()
                self.controller = None

    def setup(self):
        self.game_over = False
        self.score = 0
        self.tick = 0
        self.bullet_cooldown = 0
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player.center_x = WINDOW_WIDTH / 2
        self.player.center_y = WINDOW_HEIGHT / 2

    def connect_controller(self, controller):
        self.controller = controller
        self.controller.open()

    def debug_controller_state(self, _delta_time):
        if self.controller:
            dump_controller_state(self.tick, self.controller)

    def spawn_enemy(self, _elapsed):
        if self.game_over:
            return
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        self.enemy_list.append(Enemy(x, y))

    def on_update(self, delta_time):
        self.tick += 1
        if self.game_over:
            if self.controller:
                if self.controller.start:
                    self.setup()
                    return

            if self.player.start_pressed:
                self.setup()
                return

            return

        self.bullet_cooldown += 1

        for enemy in self.enemy_list:
            cast(Enemy, enemy).follow_sprite(self.player)

        if self.controller:
            # Controller input - movement
            move_x, move_y, move_angle = get_stick_position(
                self.controller.leftx, self.controller.lefty
            )
            if move_angle:
                self.player.change_x = move_x * MOVEMENT_SPEED
                self.player.change_y = move_y * MOVEMENT_SPEED
                self.player.angle = move_angle + ROTATE_OFFSET
            else:
                self.player.change_x = 0
                self.player.change_y = 0

            # Controller input - shooting
            shoot_x, shoot_y, shoot_angle = get_stick_position(
                self.controller.rightx, self.controller.righty
            )
            if shoot_angle:
                self.spawn_bullet(shoot_angle)
        else:
            # Keyboard input - shooting
            if self.player.shoot_right_pressed and self.player.shoot_up_pressed:
                self.spawn_bullet(0 + 45)
            elif self.player.shoot_up_pressed and self.player.shoot_left_pressed:
                self.spawn_bullet(90 + 45)
            elif self.player.shoot_left_pressed and self.player.shoot_down_pressed:
                self.spawn_bullet(180 + 45)
            elif self.player.shoot_down_pressed and self.player.shoot_right_pressed:
                self.spawn_bullet(270 + 45)
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
        ship_death_hit_list = arcade.check_for_collision_with_list(self.player,
                                                                   self.enemy_list)
        if len(ship_death_hit_list) > 0:
            self.game_over = True
        for bullet in self.bullet_list:
            bullet_killed = False
            enemy_shot_list = arcade.check_for_collision_with_list(bullet,
                                                                   self.enemy_list)
            # Loop through each colliding sprite, remove it, and add to the score.
            for enemy in enemy_shot_list:
                enemy.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
                bullet_killed = True
                self.score += 1
            if bullet_killed:
                continue

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = MOVEMENT_SPEED
        elif key == arcade.key.A:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.S:
            self.player.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player.change_x = MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.shoot_right_pressed = True
        elif key == arcade.key.UP:
            self.player.shoot_up_pressed = True
        elif key == arcade.key.LEFT:
            self.player.shoot_left_pressed = True
        elif key == arcade.key.DOWN:
            self.player.shoot_down_pressed = True
        # close the window if the user hits the escape key
        elif key == arcade.key.ESCAPE:
            self.window.close()

        rad = math.atan2(self.player.change_y, self.player.change_x)
        self.player.angle = math.degrees(rad) + ROTATE_OFFSET

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

        rad = math.atan2(self.player.change_y, self.player.change_x)
        self.player.angle = math.degrees(rad) + ROTATE_OFFSET

    def spawn_bullet(self, angle_in_deg):
        # only allow bullet to spawn on an interval
        if self.bullet_cooldown < BULLET_COOLDOWN_TICKS:
            return
        self.bullet_cooldown = 0

        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", scale=0.75)

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
        self.clear()

        # draw game items
        self.bullet_list.draw()
        self.enemy_list.draw()
        arcade.draw_sprite(self.player)

        # Put the score on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        # Game over message
        if self.game_over:
            arcade.draw_text("Game Over",
                             WINDOW_WIDTH / 2,
                             WINDOW_HEIGHT / 2,
                             arcade.color.WHITE, 100,
                             width=WINDOW_WIDTH,
                             align="center",
                             anchor_x="center",
                             anchor_y="center")



def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
