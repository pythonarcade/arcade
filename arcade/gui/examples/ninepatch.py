import arcade
from arcade import load_texture
from arcade.gui import UIManager, UINinePatchWidget, UIAnchorLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()

        self.mng = UIManager()

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.nine_patch_widget = UINinePatchWidget(
            texture=load_texture(":resources:gui_basic_assets/window/grey_panel.png"),
            start_point=(5, 5),
            end_point=(95, 95),
            size_hint=(0.5, 0.5),
        )

        self.mng.add(UIAnchorLayout(children=[self.nine_patch_widget]))

    def on_show_view(self):
        self.window.background_color = arcade.color.WHITE
        self.mng.enable()

    def on_key_press(self, symbol: int, modifiers: int):
        print(self.nine_patch_widget.width)

    def on_hide_view(self):
        self.mng.disable()

    def on_draw(self):
        self.clear()
        self.mng.draw()


if __name__ == "__main__":
    window = arcade.Window(resizable=True)
    window.show_view(MyView())
    arcade.run()
