import arcade

import arcade.gui
from arcade.gui import UIManager


class MyView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window
        self.ui_manager = UIManager(window)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.on_draw()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.ui_manager.purge_ui_elements()
        self.ui_manager.enable()

        box = arcade.gui.UIInputBox(
            text="hello", center_x=400, center_y=300, min_size=(200, 40)
        )
        self.ui_manager.add_ui_element(box)

    def on_hide_view(self):
        self.ui_manager.disable()


if __name__ == "__main__":
    window = arcade.Window(title="ARCADE_GUI")
    view = MyView(window)
    window.show_view(view)
    arcade.run()
