import arcade

from arcade.gui import UIFlatButton, UIGhostFlatButton, UIManager


class MyView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window
        self.ui_manager = UIManager(window)

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.color.BLACK)

    def on_show_view(self):
        print('on_show_view')
        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()
        self.ui_manager.add_ui_element(UIFlatButton(
            'Hello world',
            center_x=200,
            center_y=self.window.height // 2,
            width=200,
            height=40
        ))

        self.ui_manager.add_ui_element(UIGhostFlatButton(
            'Hello world',
            center_x=600,
            center_y=self.window.height // 2,
            width=200,
            height=40
        ))


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView(window))
    arcade.run()
