import arcade
from arcade.gui import ActionButton


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Text Buton Example"


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

        play_button = ActionButton(
            60, 570, 100, 40, "Play", 18, "Arial", self.resume_program)
        self.button_list.append(play_button)

        pause_button = ActionButton(
            60, 515, 100, 40, "Pause", 18, "Arial", self.pause_program)
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

    def on_mouse_press(self, x, y, button, key_modifiers):
        for button in self.button_list:
            button.check_mouse_press(x, y)

    def on_mouse_release(self, x, y, button, key_modifiers):
        for button in self.button_list:
            button.check_mouse_release(x, y)

    def pause_program(self):
        self.pause = True

    def resume_program(self):
        self.pause = False


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
