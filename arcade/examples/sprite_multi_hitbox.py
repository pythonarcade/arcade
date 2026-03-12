"""
Sprite Multi-Region Hit Boxes

Demonstrates sprites with multiple hit box regions. The player sprite
has a "body" region and a "shield" region extending to one side.
Coins that touch any region of the player are collected.

Hit box outlines are drawn for visual debugging. Use A/D to rotate
the player and see both regions rotate together.

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.sprite_multi_hitbox
"""

import random
import math
import arcade
from arcade.hitbox import HitBox

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Multi-Region Hit Box Example"

PLAYER_SPEED = 5.0
COIN_SPEED = 2.0
COIN_COUNT = 20


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.player_list = None
        self.coin_list = None
        self.score = 0
        self.score_display = None
        self.background_color = arcade.csscolor.DARK_SLATE_GRAY

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.score = 0
        self.score_display = arcade.Text(
            text="Score: 0",
            x=10, y=WINDOW_HEIGHT - 30,
            color=arcade.color.WHITE, font_size=16,
        )

        # Create the player sprite
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.player_sprite = arcade.Sprite(img, scale=0.5)
        self.player_sprite.position = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2

        # Replace the default hitbox with a multi-region hitbox.
        # "body" is a box around the torso, "shield" extends to the right.
        # Collision detection automatically checks all regions.
        self.player_sprite.hit_box = HitBox(
            {
                "body": [(-15, -48), (-15, 40), (15, 40), (15, -48)],
                "shield": [(15, -30), (15, 30), (45, 30), (45, -30)],
            },
            position=self.player_sprite.position,
            scale=self.player_sprite.scale,
            angle=self.player_sprite.angle,
        )

        self.player_list.append(self.player_sprite)
        self._spawn_coins(COIN_COUNT)

    def _spawn_coins(self, count):
        for _ in range(count):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.4)

            # Spawn along a random edge
            side = random.randint(0, 3)
            if side == 0:
                coin.center_x = random.randrange(WINDOW_WIDTH)
                coin.center_y = WINDOW_HEIGHT + 20
            elif side == 1:
                coin.center_x = random.randrange(WINDOW_WIDTH)
                coin.center_y = -20
            elif side == 2:
                coin.center_x = -20
                coin.center_y = random.randrange(WINDOW_HEIGHT)
            else:
                coin.center_x = WINDOW_WIDTH + 20
                coin.center_y = random.randrange(WINDOW_HEIGHT)

            # Aim toward the center with some randomness
            target_x = WINDOW_WIDTH / 2 + random.randint(-200, 200)
            target_y = WINDOW_HEIGHT / 2 + random.randint(-200, 200)
            dx = target_x - coin.center_x
            dy = target_y - coin.center_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                coin.change_x = (dx / dist) * COIN_SPEED
                coin.change_y = (dy / dist) * COIN_SPEED

            self.coin_list.append(coin)

    def on_draw(self):
        self.clear()

        self.coin_list.draw()
        self.player_list.draw()

        # Debug: draw each hitbox region in a different color
        player_hb = self.player_sprite.hit_box
        for region_name in player_hb.region_names:
            pts = player_hb.get_adjusted_points(region_name)
            color = arcade.color.RED if region_name == "body" else arcade.color.CYAN
            arcade.draw_line_strip(tuple(pts) + (pts[0],), color=color, line_width=2)

        self.coin_list.draw_hit_boxes(color=arcade.color.YELLOW, line_thickness=1)
        self.score_display.draw()

        arcade.draw_text(
            "Red = Body  |  Cyan = Shield  |  Arrow keys to move  |  A/D to rotate",
            WINDOW_WIDTH / 2, 20,
            arcade.color.WHITE, font_size=12, anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):
        # Move the player
        if self.up_pressed:
            self.player_sprite.center_y += PLAYER_SPEED
        if self.down_pressed:
            self.player_sprite.center_y -= PLAYER_SPEED
        if self.left_pressed:
            self.player_sprite.center_x -= PLAYER_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += PLAYER_SPEED

        # Rotate with A/D
        keys = self.window.keyboard
        if keys[arcade.key.A]:
            self.player_sprite.angle -= 3.0
        if keys[arcade.key.D]:
            self.player_sprite.angle += 3.0

        # Move coins
        self.coin_list.update()

        # Standard collision check — automatically tests all hitbox regions
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list
        )
        if hit_list:
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1
            self.score_display.text = f"Score: {self.score}"

        # Replace coins that left the screen
        margin = 100
        for coin in list(self.coin_list):
            if (coin.center_x < -margin or coin.center_x > WINDOW_WIDTH + margin
                    or coin.center_y < -margin or coin.center_y > WINDOW_HEIGHT + margin):
                coin.remove_from_sprite_lists()
        if len(self.coin_list) < COIN_COUNT:
            self._spawn_coins(COIN_COUNT - len(self.coin_list))


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
