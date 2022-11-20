from arcade.gui.events import UIOnChangeEvent

from arcade import View, load_texture, Window
from arcade.gui import UIManager, UIAnchorLayout
from arcade.gui.widgets.toggle import UITextureToggle


class MyView(View):
    def __init__(self):
        super().__init__()

        self.mng = UIManager()

        on_texture = load_texture(":resources:gui_basic_assets/toggle/switch_green.png")
        off_texture = load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
        self.toggle = UITextureToggle(on_texture=on_texture, off_texture=off_texture)

        # Add toggle to UIManager, use UIAnchorLayout to center on screen
        self.mng.add(UIAnchorLayout(children=[self.toggle]))

        # Listen for value changes
        @self.toggle.event("on_change")
        def print_oon_change(event: UIOnChangeEvent):
            print(f"New value {event.new_value}")

    def on_show_view(self):
        self.mng.enable()

    def on_hide_view(self):
        self.mng.disable()

    def on_draw(self):
        self.mng.draw()


if __name__ == "__main__":
    window = Window()
    window.show_view(MyView())
    window.run()
