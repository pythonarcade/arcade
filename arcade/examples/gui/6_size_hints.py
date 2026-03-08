"""Sizing widgets using size hint keyword arguments

The following keyword arguments can be used to set preferred size
information for layouts which arrange widgets

* size_hint
* size_hint_max
* size_hint_min

Please note the following:

* These do nothing outside a layout
* They are only hints, and do not guarantee that a specific size will
  be provided.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.6_size_hints
"""

import textwrap

import arcade
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UILabel,
    UIOnChangeEvent,
    UISpace,
    UITextArea,
    UIView,
)

arcade.resources.load_kenney_fonts()

SIZE_HINT_TEXT = textwrap.dedent(
    """
    UIWidgets provide three properties,
    which are used by layouts to determine the size of a widget.

These properties are:

* size_hint - percentage of the layout size
* size_hint_max - maximum size in pixels
* size_hint_min - minimum size in pixels

Theses properties can be None, or a tuple of two values. The first value is
the width, and the second value is the height.

If a value is None, the layout will use the widget's natural size for that dimension.

    """.strip()
)


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.ui.add(UIAnchorLayout())
        content = root.add(UIBoxLayout(size_hint=(1, 1)), anchor_x="left", anchor_y="top")

        # title and information
        header_box = content.add(
            UIBoxLayout(space_between=5, align="left", size_hint=(1, 0)),
        )
        header_box.with_border(color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE)
        header_box.with_padding(all=10)

        title = header_box.add(UILabel("Size Hint Example", font_size=24, bold=True))
        header_box.add(UISpace(color=arcade.uicolor.WHITE_CLOUDS, height=2, width=title.width))

        # create text area and set the minimal size to the content size
        text = header_box.add(
            UITextArea(
                text=SIZE_HINT_TEXT,
                width=800,  # give text enough space to not wrap
                font_size=14,
                size_hint=(1, 1),
                bold=True,
            )
        )
        text.with_padding(top=10)
        text.size_hint_min = (
            None,
            text.layout.content_height + 50,
        )  # set minimal height to content height + padding

        # add interactive demo
        content_anchor = content.add(UIAnchorLayout())
        content_anchor.with_border(color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE)
        content_anchor.with_padding(left=10, bottom=10)

        center_box = content_anchor.add(
            UIBoxLayout(size_hint=(0.8, 0.5), align="left", space_between=20)
        )

        width_slider_box = center_box.add(UIBoxLayout(vertical=False, size_hint=(1, 0)))
        width_slider_box.add(UILabel("Modify size_hint:", bold=True))
        width_slider = width_slider_box.add(
            arcade.gui.UISlider(
                min_value=0, max_value=1, value=0, size_hint=None, height=30, step=0.1
            )
        )
        width_value = width_slider_box.add(UILabel(bold=True))

        content_anchor.add(UISpace(height=50))

        # create a horizontal UIBoxLayout to show the effect of the sliders
        demo_box = center_box.add(UIBoxLayout(vertical=False, size_hint=(0.8, 1)))
        demo_box.with_background(color=arcade.uicolor.GRAY_ASBESTOS)

        # create a dummy widget to show the effect of the sliders
        dummy1 = demo_box.add(UILabel(bold=True))
        dummy1.with_background(color=arcade.uicolor.YELLOW_ORANGE)
        dummy2 = demo_box.add(UILabel(bold=True))
        dummy2.with_background(color=arcade.uicolor.GREEN_EMERALD)

        def update_size_hint_value(value: float):
            width_value.text = f"({value:.2f})"
            dummy1.size_hint = (value, 1)
            dummy1.text = f"size_hint = ({value:.2f}, 1)"

            dummy2.size_hint = (1 - value, 1)
            dummy2.text = f"size_hint = ({1 - value:.2f}, 1)"

        @width_slider.event("on_change")
        def on_change(event: UIOnChangeEvent):
            update_size_hint_value(event.new_value)

        initial_value = 1
        width_slider.value = initial_value
        update_size_hint_value(initial_value)

        content_anchor.add(UISpace(height=20))

        self.ui.execute_layout()


def main():
    window = arcade.Window(title="UIExample: Size Hints")
    window.show_view(MyView())
    window.run()


if __name__ == "__main__":
    main()
