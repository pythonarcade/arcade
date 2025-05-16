"""An overview of all included widgets.

See the other GUI examples for more indepth information about specific widgets.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.2_widgets
"""

import textwrap
from copy import deepcopy

import arcade
from arcade.gui import (
    NinePatchTexture,
    UIAnchorLayout,
    UIBoxLayout,
    UIButtonRow,
    UIDropdown,
    UIDummy,
    UIFlatButton,
    UIImage,
    UIInputText,
    UILabel,
    UIManager,
    UIMessageBox,
    UIOnActionEvent,
    UIOnChangeEvent,
    UISlider,
    UISpace,
    UISpriteWidget,
    UITextArea,
    UITextureButton,
    UITextureSlider,
    UITextureToggle,
    UIView,
)
from arcade.gui.experimental import UIPasswordInput

# Load system fonts
arcade.resources.load_kenney_fonts()

DEFAULT_FONT = ("Kenney Future", "arial")
DETAILS_FONT = ("arial", "Kenney Future Narrow")

# Preload textures, because they are mostly used multiple times, so they are not
# loaded multiple times
TEX_SCROLL_DOWN = arcade.load_texture(":resources:gui_basic_assets/scroll/indicator_down.png")
TEX_SCROLL_UP = arcade.load_texture(":resources:gui_basic_assets/scroll/indicator_up.png")

TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")
TEX_RED_BUTTON_DISABLE = arcade.load_texture(":resources:gui_basic_assets/button/red_disabled.png")

TEX_TOGGLE_RED = arcade.load_texture(":resources:gui_basic_assets/toggle/red.png")
TEX_TOGGLE_GREEN = arcade.load_texture(":resources:gui_basic_assets/toggle/green.png")

TEX_CHECKBOX_CHECKED = arcade.load_texture(":resources:gui_basic_assets/checkbox/blue_check.png")
TEX_CHECKBOX_UNCHECKED = arcade.load_texture(":resources:gui_basic_assets/checkbox/empty.png")

TEX_SLIDER_THUMB_BLUE = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_blue.png")
TEX_SLIDER_TRACK_BLUE = arcade.load_texture(":resources:gui_basic_assets/slider/track_blue.png")
TEX_SLIDER_THUMB_RED = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_red.png")
TEX_SLIDER_TRACK_RED = arcade.load_texture(":resources:gui_basic_assets/slider/track_red.png")
TEX_SLIDER_THUMB_GREEN = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_green.png")
TEX_SLIDER_TRACK_GREEN = arcade.load_texture(":resources:gui_basic_assets/slider/track_green.png")

TEX_NINEPATCH_BASE = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")

TEX_ARCADE_LOGO = arcade.load_texture(":resources:/logo.png")

# Load animation for the sprite widget
frame_textures = []
for i in range(8):
    tex = arcade.load_texture(
        f":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk{i}.png"
    )
    frame_textures.append(tex)

TEX_ANIMATED_CHARACTER = arcade.TextureAnimation(
    [arcade.TextureKeyframe(frame) for frame in frame_textures]
)

TEXT_WIDGET_EXPLANATION = textwrap.dedent("""
Arcade GUI provides three types of text widgets:


- {bold True}UILabel{bold False}:
A simple text widget that can be used to display text.

- {bold True}UIInputText{bold False}:
A text widget that can be used to get text input from the user.

- {bold True}UITextArea{bold False}:
A text widget that can be used to display text that is too long for a label.


This example shows how to use all three types of text widgets.


A few hints regarding the usage of the text widgets:


{bold True}UILabel{bold False}:

If you want to display frequently changing text,
setting a background color will improve performance.


{bold True}UIInputText{bold False}:

UIInputText dispatches an event on_change, when the text changes.


{bold True}UITextArea{bold False}:

While the widget supports scrolling, there is no scrollbar provided yet.
Users might oversee content.

In addition UITextArea supports different text styles,
which relate to Pyglet FormattedDocument.

"PLAIN" - Plain text.

"ATTRIBUTED" - Attributed text following the Pyglet attributed text style.

"HTML" - Allows to use HTML tags for formatting.

""").strip()


class ScrollableTextArea(UITextArea, UIAnchorLayout):
    """This widget is a text area that can be scrolled, like a UITextLayout, but shows indicator,
    that the text can be scrolled."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        indicator_size = 22
        self._down_indicator = UIImage(
            texture=TEX_SCROLL_DOWN, size_hint=None, width=indicator_size, height=indicator_size
        )
        self._down_indicator.visible = False
        self.add(self._down_indicator, anchor_x="right", anchor_y="bottom", align_x=3)

        self._up_indicator = UIImage(
            texture=TEX_SCROLL_UP, size_hint=None, width=indicator_size, height=indicator_size
        )
        self._up_indicator.visible = False
        self.add(self._up_indicator, anchor_x="right", anchor_y="top", align_x=3)

    def on_update(self, dt):
        self._up_indicator.visible = self.layout.view_y < 0
        self._down_indicator.visible = (
            abs(self.layout.view_y) < self.layout.content_height - self.layout.height
        )


class GalleryView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.add_widget(UIAnchorLayout())

        # Setup side navigation
        nav_side = UIButtonRow(vertical=True, size_hint=(0.3, 1))
        nav_side.add(
            UILabel(
                "Categories",
                font_name=DEFAULT_FONT,
                font_size=32,
                text_color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE,
                size_hint=(1, 0.1),
                align="center",
            )
        )
        nav_side.add(UISpace(size_hint=(1, 0.01), color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE))

        nav_side.with_padding(all=10)
        nav_side.with_background(color=arcade.uicolor.WHITE_CLOUDS)
        nav_side.add_button("Start", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        nav_side.add_button("Text", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        nav_side.add_button("Interactive", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        nav_side.add_button("Constructs", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        nav_side.add_button("Other", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        root.add(nav_side, anchor_x="left", anchor_y="top")

        @nav_side.event("on_action")
        def on_action(event: UIOnActionEvent):
            if event.action == "Start":
                self._show_start_widgets()
            elif event.action == "Text":
                self._show_text_widgets()
            elif event.action == "Interactive":
                self._show_interactive_widgets()
            elif event.action == "Constructs":
                self._show_construct_widgets()
            elif event.action == "Other":
                self._show_other_widgets()

        # Setup content to show widgets in

        self._body = UIAnchorLayout(size_hint=(0.7, 1))
        self._body.with_padding(all=20)
        root.add(self._body, anchor_x="right", anchor_y="top")

        # init start widgets
        self._show_start_widgets()

    def _show_start_widgets(self):
        """Show a short introduction message."""
        self._body.clear()
        self._body.add(
            UITextArea(
                text=textwrap.dedent("""
                Welcome to the Widget Gallery

                Choose a category on the left to see the widgets.
                You can checkout the source code in the examples/gui folder
                to see how this gallery is built.
                """).strip(),
                font_name=DETAILS_FONT,
                font_size=32,
                text_color=arcade.uicolor.WHITE,
                size_hint=(0.8, 0.8),
            ),
            anchor_y="top",
        )
        open_sourcecode = self._body.add(
            UIFlatButton(
                text="Open Source Code", style=UIFlatButton.STYLE_RED, size_hint=(0.3, 0.1)
            ),
            anchor_y="bottom",
            align_y=20,
        )

        @open_sourcecode.event("on_click")
        def on_click(_):
            """This will open the source code of this example on GitHub."""
            import webbrowser

            webbrowser.open(
                "https://github.com/pythonarcade/arcade/tree/development/arcade/examples/gui"
            )

    def _show_text_widgets(self):
        """Show the text widgets.

        For this we clear the body and add the text widgets.

        Featuring:
        - UILabel
        - UIInputText
        - UITextArea
        """

        self._body.clear()

        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left", space_between=10)
        self._body.add(box)
        box.add(UILabel("Text Widgets", font_name=DEFAULT_FONT, font_size=32))
        box.add(UISpace(size_hint=(1, 0.1)))

        row_1 = UIBoxLayout(vertical=False, size_hint=(1, 0.1))
        box.add(row_1)
        row_1.add(UILabel("Username: ", font_name=DEFAULT_FONT, font_size=24))
        name_input = row_1.add(
            UIInputText(
                width=400,
                height=40,
                font_name=DEFAULT_FONT,
                font_size=24,
                border_color=arcade.uicolor.GRAY_CONCRETE,
                border_width=2,
            )
        )

        row_2 = UIBoxLayout(vertical=False, size_hint=(1, 0.1))
        box.add(row_2)
        row_2.add(UILabel("Password: ", font_name=DEFAULT_FONT, font_size=24))
        pw_input = row_2.add(
            UIPasswordInput(
                width=400,
                height=40,
                font_name=DEFAULT_FONT,
                font_size=24,
                border_color=arcade.uicolor.GRAY_CONCRETE,
                border_width=2,
            )
        )

        @pw_input.event("on_change")
        def _(event: UIOnChangeEvent):
            event.source.invalid = event.new_value != "arcade"

        welcome_label = box.add(
            UILabel("Nice to meet you ''", font_name=DEFAULT_FONT, font_size=24)
        )

        @name_input.event("on_change")
        def _(event: UIOnChangeEvent):
            welcome_label.text = f"Nice to meet you `{event.new_value}`"

        box.add(UISpace(size_hint=(1, 0.3)))  # Fill some of the left space

        text_area = box.add(
            ScrollableTextArea(
                text=TEXT_WIDGET_EXPLANATION,
                size_hint=(1, 0.9),
                font_name=DETAILS_FONT,
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                document_mode="ATTRIBUTED",
            )
        )
        text_area.with_padding(left=10, right=10)
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)

    def _show_interactive_widgets(self):
        self._body.clear()
        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left", space_between=10)
        self._body.add(box)
        box.add(UILabel("Interactive Widgets", font_name=DEFAULT_FONT, font_size=32))
        box.add(UISpace(size_hint=(1, 0.1)))

        flat_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(flat_row)

        flat_row.add(
            UIFlatButton(
                text="UIFlatButton blue", style=UIFlatButton.STYLE_BLUE, size_hint=(0.3, 1)
            )
        )
        flat_row.add(
            UIFlatButton(text="UIFlatButton red", style=UIFlatButton.STYLE_RED, size_hint=(0.3, 1))
        )
        flat_row.add(
            UIFlatButton(text="disabled", style=UIFlatButton.STYLE_BLUE, size_hint=(0.3, 1))
        ).disabled = True

        tex_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(tex_row)
        tex_row.add(
            UITextureButton(
                text="UITextureButton",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
                texture_disabled=TEX_RED_BUTTON_DISABLE,
                size_hint=(0.3, 1),
            )
        )

        tex_row.add(UISpace(size_hint=(0.3, 1)))

        tex_row.add(
            UITextureButton(
                text="disabled",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
                texture_disabled=TEX_RED_BUTTON_DISABLE,
                size_hint=(0.3, 1),
            )
        ).disabled = True

        toggle_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(toggle_row)
        toggle_row.add(
            UILabel("UITextureToggle", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0))
        )
        toggle_row.add(
            UITextureToggle(
                on_texture=TEX_TOGGLE_RED,
                off_texture=TEX_TOGGLE_GREEN,
                width=64,
                height=32,
            )
        )
        toggle_row.add(
            UITextureToggle(
                on_texture=TEX_CHECKBOX_CHECKED,
                off_texture=TEX_CHECKBOX_UNCHECKED,
                width=32,
                height=32,
            )
        )

        dropdown_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(dropdown_row)
        dropdown_row.add(
            UILabel("UIDropdown", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0))
        )
        dropdown_row.add(
            UIDropdown(
                default="Option 1",
                options=["Option 1", "Option 2", "Option 3"],
            )
        )

        slider_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(slider_row)

        slider_row.add(
            UILabel(
                "UISlider",
                font_name=DETAILS_FONT,
                font_size=16,
                size_hint=(0.3, 0),
            )
        )
        s1 = slider_row.add(UISlider(size_hint=(0.3, 1), step=1, style=UISlider.NO_STEP_STYLE))
        s2 = slider_row.add(
            UISlider(
                size_hint=(0.3, 1),
                step=5,
            )
        )
        s3 = slider_row.add(
            UISlider(
                size_hint=(0.3, 1),
                step=10,
            )
        )

        @s1.event("on_change")
        def _(event: UIOnChangeEvent):
            s2.value = event.new_value
            s3.value = event.new_value

        @s2.event("on_change")
        def _(event: UIOnChangeEvent):
            s1.value = event.new_value
            s3.value = event.new_value

        @s3.event("on_change")
        def _(event: UIOnChangeEvent):
            s1.value = event.new_value
            s2.value = event.new_value

        tex_slider_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(tex_slider_row)

        tex_slider_row.add(
            UILabel(
                "UITextureSlider",
                font_name=DETAILS_FONT,
                font_size=16,
                size_hint=(0.3, 0),
            )
        )

        ts1 = tex_slider_row.add(
            UITextureSlider(
                thumb_texture=TEX_SLIDER_THUMB_BLUE,
                track_texture=NinePatchTexture(10, 10, 10, 10, TEX_SLIDER_TRACK_BLUE),
                size_hint=(0.3, None),
            )
        )

        green_style = deepcopy(UITextureSlider.DEFAULT_STYLE)
        green_style["normal"].filled_track = arcade.uicolor.GREEN_GREEN_SEA
        green_style["hover"].filled_track = arcade.uicolor.GREEN_EMERALD
        green_style["press"].filled_track = arcade.uicolor.GREEN_GREEN_SEA
        ts2 = tex_slider_row.add(
            UITextureSlider(
                thumb_texture=TEX_SLIDER_THUMB_GREEN,
                track_texture=NinePatchTexture(10, 10, 10, 10, TEX_SLIDER_TRACK_GREEN),
                size_hint=(0.3, None),
                style=green_style,
            )
        )

        red_style = deepcopy(UITextureSlider.DEFAULT_STYLE)
        red_style["normal"].filled_track = arcade.uicolor.RED_POMEGRANATE
        red_style["hover"].filled_track = arcade.uicolor.RED_ALIZARIN
        red_style["press"].filled_track = arcade.uicolor.RED_POMEGRANATE
        ts3 = tex_slider_row.add(
            UITextureSlider(
                thumb_texture=TEX_SLIDER_THUMB_RED,
                track_texture=NinePatchTexture(10, 10, 10, 10, TEX_SLIDER_TRACK_RED),
                size_hint=(0.3, None),
                style=red_style,
            )
        )

        @ts1.event("on_change")
        def _(event: UIOnChangeEvent):
            ts2.value = event.new_value
            ts3.value = event.new_value

        @ts2.event("on_change")
        def _(event: UIOnChangeEvent):
            ts1.value = event.new_value
            ts3.value = event.new_value

        @ts3.event("on_change")
        def _(event: UIOnChangeEvent):
            ts1.value = event.new_value
            ts2.value = event.new_value

        box.add(UISpace(size_hint=(0.2, 0.1)))
        text_area = box.add(
            UITextArea(
                text=textwrap.dedent("""
                        Interactive widgets are widgets that the user can interact with.
                        This includes buttons, toggles, sliders and more.

                        By subclassing UIInteractiveWidget you
                        can create your own interactive widgets.

                        For text input have a look at the text widgets.
                    """).strip(),
                font_name=DETAILS_FONT,
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                size_hint=(1, 0.9),
            )
        )
        text_area.with_padding(left=10, right=10)
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)

    def _show_construct_widgets(self):
        self._body.clear()
        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left", space_between=10)
        self._body.add(box)
        box.add(UILabel("Constructs", font_name=DEFAULT_FONT, font_size=32))
        box.add(UISpace(size_hint=(1, 0.1)))

        message_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(message_row)
        message_row.add(
            UILabel(
                "UIMessageBox",
                font_name=DETAILS_FONT,
                font_size=16,
                size_hint=(0.3, 0),
            )
        )
        message_button = message_row.add(
            UIFlatButton(
                text="Show Message",
                style=UIFlatButton.STYLE_BLUE,
                size_hint=(0.3, 1),
            )
        )

        @message_button.event("on_click")
        def on_click(event):
            self.ui.add(
                UIMessageBox(
                    width=500,
                    height=350,
                    title="Message Box",
                    buttons=("Ok", "Cancel"),
                    message_text=textwrap.dedent("""
                    This is a message box.
                    It can be used to show messages to the user.

                    You can add buttons to it, to let the user choose an action.
                    """).strip(),
                ),
                layer=UIManager.OVERLAY_LAYER,
            )

        button_row = UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=10)
        box.add(button_row)
        button_row.add(
            UILabel(
                "UIButtonRow",
                font_name=DETAILS_FONT,
                font_size=16,
                size_hint=(0.3, 0),
            )
        )
        buttons = button_row.add(
            UIButtonRow(
                text="Show Message",
                style=UIFlatButton.STYLE_BLUE,
                size_hint=(1, 0),
            )
        )
        buttons.add_button("Default Style", size_hint=(1, None))
        buttons.add_button("Red Style", style=UIFlatButton.STYLE_RED, size_hint=(1, None))
        buttons.add_button("Blue Style", style=UIFlatButton.STYLE_BLUE, size_hint=(1, None))

        # Constructs
        # "UIButtonRow",

        box.add(UISpace(size_hint=(0.2, 0.1)))
        text_area = box.add(
            UITextArea(
                text=textwrap.dedent("""
            Constructs are widgets that combine multiple widgets, to provide common functionality
            within a simple widget.
            Examples for this are message boxes or rows of buttons.
            """).strip(),
                font_name=DETAILS_FONT,
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                size_hint=(1, 0.5),
            )
        )
        text_area.with_padding(left=10, right=10)
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)

    def _show_other_widgets(self):
        self._body.clear()
        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left", space_between=10)
        self._body.add(box)
        box.add(UILabel("Other Widgets", font_name=DEFAULT_FONT, font_size=32))
        box.add(UISpace(size_hint=(1, 0.1)))

        image_row = box.add(UIBoxLayout(vertical=False, size_hint=(1, 0.1)))
        image_row.add(UILabel("UIImage", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0)))
        image_row.add(UIImage(texture=TEX_ARCADE_LOGO, width=64, height=64))

        dummy_row = box.add(UIBoxLayout(vertical=False, size_hint=(1, 0.1)))
        dummy_row.add(UILabel("UIDummy", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0)))
        dummy_row.add(UIDummy(size_hint=(0.2, 1)))
        dummy_row.add(UIDummy(size_hint=(0.2, 1)))
        dummy_row.add(UIDummy(size_hint=(0.2, 1)))

        sprite = arcade.TextureAnimationSprite(animation=TEX_ANIMATED_CHARACTER)
        sprite.scale = 0.5
        sprite_row = box.add(UIBoxLayout(vertical=False, size_hint=(1, 0.1)))
        sprite_row.add(
            UILabel("UISpriteWidget", font_name=DETAILS_FONT, font_size=16, size_hint=(0.3, 0))
        )
        sprite_row.add(UISpriteWidget(sprite=sprite, width=sprite.width, height=sprite.height))

        box.add(UISpace(size_hint=(0.2, 0.1)))
        text_area = box.add(
            UITextArea(
                text=textwrap.dedent("""
                    Arcade GUI provides also a few more widgets for special use cases.

                    - UIImage: A widget to display an image.
                    - UIDummy: Which can be used as a placeholder.
                                It renders a random color and changes it on click.
                    - UISpace: A widget that only takes up space.
                                But can also be used to add a colored space.
                    - UISpriteWidget: A widget that can display a sprite.

                    """).strip(),
                font_name=DETAILS_FONT,
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                size_hint=(1, 0.9),
            )
        )
        text_area.with_padding(left=10, right=10)
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)


def main():
    window = arcade.Window(title="GUI Example: Widget Gallery")
    window.show_view(GalleryView())
    window.run()


if __name__ == "__main__":
    main()
