import os
import arcade


class ShowButton(arcade.gui.TextButton):
    def __init__(self, dialoguebox, x, y, width=110, height=50, text="Show", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.dialoguebox = dialoguebox

    def on_press(self):
        if not self.dialoguebox.active:
            self.pressed = True

    def on_release(self):
        if self.pressed:
            self.pressed = False
            self.dialoguebox.active = True


class CloseButton(arcade.gui.TextButton):
    def __init__(self, dialoguebox, x, y, width=110, height=50, text="Close", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.dialoguebox = dialoguebox

    def on_press(self):
        if self.dialoguebox.active:
            self.pressed = True

    def on_release(self):
        if self.pressed and self.dialoguebox.active:
            self.pressed = False
            self.dialoguebox.active = False


class Window(arcade.Window):
    def __init__(self):
        super().__init__()

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.half_width = self.width/2
        self.half_height = self.height/2
        self.theme = None

    def add_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = arcade.gui.DialogueBox(self.half_width, self.half_height, self.half_width*1.1,
                                             self.half_height*1.5, color, self.theme)
        close_button = CloseButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 40,
                                   theme=self.theme)
        dialoguebox.button_list.append(close_button)
        message = "Hello I am a Dialogue Box."
        dialoguebox.text_list.append(arcade.gui.Text(message, self.half_width, self.half_height, self.theme.font_color))
        self.dialogue_box_list.append(dialoguebox)

    def add_text(self):
        message = "Press this button to activate the Dialogue Box"
        self.text_list.append(arcade.gui.Text(message, self.half_width-50, self.half_height))

    def add_button(self):
        show_button = ShowButton(self.dialogue_box_list[0], self.width-100, self.half_height, theme=self.theme)
        self.button_list.append(show_button)

    def set_dialogue_box_texture(self):
        dialogue_box = "gui_themes/Fantasy/DialogueBox/DialogueBox.png"
        self.theme.add_dialogue_box_texture(dialogue_box)

    def set_button_texture(self):
        normal = "gui_themes/Fantasy/Buttons/Normal.png"
        hover = "gui_themes/Fantasy/Buttons/Hover.png"
        clicked = "gui_themes/Fantasy/Buttons/Clicked.png"
        locked = "gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def set_theme(self):
        self.theme = arcade.gui.Theme()
        self.set_dialogue_box_texture()
        self.set_button_texture()
        self.theme.set_font(24, arcade.color.WHITE)

    def setup(self):
        arcade.set_background_color(arcade.color.ALICE_BLUE)
        self.set_theme()
        self.add_dialogue_box()
        self.add_text()
        self.add_button()

    def on_draw(self):
        arcade.start_render()
        super().on_draw()

    def on_update(self, delta_time):
        if self.dialogue_box_list[0].active:
            return


def main():
    window = Window()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
