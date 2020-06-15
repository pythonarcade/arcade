"""
GUI Button

Simple program to show basic sprite usage.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_button
"""
import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Button Example"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Set window background
        arcade.set_background_color(arcade.color.AMAZON)

        # Variable that will hold state of game (pause/play)
        self.pause = False

        # Parameters of running text
        self.text = "Graphical User Interface"
        self.text_x = 0
        self.text_y = 300
        self.text_font_size = 40
        self.speed = 1

        # Theme of GUI elements
        self.theme = None

    def setup(self):
        """
        Set up the game.
        """
        self.setup_theme()
        self.set_buttons()

    def setup_theme(self):
        """
        Set up theme of GUI elements.
        """

        # Create theme
        self.theme = arcade.gui.Theme()

        # Set up font color of theme
        self.theme.font.color = arcade.color.WHITE

        # Set up textures of buttons
        normal = ":resources:gui_themes/Fantasy/Buttons/Normal.png"
        hover = ":resources:gui_themes/Fantasy/Buttons/Hover.png"
        clicked = ":resources:gui_themes/Fantasy/Buttons/Clicked.png"
        locked = ":resources:gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def set_buttons(self):
        """
        Set up buttons.
        """

        # Create play button
        play_button = arcade.gui.TextButton(60, 570, 110, 50, "Play",
                                            theme=self.theme)
        # Set up function, that will be execute when the button be clicked
        play_button.click_action = self.resume_program
        # Add play button in list of buttons
        self.button_list.append(play_button)

        # Create stop button
        stop_button = arcade.gui.TextButton(60, 515, 110, 50, "Pause",
                                            theme=self.theme)
        # Set up function, that will be execute when the button be clicked
        stop_button.click_action = self.pause_program
        # Add stop button in list of buttons
        self.button_list.append(stop_button)

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()
        super().on_draw()

        # Draw the running text
        arcade.draw_text(self.text, self.text_x, self.text_y, arcade.color.ALICE_BLUE, self.text_font_size)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if not self.pause:
            if self.text_x < 0 or self.text_x > self.width:
                self.speed = -self.speed
            self.text_x += self.speed

    def pause_program(self):
        """
        Stop the game.
        """
        self.pause = True

    def resume_program(self):
        """
        Resume the game.
        """
        self.pause = False


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
