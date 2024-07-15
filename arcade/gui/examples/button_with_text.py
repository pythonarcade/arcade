"""
Customizing buttons with text & textures.

This example showcases arcade's range of different built-in button types
and how they can be used to customize a UI. A UIGridLayout is used to
arrange buttons.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.button_with_text
"""

from __future__ import annotations

import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIImage
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.widgets.buttons import UIFlatButton, UITextureButton
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout
from arcade.gui.widgets.toggle import UITextureToggle

# Preload textures, because they are mostly used multiple times, so they are not
# loaded multiple times
ICON_SMALLER = load_texture(":resources:gui_basic_assets/icons/smaller.png")
ICON_LARGER = load_texture(":resources:gui_basic_assets/icons/larger.png")

TEX_SWITCH_GREEN = load_texture(":resources:gui_basic_assets/toggle/switch_green.png")
TEX_SWITCH_RED = load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
TEX_RED_BUTTON_NORMAL = load_texture(":resources:gui_basic_assets/red_button_normal.png")
TEX_RED_BUTTON_HOVER = load_texture(":resources:gui_basic_assets/red_button_hover.png")
TEX_RED_BUTTON_PRESS = load_texture(":resources:gui_basic_assets/red_button_press.png")


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        grid = UIGridLayout(
            column_count=3,
            row_count=4,
            size_hint=(0, 0),
            vertical_spacing=10,
            horizontal_spacing=10,
        )

        self.ui.add(UIAnchorLayout(children=[grid]))

        # simple UIFlatButton with text
        grid.add(UIFlatButton(text="UIFlatButton", width=200), row_num=0, col_num=0)

        # UIFlatButton change text placement right
        flat_with_more_text = UIFlatButton(text="text placed right", width=200)
        flat_with_more_text.place_text(anchor_x="right")
        grid.add(flat_with_more_text, row_num=1, col_num=0)

        # UIFlatButton change text placement right
        flat_with_more_text = UIFlatButton(text="text placed top left", width=200)
        flat_with_more_text.place_text(anchor_x="left", anchor_y="top")
        grid.add(flat_with_more_text, row_num=2, col_num=0)

        # UIFlatButton with icon on the left
        flat_with_icon_left = UIFlatButton(text="UIFlatButton with icon", width=200)
        flat_with_icon_left.place_text(align_x=+20)
        flat_with_icon_left.add(
            child=UIImage(
                texture=ICON_LARGER,
                width=30,
                height=30,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(flat_with_icon_left, row_num=0, col_num=1)

        # UIFlatButton with icon on the right
        flat_with_icon_right = UIFlatButton(text="UIFlatButton with icon", width=200)
        flat_with_icon_right.place_text(align_x=-20)
        flat_with_icon_right.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=30,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )
        grid.add(flat_with_icon_right, row_num=1, col_num=1)

        # UIFlatButton with icon on both sides
        flat_with_icon_right = UIFlatButton(text="UIFlatButton", width=200)
        flat_with_icon_right.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=30,
                height=30,
            ),
            anchor_x="left",
            align_x=10,
        )
        flat_with_icon_right.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=30,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )
        grid.add(flat_with_icon_right, row_num=2, col_num=1)

        # UITextureButton
        texture_button = UITextureButton(
            text="UITextureButton",
            width=200,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )
        grid.add(texture_button, row_num=0, col_num=2)

        # UITextureButton with icon left
        texture_button_with_icon_left = UITextureButton(
            text="UITextureButton",
            width=200,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )
        texture_button_with_icon_left.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(texture_button_with_icon_left, row_num=1, col_num=2)

        # UITextureButton with multiline text
        texture_button_with_icon_left = UITextureButton(
            text="UITextureButton\nwith a second line",
            multiline=True,
            width=200,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )
        texture_button_with_icon_left.place_text(anchor_x="left", align_x=45)
        texture_button_with_icon_left.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        grid.add(texture_button_with_icon_left, row_num=2, col_num=2)

        # UIFlatButtons with toggle
        texture_button_with_toggle = UIFlatButton(
            text="Just get crazy now!",
            width=630,
        )
        texture_button_with_toggle.place_text(anchor_x="left", align_x=45)
        texture_button_with_toggle.add(
            child=UIImage(
                texture=ICON_SMALLER,
                width=25,
                height=25,
            ),
            anchor_x="left",
            align_x=10,
        )
        toggle = texture_button_with_toggle.add(
            child=UITextureToggle(
                on_texture=TEX_SWITCH_RED,
                off_texture=TEX_SWITCH_GREEN,
                width=60,
                height=30,
            ),
            anchor_x="right",
            align_x=-10,
        )

        @toggle.event
        def on_change(event: UIOnChangeEvent):
            texture_button_with_toggle.disabled = event.new_value

        grid.add(texture_button_with_toggle, row_num=3, col_num=0, col_span=3)

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


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
