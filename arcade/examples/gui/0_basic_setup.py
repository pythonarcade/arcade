"""Demonstrates general setup.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.0_basic_setup

Content:
- create a view manually creating UIManager and adding widgets
- create a second view extending UIView and adding widgets

"""

import arcade
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIAnchorLayout,
    UIView,
)

# Preload textures, because they are mostly used multiple times, so they are not
# loaded multiple times
TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")


class GreenView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        # Create a UIManager
        self.ui = UIManager()

        # Create an anchor layout, which can be used to position widgets on screen
        anchor = self.ui.add(UIAnchorLayout())

        # Add a button switch to the other View.
        button = anchor.add(
            UITextureButton(
                text="Switch to blue view",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
            )
        )

        # add a button to switch to the blue view
        @button.event("on_click")
        def on_click(event):
            self.window.show_view(BlueView())

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self):
        # Clear the screen
        self.clear(color=arcade.uicolor.GREEN_EMERALD)

        # Add draw commands that should be below the UI
        # ...

        self.ui.draw()

        # Add draw commands that should be on top of the UI (uncommon)
        # ...


class BlueView(UIView):
    """Uses the arcade.gui.UIView which takes care about the UIManager setup."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_PETER_RIVER

        # Create an anchor layout, which can be used to position widgets on screen
        anchor = self.add_widget(UIAnchorLayout())

        # Add a button switch to the other View.
        button = anchor.add(
            UITextureButton(
                text="Switch to green view",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
            )
        )

        # add a button to switch to the green view
        @button.event("on_click")
        def on_click(event):
            self.window.show_view(GreenView())

    def on_draw_before_ui(self):
        # Add draw commands that should be below the UI
        pass

    def on_draw_after_ui(self):
        # Add draw commands that should be on top of the UI (uncommon)
        pass


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(title="GUI Example: Basic Setup")

    # Show the view on screen
    window.show_view(GreenView())

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()
