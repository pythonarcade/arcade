import arcade

import arcade.gui
from arcade import load_texture
from arcade.gui import UIManager, UIImageToggle


class MyView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window
        self.ui_manager = UIManager(window)

    def on_draw(self):
        arcade.start_render()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.ui_manager.purge_ui_elements()

        screen_switch = UIImageToggle(
            true_texture=load_texture(':resources:gui_basic_assets/icons/smaller.png'),
            false_texture=load_texture(':resources:gui_basic_assets/icons/larger.png'),
            center_x=self.window.width // 2,
            center_y=self.window.height // 2,
            value=False
        )
        self.ui_manager.add_ui_element(screen_switch)

        @screen_switch.event
        def on_toggle(value: bool):
            if value:
                self.window.set_fullscreen(True)
            else:
                self.window.set_fullscreen(False)

            # Recenter
            screen_switch.position = self.window.width // 2, self.window.height // 2

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()


if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    window.show_view(MyView(window))
    arcade.run()
