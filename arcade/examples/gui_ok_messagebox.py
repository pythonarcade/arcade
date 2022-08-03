"""
Example code showing how to use the OKMessageBox

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_ok_messagebox
"""
import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
from arcade.gui import UIOnClickEvent
from arcade.gui.events import UIOnActionEvent


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "OKMessageBox Example", resizable=True)
        arcade.set_background_color(arcade.color.COOL_GREY)

        # Create and enable the UIManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a box group to align the 'open' button in the center
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout()

        # Create a button. We'll click on this to open our window.
        # Add it v_box for positioning.
        open_message_box_button = arcade.gui.widgets.buttons.UIFlatButton(
            text="Open", width=200
        )
        self.v_box.add(open_message_box_button)

        # Add a hook to run when we click on the button.
        open_message_box_button.on_click = self.on_click_open
        self.open_message_box_button = open_message_box_button
        # Create a widget to hold the v_box widget, that will center the buttons

        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ui_anchor_layout)

    def on_click_open(self, _: UIOnClickEvent):
        # The code in this function is run when we click the ok button.
        # The code below opens the message box and auto-dismisses it when done.
        message_box = arcade.gui.UIMessageBox(
            width=300,
            height=200,
            message_text=(
                "You should have a look on the new GUI features "
                "coming up with arcade 2.6!"
            ),
            buttons=["Ok", "Cancel"],
        )

        @message_box.event("on_action")
        def on_message_box_close(e: UIOnActionEvent):
            print(f"User pressed {e.action}.")

            # show open button and allow interaction again
            self.open_message_box_button.visible = True

        # hide open button and prevent interaction
        self.open_message_box_button.visible = False

        self.manager.add(message_box)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_key_release(self, symbol: int, modifiers: int):
        print(self.open_message_box_button.rect)


if __name__ == '__main__':
    MyWindow().run()
