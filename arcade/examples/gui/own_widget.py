"""Example of creating a custom progress bar.

This example shows how to create a custom progress bar.

A progress bar consists of a black background box and a color bar that fills the box
from left to right. Unfilled space is gray.
A value between 0 and 1 determines the fill level of the bar.

The first progress bar is created using a `UIWidget` and the second progress bar is
created using a `UIAnchorLayout`.

For the first approach, you only need to know about the general GUI concepts, specifically
how widgets are rendered.

For the second approach, you need to know how to use layouts and size_hints to arrange widgets.

Both approaches use a Property to trigger a render when the value changes.
Properties are a way to bind a value to a widget and trigger a function when the value changes.
Read more about properties in the `arcade.gui` documentation.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.own_widgets
"""

import arcade
from arcade.gui import Property, UIAnchorLayout, UIBoxLayout, UISpace, UIView, UIWidget, bind
from arcade.types import Color


class ProgressBar1(UIWidget):
    """A custom progress bar widget.

    A UIWidget is a basic building block for GUI elements. It is a rectangle with a
    background color and can have children.

    To create a custom progress bar, we create a UIWidget with a black background,
    set a border and add a `do_render` method to draw the actual progress bar.

    """

    value = Property(0.0)
    """The fill level of the progress bar. A value between 0 and 1."""

    def __init__(
        self,
        *,
        value: float = 1.0,
        width=100,
        height=20,
        color: Color = arcade.color.GREEN,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            size_hint=None,  # disable size hint, so it just uses the size given
        )
        self.with_background(color=arcade.uicolor.GRAY_CONCRETE)
        self.with_border(color=arcade.uicolor.BLACK)

        self.value = value
        self.color = color

        # trigger a render when the value changes
        bind(self, "value", self.trigger_render)

    def do_render(self, surface: arcade.gui.Surface) -> None:
        """Draw the actual progress bar."""
        # this will set the viewport to the size of the widget
        # so that 0,0 is the bottom left corner of the widget content
        self.prepare_render(surface)

        # Draw the actual bar
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.content_width * self.value,
            self.content_height,
            self.color,
        )


class Progressbar2(UIAnchorLayout):
    """A custom progress bar widget.

    A UIAnchorLayout is a layout that arranges its children in a specific way.
    The actual bar is a UISpace that fills the parent widget from left to right.
    """

    value = Property(0.0)

    def __init__(
        self,
        value: float = 1.0,
        width=100,
        height=20,
        color: Color = arcade.color.GREEN,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            size_hint=None,  # disable size hint, so it just uses the size given
        )
        self.with_background(color=arcade.uicolor.GRAY_CONCRETE)
        self.with_border(color=arcade.uicolor.BLACK)

        self._bar = UISpace(
            color=color,
            size_hint=(value, 1),
        )
        self.add(
            self._bar,
            anchor_x="left",
            anchor_y="top",
        )
        self.value = value

        # update the bar when the value changes
        bind(self, "value", self._update_bar)

    def _update_bar(self):
        self._bar.size_hint = (self.value, 1)
        self._bar.visible = self.value > 0


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.ui.add(UIAnchorLayout())
        bars = root.add(UIBoxLayout(space_between=10))

        # UIWidget based progress bar
        self.progressbar1 = ProgressBar1(
            value=0.8,
            color=arcade.color.RED,
        )
        bars.add(self.progressbar1)

        # UIAnchorLayout based progress bar
        self.progressbar2 = Progressbar2(
            value=0.8,
            color=arcade.color.BLUE,
        )
        bars.add(self.progressbar2)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.NUM_ADD:
            self.progressbar1.value = (self.progressbar1.value + 0.1) % 1
            self.progressbar2.value = (self.progressbar2.value + 0.1) % 1
        elif symbol == arcade.key.NUM_SUBTRACT:
            self.progressbar1.value = (self.progressbar1.value - 0.1) % 1
            self.progressbar2.value = (self.progressbar2.value - 0.1) % 1

        return None


def main():
    window = arcade.Window(title="GUI Example: Progressbar")
    window.show_view(MyView())
    arcade.run()


if __name__ == "__main__":
    main()
