import arcade
from arcade.gui import TextButton


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Text Buton Example"


class PlayButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Play"):
        super().__init__(x, y, width, height, text)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False


class PauseButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Pause"):
        super().__init__(x, y, width, height, text)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = True
            self.pressed = False


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.pause = False
        self.text = "Graphical User Interface"
        self.text_x = 0
        self.text_y = 300
        self.text_font_size = 40
        self.speed = 1
        self.button_list = None

    def setup(self):
        self.button_list = []

        play_button = PlayButton(self, 60, 570, 100, 40)
        pause_button = PauseButton(self, 60, 515, 100, 40)

        self.button_list.append(play_button)
        self.button_list.append(pause_button)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(self.text, self.text_x, self.text_y,
                         arcade.color.ALICE_BLUE, self.text_font_size)
        for button in self.button_list:
            button.draw()

    def update(self, delta_time):
        if self.pause:
            return

        if self.text_x < 0 or self.text_x > SCREEN_WIDTH:
            self.speed = -self.speed
        self.text_x += self.speed

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
