"""
This example shows how to programmatically change the GUI style.

You can run this example with:
python -m arcade.examples.gui_custom_style

This can also be done with a yaml file.
See:
https://github.com/pvcraven/arcade/blob/development/arcade/resources/style/default.yml
and the UIStyle.from_file() command.
"""
import arcade

import arcade.gui
from arcade.gui import UIFlatButton, UIGhostFlatButton, UIManager
from arcade.gui.ui_style import UIStyle


class MyView(arcade.View):
    """ Main program view """

    def __init__(self):
        """ Set up this view """
        super().__init__()

        self.ui_manager = UIManager()

    def setup(self):
        """ Setup the view """
        self.ui_manager.purge_ui_elements()
        flat = UIFlatButton('Hello world', center_x=200, center_y=self.window.height // 2, width=200, height=40)
        flat.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(51, 139, 57),
            bg_color_hover=(51, 139, 57),
            bg_color_press=(28, 71, 32),
            border_color=(51, 139, 57),
            border_color_hover=arcade.color.WHITE,
            border_color_press=arcade.color.WHITE
        )
        self.ui_manager.add_ui_element(flat)

        # creates a new class, which will match the id
        UIStyle.default_style().set_class_attrs(
            'right_button',
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(135, 21, 25),
            bg_color_hover=(135, 21, 25),
            bg_color_press=(122, 21, 24),
            border_color=(135, 21, 25),
            border_color_hover=arcade.color.WHITE,
            border_color_press=arcade.color.WHITE
        )
        self.ui_manager.add_ui_element(UIGhostFlatButton(
            'Hello world',
            center_x=600,
            center_y=self.window.height // 2,
            width=200,
            height=40,
            id='right_button'
        ))

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.set_background_color(arcade.color.BLACK)

    def on_show_view(self):
        """ Show this view """
        self.setup()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView())
    arcade.run()
