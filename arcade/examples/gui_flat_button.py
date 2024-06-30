"""
Example code showing how to create a button,
and the three ways to process button events.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_flat_button
"""
import arcade
import arcade.gui

# --- Method 1 for handling click events,
# Create a child class.
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout


class QuitButton(arcade.gui.widgets.buttons.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.ui = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        # Create the buttons
        start_button = arcade.gui.widgets.buttons.UIFlatButton(
            text="Start Game", width=200
        )
        self.v_box.add(start_button)

        settings_button = arcade.gui.widgets.buttons.UIFlatButton(
            text="Settings", width=200
        )
        self.v_box.add(settings_button)

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
        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")

        self.ui.add(ui_anchor_layout)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_click_start(self, event):
        print("Start:", event)

    def on_draw(self):
        self.clear()
        self.ui.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.close()


if __name__ == '__main__':
    window = arcade.Window(1280, 720, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
