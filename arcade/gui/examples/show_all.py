"""
Example showing GUI elements
"""
import arcade

import arcade.gui
from arcade.gui import UIManager


class MyView(arcade.View):
    """ View for this example """
    def __init__(self, my_window: arcade.Window):
        super().__init__()

        self.window = my_window
        self.ui_manager = UIManager(my_window)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()

    def on_show_view(self):
        """ Show main view """
        arcade.set_background_color(arcade.color.BLACK)
        self.ui_manager.purge_ui_elements()

        y_slot = self.window.height // 4

        # left
        self.ui_manager.add_ui_element(arcade.gui.UILabel(
            'UILabel',
            center_x=self.window.width // 4,
            center_y=y_slot * 3,
        ))

        ui_input_box = arcade.gui.UIInputBox(
            center_x=self.window.width // 4,
            center_y=y_slot * 2,
            width=300
        )
        ui_input_box.text = 'UIInputBox'
        ui_input_box.cursor_index = len(ui_input_box.text)
        self.ui_manager.add_ui_element(ui_input_box)

        button_normal = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png')
        hovered_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_hover.png')
        pressed_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_press.png')
        self.ui_manager.add_ui_element(arcade.gui.UIImageButton(
            center_x=self.window.width // 4,
            center_y=y_slot * 1,
            normal_texture=button_normal,
            hover_texture=hovered_texture,
            press_texture=pressed_texture,
            text='UIImageButton'
        ))

        # right
        self.ui_manager.add_ui_element(arcade.gui.UIFlatButton(
            'FlatButton',
            center_x=self.window.width // 4 * 3,
            center_y=y_slot * 1,
            width=250,
            # height=20
        ))
        self.ui_manager.add_ui_element(arcade.gui.UIGhostFlatButton(
            'GhostFlatButton',
            center_x=self.window.width // 4 * 3,
            center_y=y_slot * 2,
            width=250,
            # height=20
        ))

        self.ui_manager.add_ui_element(arcade.gui.UIToggle(
            center_x=self.window.width // 4 * 3 - 60,
            center_y=y_slot * 3,
            height=30,
            value=False
        ))
        self.ui_manager.add_ui_element(arcade.gui.UIToggle(
            center_x=self.window.width // 4 * 3 + 60,
            center_y=y_slot * 3,
            height=30,
            value=True
        ))

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView(window))
    arcade.run()
