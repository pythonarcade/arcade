"""
Disappearing Info Box.

An example of how to make info boxes vanish after some amount of time.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_disappearing_info_box
"""

import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout

BOX_WIDTH = 300
BOX_HEIGHT = 200

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Disappearing Info Box Example"


class MyWindow(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.COOL_GREY)

        # Create and enable the UIManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a box group to align the 'open' button in the center
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout()

        # Create a button. Then add a hook to run when we click on the button
        open_message_box_button = arcade.gui.widgets.buttons.UIFlatButton(
            text="Open", width=200
        )
        self.v_box.add(open_message_box_button)
        open_message_box_button.on_click = self.on_click_open  # type: ignore
        self.open_message_box_button = open_message_box_button

        # Create a widget to hold the v_box widget, that will center the ok button
        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ui_anchor_layout)

    def on_draw(self) -> None:
        self.clear()
        self.manager.draw()

    def on_click_open(self, event) -> None:
        # The code in this function is run when we click the ok button. This code opens
        # the info box which disappears after a certain amount of time
        info_box = arcade.gui.UIMessageBox(
            width=BOX_WIDTH,
            height=BOX_HEIGHT,
            message_text="This box will disappear in 3 seconds!",
            bg_color=arcade.color.BABY_BLUE,
            buttons=("Ok", "test",),
            disappear=True,
            disappear_time=3,
            callback=self.on_message_box_close,
        )

        # Hide the open button and add the info box to the UIManager
        self.open_message_box_button.visible = False
        self.manager.add(info_box)

    def on_message_box_close(self, button_text: str) -> None:
        if not button_text:
            print("No buttons were pressed")
        else:
            print(f"User pressed {button_text}")

        # Show the open button and allow interaction again
        self.open_message_box_button.visible = True


window = MyWindow()
window.run()
