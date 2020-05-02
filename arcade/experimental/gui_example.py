"""
Starting Template Simple

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template_simple
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Example"

arcade.configure_logging()

class MyClickableText(arcade.experimental.gui.ClickableText):
    def __init__(self, center_x:float, center_y:float, text:str):
        super().__init__(center_x=center_x,
                         center_y=center_y,
                         text_color=arcade.color.GRAY,
                         text_color_mouse_over=arcade.color.WHITE,
                         font_size=20,
                         text=text)

    def on_click(self):
        print("Click!")


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        theme = arcade.experimental.gui.Theme(
            text_color=arcade.color.WHITE,
            font_size=12,
            font_name=('calibri', 'arial'),

            background_color=(20, 20, 20),
            border_color=(20, 20, 20),
            border_width=1,

            text_color_mouse_over=arcade.color.WHITE,
            border_color_mouse_over=arcade.color.WHITE,
            background_color_mouse_over=(20, 20, 20),

            background_color_mouse_press=arcade.color.WHITE,
            text_color_mouse_press=arcade.color.BLACK,
            border_color_mouse_press=arcade.color.WHITE,
        )
        for i in range(9):
            ui_element = MyClickableText(center_x=350,
                                         center_y=570 - (40 * i),
                                         text=f"Can't stop the signal {i + 1}")
            self.ui_manager.append(ui_element)

        for i in range(7):
            ui_element = arcade.experimental.gui.FlatTextButton(center_x=100,
                                                                center_y=560 - (50 * i),
                                                                width=150,
                                                                height=40,
                                                                text=f"Option {i + 1}",
                                                                theme=theme)
            self.ui_manager.append(ui_element)

        for i in range(10):
            for j in range(10):
                ui_element = arcade.experimental.gui.FlatButton(center_x=550 + i * 20,
                                                                center_y=400 + j * 20,
                                                                width=15,
                                                                height=15,
                                                                theme=theme)
                self.ui_manager.append(ui_element)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()

        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        print("Click Window")


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
