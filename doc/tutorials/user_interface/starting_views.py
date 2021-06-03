import arcade


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

    def on_draw(self):
        arcade.start_render()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_hide_view(self):
        pass


if __name__ == "__main__":
    window = arcade.Window(title="ARCADE_GUI")
    window.show_view(MyView(window))
    arcade.run()
