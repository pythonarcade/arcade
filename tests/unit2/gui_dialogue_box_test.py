import arcade
from arcade.gui import DialogueBox, TextButton, Text


class ShowButton(TextButton):
    def __init__(self, dialoguebox, x, y, width=100, height=40, text="Show"):
        super().__init__(x, y, width, height, text)
        self.dialoguebox = dialoguebox

    def on_press(self):
        if not self.dialoguebox.active:
            self.pressed = True

    def on_release(self):
        if self.pressed:
            self.pressed = False
            self.dialoguebox.active = True


class CloseButton(TextButton):
    def __init__(self, dialoguebox, x, y, width=100, height=40, text="Close"):
        super().__init__(x, y, width, height, text)
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
        self.half_width = self.width/2
        self.half_height = self.height/2

    def add_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = DialogueBox(self.half_width, self.half_height, self.half_width, self.half_height, color)
        close_button = CloseButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 40)
        dialoguebox.button_list.append(close_button)
        message = "Hello I am a Dialogue Box."
        dialoguebox.text_list.append(Text(message, self.half_width, self.half_height+100))
        self.dialogue_box_list.append(dialoguebox)

    def add_text(self):
        message = "Press this button to activate the Dialogue Box"
        self.text_list.append(Text(message, self.half_width-50, self.half_height))

    def add_button(self):
        show_button = ShowButton(self.dialogue_box_list[0], self.width-100, self.half_height)
        self.button_list.append(show_button)

    def setup(self):
        arcade.set_background_color(arcade.color.ALICE_BLUE)
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


if __name__=="__main__":
    main()
