import arcade
from arcade.gui import UIManager, UILabel, UIOnChangeEvent
from arcade.gui.widgets.dropdown import UIDropdown


class MyView(arcade.View):
    def __init__(self):
        super().__init__()

        self.mng = UIManager()

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.dropdown = UIDropdown(
            default="Platformer",
            options=["Arcade", None, "Platformer", "Jump and Run"],
            height=50,
            width=200,
        )
        self.dropdown.center_on_screen()
        self.mng.add(self.dropdown)

        self.label = self.mng.add(UILabel(text=" ", text_color=(0, 0, 0)))

        @self.dropdown.event()
        def on_change(event: UIOnChangeEvent):
            print(f"Value changed from '{event.old_value}' to '{event.new_value}'")
            self.label.text = (
                f"Value changed from '{event.old_value}' to '{event.new_value}'"
            )
            self.label.fit_content()

            # place label above dropdown
            self.label.center_on_screen()
            self.label.move(dy=50)

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
