from arcade.gui import *

import os

class PlayButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Play", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False


class PauseButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Pause", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = True
            self.pressed = False


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "GUI Text Buton Example")

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)
        self.pause = False
        self.text = "Graphical User Interface"
        self.text_x = 0
        self.text_y = 300
        self.text_font_size = 40
        self.speed = 1
        self.theme = None

    def set_button_textures(self):
        normal = "gui_themes/Fantasy/Buttons/Normal.png"
        hover = "gui_themes/Fantasy/Buttons/Hover.png"
        clicked = "gui_themes/Fantasy/Buttons/Clicked.png"
        locked = "gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def setup_theme(self):
        self.theme = Theme()
        self.theme.set_font(24, arcade.color.WHITE)
        self.set_button_textures()

    def set_buttons(self):
        self.button_list.append(PlayButton(self, 60, 570, 110, 50, theme=self.theme))
        self.button_list.append(PauseButton(self, 60, 515, 110, 50, theme=self.theme))

    def setup(self):
        self.setup_theme()
        self.set_buttons()

    def on_draw(self):
        arcade.start_render()
        super().on_draw()
        arcade.draw_text(self.text, self.text_x, self.text_y, arcade.color.ALICE_BLUE, self.text_font_size)

    def update(self, delta_time):
        if self.pause:
            return

        if self.text_x < 0 or self.text_x > self.width:
            self.speed = -self.speed
        self.text_x += self.speed


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
