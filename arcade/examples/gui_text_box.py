import arcade


class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600)
        self.text = ""
        self.center_x = self.width / 2
        self.center_y = self.height / 2

    def setup(self):
        arcade.set_background_color(arcade.color.AMETHYST)
        self.text_list.append(arcade.gui.Text("Name: ", self.center_x - 225, self.center_y))
        self.textbox_list.append(arcade.gui.TextBox(self.center_x - 125, self.center_y))
        self.button_list.append(arcade.gui.SubmitButton(self.textbox_list[0], self.on_submit, self.center_x,
                                                        self.center_y))

    def on_draw(self):
        arcade.start_render()
        super().on_draw()
        if self.text:
            arcade.draw_text(f"Hello {self.text}", 400, 100, arcade.color.BLACK, 24)

    def on_submit(self):
        self.text = self.textbox_list[0].text_storage.text


def main():
    window = Window()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
