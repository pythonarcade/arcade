"""
GUI Slider Example

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.view_screens_minimal

This example demonstrates how to create a GUI slider and react to
changes in its value.

There are two other ways of handling update events. For more
information on this subject, see the gui_flat_button example.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_slider
"""
import arcade
from arcade.gui import UIManager, UILabel
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.widgets.slider import UISlider


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        # Required, create a UI manager to handle all UI widgets
        self.ui = UIManager()

        # Create our pair of widgets
        ui_slider = UISlider(value=50, width=600, height=50)
        label = UILabel(text=f"{ui_slider.value:02.0f}", font_size=20)

        # Change the label's text whenever the slider is dragged
        # See the gui_flat_button example for more information.
        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label.text = f"{ui_slider.value:02.0f}"
            label.fit_content()

        # Create a layout to hold the label and the slider
        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(
            child=ui_slider,
            anchor_x="center_x",
            anchor_y="center_y"
        )
        ui_anchor_layout.add(child=label, align_y=50)

        self.ui.add(ui_anchor_layout)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == '__main__':
    window = arcade.Window(1280, 720, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
