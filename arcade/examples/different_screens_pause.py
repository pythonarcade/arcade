"""
This program shows how to have a pause screen without resetting the game.

Make a seperate class for each screen in your game. The structure will
look like an arcade.Window as each screen will need to have its own draw,
update and window event methods. To switch a screen, simply use the
arcade.set_screen() function and pass it the ClassName of the screen you
want to switch to.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.different_screens_pause
"""

import arcade
import random
import os


file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)


WIDTH = 800
HEIGHT = 600
SPRITE_SCALING = 0.5


class MenuScreen:
    background_color = arcade.color.WHITE

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Menu Screen", WIDTH/2, HEIGHT/2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        arcade.set_screen(GameScreen)


class GameScreen:
    background_color = arcade.color.AMAZON

    def __init__(self):
        self.player_sprite = arcade.Sprite("images/character.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_sprite.velocity = [3, 3]

    def on_draw(self):
        arcade.start_render()
        # Draw all the sprites.
        self.player_sprite.draw()

        # Show tip to pause screen
        arcade.draw_text("Press Esc. to pause",
                         WIDTH/2,
                         HEIGHT-100,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def update(self, delta_time):
        # Call update on all sprites
        self.player_sprite.update()

        # Bounce off the edges
        if self.player_sprite.left < 0 or self.player_sprite.right > WIDTH:
            self.player_sprite.change_x *= -1
        if self.player_sprite.bottom < 0 or self.player_sprite.top > HEIGHT:
            self.player_sprite.change_y *= -1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.set_screen(PauseScreen)


class PauseScreen:
    background_color = arcade.color.ORANGE

    def on_draw(self):
        arcade.set_background_color
        arcade.start_render()
        arcade.draw_text("PAUSED", WIDTH/2, HEIGHT/2+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         WIDTH/2,
                         HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         WIDTH/2,
                         HEIGHT/2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            arcade.set_screen(GameScreen)
        elif key == arcade.key.ENTER:  # reset game
            arcade.set_screen(GameScreen, reset=True)


def main():
    arcade.Window(WIDTH, HEIGHT, "Instruction and Game Over Screens Example")
    arcade.set_screen(MenuScreen)
    arcade.run()


if __name__ == "__main__":
    main()
