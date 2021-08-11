"""
Example code showing how to create a button,
and the three ways to process button events.
"""
import arcade
from arcade.gui import UIManager
from arcade.gui.events import UIOnClickEvent
from arcade.gui.widgets import UIAnchorWidget, UIBoxGroup, UIFlatButton


# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(UIFlatButton):
    def on_click(self, event: UIOnClickEvent):
        arcade.exit()


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UIFlatButton Example", resizable=True)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = UIBoxGroup()

        # Create the buttons
        start_button = UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = UIFlatButton(text="Settings", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        # --- Method 2 for handling click events,
        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start

        # --- Method 3 for handling click events,
        # use a decorator to handle on_click events
        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Settings:", event)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_click_start(self, event):
        print("Start:", event)

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()


window = MyWindow()
arcade.run()
