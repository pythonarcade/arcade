import arcade
from arcade.gui import TextBox


class Window(arcade.Window):
    def __init__(self):
        super().__init__(1280, 720)
        self.center_x = self.width / 2
        self.center_y = self.height / 2

    def setup(self):
        arcade.set_background_color(arcade.color.ALICE_BLUE)
        self.textbox_list.append(TextBox(self.center_x, self.center_y))
    
    def on_draw(self):
        arcade.start_render()
        super().on_draw()

def main():
    window = Window()
    window.setup()
    arcade.run()


if __name__=="__main__":
    main()
