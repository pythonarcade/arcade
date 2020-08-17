"""
GUI Dialogue Box

Simple program to show basic dialogue box usage.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_dialogue_box
"""
import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Button Example"


class Window(arcade.Window):
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

        self.half_width = self.width/2
        self.half_height = self.height/2

        # Set window background
        arcade.set_background_color(arcade.color.BABY_BLUE_EYES)

        # Theme of GUI elements
        self.theme = None

        self.dialogue_box = None
        self.show_button = None

    def setup(self):
        """
        Set up the game.
        """
        self.setup_theme()
        self.add_dialogue_box()
        self.add_show_button()

    def setup_theme(self):
        """
        Set up theme of GUI elements.
        """
        self.theme = arcade.gui.Theme()

        # Set up font color of theme
        self.theme.font.color = arcade.color.WHITE

        # Set up texture of dialogue box
        self.theme.add_dialogue_box_texture(
            ":resources:gui_themes/Fantasy/DialogueBox/DialogueBox.png"
        )

        # Set up textures of buttons
        normal = ":resources:gui_themes/Fantasy/Buttons/Normal.png"
        hover = ":resources:gui_themes/Fantasy/Buttons/Hover.png"
        clicked = ":resources:gui_themes/Fantasy/Buttons/Clicked.png"
        locked = ":resources:gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def add_dialogue_box(self):
        """
        Add dialogue box
        """
        color = (220, 228, 255)
        # Create dialogue box
        self.dialogue_box = arcade.gui.DialogueBox(self.half_width,
                                                   self.half_height,
                                                   self.half_width * 1.1,
                                                   self.half_height * 1.5,
                                                   color, self.theme)

        x_button = self.dialogue_box.x
        y_button = self.dialogue_box.y + self.dialogue_box.height / 2 - 41
        # Create close button
        close_button = arcade.gui.TextButton(x_button, y_button,
                                             width=110, height=50,
                                             text="Close", theme=self.theme)
        # Set up function, that will be execute when the button be clicked
        close_button.click_action = self.switch_state_dialogue_box
        # Add the button in list of dialogue box buttons
        self.dialogue_box.button_list.append(close_button)

        # Create a text label for dialogue box
        label = arcade.gui.TextLabel("Hello I am a Dialogue Box",
                                     self.half_width, self.half_height)
        # Add the label in list of dialogue box text items
        self.dialogue_box.text_list.append(label)

        # Add the dialogue box in list of dialogue boxes of the game for render
        self.dialogue_box_list.append(self.dialogue_box)

    def add_show_button(self):
        """
        Add show button
        """
        x_button = self.dialogue_box.x
        y_button = self.dialogue_box.y + self.dialogue_box.height / 2 - 41
        # Create show button
        self.show_button = arcade.gui.TextButton(x_button, y_button,
                                                 width=110, height=50,
                                                 text="Show", theme=self.theme)
        # Set up function, that will be execute when the button be clicked
        self.show_button.click_action = self.switch_state_dialogue_box

        # Add the button in list of game buttons for render
        self.button_list.append(self.show_button)

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()
        super().on_draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        pass

    def switch_state_dialogue_box(self):
        """
        Switch active status of dialogue box and show button
        """
        if self.dialogue_box.active:
            self.dialogue_box.active = False
            self.show_button.active = True
        else:
            self.dialogue_box.active = True
            self.show_button.active = False


def main():
    window = Window()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
