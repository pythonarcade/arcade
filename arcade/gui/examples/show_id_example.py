from typing import cast

import arcade
from arcade.gui import UILabel, UIClickable, UIInputBox, UIEvent, UIFlatButton, UIManager


class MyView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window
        self.ui_manager = UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)

    def on_draw(self):
        arcade.start_render()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.ui_manager.purge_ui_elements()

        self.ui_manager.add_ui_element(UILabel(
            text='Username:',
            center_x=100,
            center_y=self.window.height // 2,
            width=300,
            height=40,
        ))
        self.ui_manager.add_ui_element(UIInputBox(
            center_x=350,
            center_y=self.window.height // 2,
            width=300,
            height=40,
            id='username'
        ))
        self.ui_manager.add_ui_element(UIFlatButton(
            text='Login',
            center_x=650,
            center_y=self.window.height // 2,
            width=200,
            height=40,
            id='submit_button'
        ))

        self.ui_manager.add_ui_element(UILabel(
            text='',
            center_x=self.window.width // 2,
            center_y=self.window.height // 2 - 100,
            width=600,
            height=40,
            id='login_message'
        ))

    def on_ui_event(self, event: UIEvent):
        if event.type == UIClickable.CLICKED and event.get('ui_element').id == 'submit_button':
            # Trigger action if 'submit_button' was clicked
            self.submit()
        elif event.type == UIInputBox.ENTER and event.get('ui_element').id == 'username':
            # Trigger action if ENTER pressed in 'username'-UIInputBox
            self.submit()

    def submit(self):
        username_input = cast(UIInputBox, self.ui_manager.find_by_id('username'))
        username = username_input.text

        login_message: UILabel = cast(UILabel, self.ui_manager.find_by_id('login_message'))
        login_message.text = f'Welcome {username}, you are my first player.'

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView(window))
    arcade.run()
