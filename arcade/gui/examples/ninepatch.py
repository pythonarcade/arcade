import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIAnchorLayout, UIWidget, NinePatchTexture


class MyView(arcade.View):
    def __init__(self):
        super().__init__()

        self.mng = UIManager()

        # Setup widget and use background with ninepatch information
        self.nine_patch_widget = UIWidget(size_hint=(0.5, 0.5))
        self.nine_patch_widget.with_background(
            texture=NinePatchTexture(
                texture=load_texture(":resources:gui_basic_assets/window/grey_panel.png"),
                start=(7, 7),
                end=(93, 93),
            )
        )

        self.mng.add(UIAnchorLayout(children=[self.nine_patch_widget]))

    def on_show_view(self):
        self.window.background_color = arcade.color.WHITE
        self.mng.enable()

    def on_hide_view(self):
        self.mng.disable()

    def on_draw(self):
        self.clear()
        self.mng.draw()


if __name__ == "__main__":
    window = arcade.Window(resizable=True)
    window.show_view(MyView())
    arcade.run()
