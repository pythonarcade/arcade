import arcade

import arcade.gui
from arcade.gui import UIManager


# TODO Work in progress
class MyView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window
        self.ui_manager = UIManager(window)

    def on_draw(self):
        arcade.start_render()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.ui_manager.purge_ui_elements()

        button_normal = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png')
        hovered_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_hover.png')
        pressed_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_press.png')
        self.ui_manager.add_ui_element(arcade.gui.UIImageButton(
            center_x=self.window.width // 2,
            center_y=window.height // 2,
            normal_texture=button_normal,
            hover_texture=hovered_texture,
            press_texture=pressed_texture,
            text='UIImageButton',
        ))

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView(window))
    arcade.run()
