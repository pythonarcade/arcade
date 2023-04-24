import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIAnchorLayout, UIWidget, NinePatchTexture


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        # Setup widget and use background with ninepatch information
        self.nine_patch_widget = UIWidget(size_hint=(0.5, 0.5))
        self.nine_patch_widget.with_background(
            texture=NinePatchTexture(
                texture=load_texture(
                    ":resources:gui_basic_assets/window/grey_panel.png"
                ),
                left=7,
                right=7,
                bottom=7,
                top=7,
            )
        )

        self.ui.add(UIAnchorLayout(children=[self.nine_patch_widget]))

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == '__main__':
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
