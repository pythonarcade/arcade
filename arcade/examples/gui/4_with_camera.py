"""This example shows how to use arcade.gui with a camera.
It is a simple game where the player can move around and collect coins.
The player can upgrade their speed and the spawn rate of the coins.
The game has a timer and ends after 60 seconds.
The game is controlled with the arrow keys or WASD.

At the beginning of the game, the UI camera is used, to apply some animations.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.4_with_camera
"""

import math
import random

import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UILabel, UIOnClickEvent, UIView

COIN_PNG = ":resources:images/items/coinGold.png"
ADV_PNG = ":resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png"


class MyCoinGame(UIView):
    """Main view of the game. This class is a subclass of UIView, which provides
    basic GUI setup. We add UIManager to the view under `self.ui`.

    The example showcases how to:
    - use UIView to set up a basic GUI
    - add a button to the view and connect it to a function
    - use camera to move the view

    """

    def __init__(self):
        super().__init__()
        self.bg_color = arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE

        # basic camera setup
        self.keys = set()
        self.in_game_camera = arcade.Camera2D()
        self.in_game_camera.bottom_left = 100, 100

        # in-game counter
        self._total_time = 0
        self._game_duration = 60
        self._game_over = False
        self._last_coin_spawn = 0
        self._coin_spawn_delay = 3
        self._coins_collected = 0

        # upgradable player values
        self._player_speed = 5

        # setup in-game objects
        self.sprites = arcade.SpriteList()

        self.game_area = arcade.SpriteSolidColor(
            width=1300,
            height=730,
            color=arcade.color.GRAY_ASPARAGUS,
            center_x=1280 / 2,
            center_y=720 / 2,
        )

        self.sprites.append(self.game_area)

        self.player = arcade.Sprite(
            ADV_PNG,
            scale=0.5,
            center_x=1280 / 2,
            center_y=720 / 2,
        )
        self.sprites.append(self.player)

        self.coins = arcade.SpriteList()
        for i in range(12):
            # place coins in a circle around the player, radius =100
            coin = arcade.Sprite(
                COIN_PNG,
                scale=0.5,
                center_x=1280 / 2 + 200 * math.cos(math.radians(i * 40)),
                center_y=720 / 2 + 200 * math.sin(math.radians(i * 40)),
            )
            self.coins.append(coin)

        # UI setup, we use UIView, which automatically adds UIManager as self.ui
        anchor = self.ui.add(UIAnchorLayout())

        shop_buttons = anchor.add(
            UIBoxLayout(vertical=False, space_between=10),
            anchor_x="center",
            anchor_y="bottom",
            align_y=10,
        )

        # speed upgrade button
        speed_upgrade = UIFlatButton(text="Upgrade Speed (5C)", width=200, height=40)
        shop_buttons.add(speed_upgrade)

        @speed_upgrade.event("on_click")
        def upgrade_speed(event: UIOnClickEvent):
            cost = self._player_speed
            if self._coins_collected >= cost:
                self._coins_collected -= cost
                self._player_speed += 1
                speed_upgrade.text = f"Update Speed ({self._player_speed}C)"
                print("Speed upgraded")

        # update spawn rate button
        spawn_rate_upgrade = UIFlatButton(text="Upgrade spawn rate: 10C", width=300, height=40)
        shop_buttons.add(spawn_rate_upgrade)

        @spawn_rate_upgrade.event("on_click")
        def upgrade_spawn_rate(event: UIOnClickEvent):
            cost = 10
            if self._coins_collected >= cost:
                self._coins_collected -= cost
                self._coin_spawn_delay -= 0.5
                print("Spawn rate upgraded")

        # position top center, with a 40px offset
        self.out_of_game_area = anchor.add(
            UILabel(text="Out of game area", font_size=32),
            anchor_x="center",
            anchor_y="top",
            align_y=-40,
        )
        self.out_of_game_area.visible = False

        self.coin_counter = anchor.add(
            UILabel(text="Collected coins 0", size_hint=(0, 0)),
            anchor_x="left",
            anchor_y="top",
            align_y=-10,
            align_x=10,
        )
        self.coin_counter.with_background(
            color=arcade.color.TRANSPARENT_BLACK
            # giving a background will make the label way more performant,
            # because it will not re-render the whole UI after a text change
        )

        # Game timer
        self.timer = anchor.add(
            UILabel(
                text="Time 30.0",
                font_size=15,
                size_hint=(0, 0),  # take the whole width to prevent linebreaks
            ),
            anchor_x="center",
            anchor_y="top",
            align_y=-10,
            align_x=-10,
        )
        self.timer.with_background(color=arcade.color.TRANSPARENT_BLACK)

        self.cam_pos = self.ui.camera.position

    def on_draw_before_ui(self):
        self.in_game_camera.use()  # use the in-game camera to draw in-game objects
        self.sprites.draw()
        self.coins.draw()

    def on_update(self, delta_time: float) -> bool | None:
        if self._total_time > self._game_duration:
            # ad new UI label to show the end of the game
            game_over_text = self.ui.add(
                UILabel(
                    text="End of game!\n"
                    f"You achieved {self._coins_collected} coins!\n"
                    "Press ESC to exit.\n"
                    "Use ENTER to restart.",
                    font_size=32,
                    bold=True,
                    multiline=True,
                    align="center",
                    text_color=arcade.color.WHITE,
                    size_hint=(0, 0),
                ),
            )
            game_over_text.with_padding(all=10)
            game_over_text.with_background(color=arcade.types.Color(50, 50, 50, 120))
            game_over_text.center_on_screen()

            return True

        self._total_time += delta_time
        self._last_coin_spawn += delta_time

        # update the timer
        self.timer.text = f"Time {self._game_duration - self._total_time:.1f}"

        # spawn new coins
        if self._last_coin_spawn > self._coin_spawn_delay:
            coin = arcade.Sprite(
                COIN_PNG,
                scale=0.5,
                center_x=random.randint(0, 1280),
                center_y=random.randint(0, 720),
            )
            self.coins.append(coin)
            self._last_coin_spawn -= self._coin_spawn_delay

        # move the player sprite
        if {arcade.key.LEFT, arcade.key.A} & self.keys:
            self.player.left -= self._player_speed
        if {arcade.key.RIGHT, arcade.key.D} & self.keys:
            self.player.left += self._player_speed
        if {arcade.key.UP, arcade.key.W} & self.keys:
            self.player.top += self._player_speed
        if {arcade.key.DOWN, arcade.key.S} & self.keys:
            self.player.top -= self._player_speed

        # move the camera with the player
        self.in_game_camera.position = self.player.position

        # collect coins
        collisions = self.player.collides_with_list(self.coins)
        for coin in collisions:
            coin.remove_from_sprite_lists()
            self._coins_collected += 1
            print("Coin collected")

        # update the coin counter
        self.coin_counter.text = f"Collected coins {self._coins_collected}"

        # inform player if they are out of the game area
        if not self.player.collides_with_sprite(self.game_area):
            self.out_of_game_area.visible = True
        else:
            self.out_of_game_area.visible = False

        # slide in the UI from bottom, until total time reaches 2 seconds
        progress = min(1.0, self._total_time / 2)

        # Because we allow for camera rotation we have work in the center
        # and not the edge because it behaves oddly otherwise
        cam_pos_x = self.window.center_x
        cam_pos_y = 50 * (1 - progress) + self.window.center_y
        self.ui.camera.position = (cam_pos_x, cam_pos_y)

        return False

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        self.keys.add(symbol)

        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol == arcade.key.ENTER:
            self.window.show_view(MyCoinGame())

        return False

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if symbol in self.keys:
            self.keys.remove(symbol)
        return False


def main():
    window = arcade.Window(1280, 720, "GUI Example: Coin Game (Camera)", resizable=False)
    window.show_view(MyCoinGame())
    window.run()


if __name__ == "__main__":
    main()
