"""Example of creating a custom progress bar.

This example shows how to create a custom layout.

The layout will place the widgets in a rotating circle around the center of the screen.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.own_layout
"""

from math import cos, sin
from typing import TypeVar

import arcade
from arcade.gui import UIAnchorLayout, UIFlatButton, UILayout, UIView, UIWidget

W = TypeVar("W", bound="UIWidget")


class CircleLayout(UILayout):
    """A custom progress bar widget.

    A UIAnchorLayout is a layout that arranges its children in a specific way.
    The actual bar is a UISpace that fills the parent widget from left to right.
    """

    def __init__(self, size_hint=(1, 1), **kwargs):
        super().__init__(size_hint=size_hint, **kwargs)
        self._time = 0  # used for rotation

    def add(self, child: W, **kwargs) -> W:
        """Add a widget to the layout.

        The widget is placed in a circle around the center of the screen.
        """
        return super().add(child, **kwargs)

    def do_layout(self):
        """Layout the children in a circle around the center of the screen."""
        if not self._children:
            return

        # handle the size hints of the children
        for child in self.children:
            self._resize_child(child)

        # calculate the radius, so that the children are placed inside the parent widget
        max_child_width = max(child.content_width for child in self.children)
        max_child_height = max(child.content_height for child in self.children)
        radius = (
            min(self.content_width - max_child_width, self.content_height - max_child_height) / 2
        )

        for i, child in enumerate(self.children):
            angle = i / len(self.children) * 2 * 3.1415
            # add rotation based on time
            angle += self._time * 0.08
            center_x = self.center_x + radius * cos(angle)
            center_y = self.center_y + radius * sin(angle)

            new_rect = child.rect.align_center((center_x, center_y))
            child.rect = new_rect

    def _resize_child(self, child: UIWidget):
        """Resizes the child based on the size_hint, size_hint_min, and size_hint_max."""
        new_child_rect = child.rect

        sh_w, sh_h = child.size_hint or (None, None)
        shmn_w, shmn_h = child.size_hint_min or (None, None)
        shmx_w, shmx_h = child.size_hint_max or (None, None)

        if sh_w is not None:
            new_child_rect = new_child_rect.resize(width=self.content_width * sh_w)

            if shmn_w:
                new_child_rect = new_child_rect.min_size(width=shmn_w)
            if shmx_w:
                new_child_rect = new_child_rect.max_size(width=shmx_w)

        if sh_h is not None:
            new_child_rect = new_child_rect.resize(height=self.content_height * sh_h)

            if shmn_h:
                new_child_rect = new_child_rect.min_size(height=shmn_h)
            if shmx_h:
                new_child_rect = new_child_rect.max_size(height=shmx_h)

        child.rect = new_child_rect

    def on_update(self, dt):
        self._time += dt


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.ui.add(UIAnchorLayout())

        # Create a custom layout
        self.circle_layout = root.add(CircleLayout(size_hint=(0.8, 0.8)))

        # Add buttons to the layout
        for i in range(8):
            self.circle_layout.add(
                UIFlatButton(
                    text=f"Button {i}",
                    size_hint=(0.1, 0.1),
                )
            )


def main():
    window = arcade.Window(title="GUI Example: CircleLayout")
    window.show_view(MyView())
    arcade.run()


if __name__ == "__main__":
    main()
