import arcade
from arcade import load_texture
from arcade.gui import UIManager, UINinePatchWidget


class MyView(arcade.View):
    def __init__(self):
        super().__init__()

        self.mng = UIManager()

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.nine_patch_widget = UINinePatchWidget(
            width=300,
            height=200,
            texture=load_texture(":resources:gui_basic_assets/window/grey_panel.png"),
            start_point=(10, 10),
            end_point=(190, 190)
        )

        self.nine_patch_widget.center_on_screen()
        self.mng.add(self.nine_patch_widget)

    def on_show_view(self):
        self.window.background_color = arcade.color.WHITE
        self.mng.enable()

    def on_hide_view(self):
        self.mng.disable()

    def on_draw(self):
        self.clear()
        self.mng.draw()


if __name__ == "__main__":
    window = arcade.Window()
    window.show_view(MyView())
    arcade.run()
