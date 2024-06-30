"""
Creating a dropdown menu with UIDropDown

When an option in the UIDropDown is chosen, this example will respond
by changing the text displayed on screen to reflect it.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.dropdown
"""

from __future__ import annotations

import arcade
from arcade.gui import UIManager, UILabel, UIOnChangeEvent
from arcade.gui.widgets.dropdown import UIDropdown


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.dropdown = UIDropdown(
            default="Platformer",
            options=["Arcade", UIDropdown.DIVIDER, "Platformer", "Jump and Run"],
            height=50,
            width=200,
        )
        self.dropdown.center_on_screen()
        self.ui.add(self.dropdown)

        self.label = self.ui.add(UILabel(text=" ", text_color=(0, 0, 0)))

        @self.dropdown.event()
        def on_change(event: UIOnChangeEvent):
            print(f"Value changed from '{event.old_value}' to '{event.new_value}'")
            self.label.text = f"Value changed from '{event.old_value}' to '{event.new_value}'"
            self.label.fit_content()

            # place label above dropdown
            self.label.center_on_screen()
            self.label.move(dy=50)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
