import arcade
from arcade import View, Window
from arcade.gui import UIImageButton
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UILayoutManager

BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/red_button_normal.png")
HOVERED_TEXTURE = arcade.load_texture(
    ":resources:gui_basic_assets/red_button_hover.png"
)
PRESSED_TEXTURE = arcade.load_texture(
    ":resources:gui_basic_assets/red_button_press.png"
)


class MenuButton(UIImageButton):
    def __init__(self, text):
        super().__init__(
            text=text,
            normal_texture=BUTTON_NORMAL,
            hover_texture=HOVERED_TEXTURE,
            press_texture=PRESSED_TEXTURE,
        )


class MyView(View):
    def __init__(self, window=None):
        super().__init__(window=window)
        self.ui_manager = UILayoutManager(window=window)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

        # Add BoxLayout centered on screen
        menu = self.ui_manager.pack(UIBoxLayout(), center_x=0, center_y=0)

        # add button to menu
        start_button = menu.pack(MenuButton("Start Game"))
        start_button.on_click = self.start_game

        # same code but different syntax
        menu.pack(MenuButton("Settings"), space=20).on_click = self.open_settings

        # Add exit button
        menu.pack(MenuButton("Exit"), space=20).on_click = self.exit_game

        # manually call `do_layout()`, so everything is ready on the first `on_draw()` call
        self.ui_manager.do_layout()

    def start_game(self):
        print("Open GameView")
        # self.window.show_view(GameView())

    def open_settings(self):
        print("Open SettingsView")
        # self.window.show_view(SettingsView())

    def exit_game(self):
        print("Exit game")
        self.window.close()

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.on_draw()


def main():
    window = Window(resizable=True)
    window.show_view(MyView())
    arcade.run()


if __name__ == "__main__":
    main()
