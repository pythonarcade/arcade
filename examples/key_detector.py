"""
Arcade Key Detector

Shows arcade key constants for pressed keys.
"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
TITLE = "Arcade Key Detector"
BACKGROUND_COLOR = arcade.color.WHITE
TEXT_COLOR = arcade.color.BLACK
FRAMES_PER_SECOND = 25
LINE_HEIGHT = 40


def load_arcade_key_dict():
    file = open(arcade.key.__file__)
    result = dict()
    for line in file:
        parts = line.replace('\n', '').replace(' ', '').split('=')
        if len(parts) == 2:
            key = int(parts[1])
            name = parts[0]
            if key in result:
                result[key] = result[key] + ', ' + name
            else:
                result[key] = name

    file.close()
    return result


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.key_dict = load_arcade_key_dict()
        arcade.set_background_color(BACKGROUND_COLOR)


    def on_draw(self):
        arcade.start_render()
        y = SCREEN_HEIGHT - LINE_HEIGHT
        for pressed_key in self.pressed_keys:
            if pressed_key in self.key_dict:
                text = self.key_dict[pressed_key]
            else:
                text = 'unknown key (' + str(pressed_key) + ')'

            arcade.draw_text(text, 20, y, TEXT_COLOR, font_size=20)
            y = y - LINE_HEIGHT

        return


def main():
    MyWindow()
    arcade.run()
    return


if __name__ == "__main__":
    main()
