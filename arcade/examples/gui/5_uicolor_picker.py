"""Show all arcade.uicolors in a grid.

Click on a color to select
it and copy the Arcade reference to the clipboard.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.5_uicolor_picker

"""

from dataclasses import dataclass

import arcade
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIEvent,
    UIGridLayout,
    UIInteractiveWidget,
    UILabel,
    UITextWidget,
    UIView,
)


@dataclass
class ChooseColorEvent(UIEvent):
    """Custom event, which is dispatched when a color button is clicked."""

    color_name: str
    color: arcade.color.Color


class Toast(UILabel):
    """Label which disappears after a certain time."""

    def __init__(self, text: str, duration: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.duration = duration
        self.time = 0

    def on_update(self, dt):
        self.time += dt

        if self.time > self.duration:
            self.parent.remove(self)


class ColorButton(UITextWidget, UIInteractiveWidget):
    """Button which shows a color and color name and
    emits a ChooseColorEvent event when clicked."""

    def __init__(
        self,
        color_name: str,
        color: arcade.color.Color,
        **kwargs,
    ):
        super().__init__(text=color_name, **kwargs)
        # set color and place text on the bottom
        self.with_background(color=color)
        self.place_text(anchor_y="bottom")

        # set font color based on background color
        f = 2 if color_name.startswith("DARK") else 0.5
        self.ui_label.update_font(
            font_color=arcade.color.Color(int(color[0] * f), int(color[1] * f), int(color[2] * f))
        )

        # store color name and color for later reference
        self._color_name = color_name
        self._color = color

        # register custom event
        self.register_event_type("on_choose_color")

    def on_update(self, dt):
        """Update the button state.

        UIInteractiveWidget provides properties like hovered and pressed,
        which can be used to highlight the button."""
        if self.pressed:
            self.with_border(color=arcade.uicolor.WHITE_CLOUDS, width=3)
        elif self.hovered:
            self.with_border(color=arcade.uicolor.WHITE_CLOUDS, width=2)
        else:
            self.with_border(color=arcade.color.BLACK, width=1)

    def on_click(self, event) -> bool:
        """Emit a ChooseColorEvent event when clicked."""
        self.dispatch_event(
            "on_choose_color", ChooseColorEvent(self, self._color_name, self._color)
        )
        return True

    def on_choose_color(self, event: ChooseColorEvent):
        """ChooseColorEvent event handler, which can be overridden."""
        pass


class ColorView(UIView):
    """Uses the arcade.gui.UIView which takes care about the UIManager setup."""

    def __init__(self):
        super().__init__()
        # Create an anchor layout, which can be used to position widgets on screen
        self.root = self.add_widget(UIAnchorLayout())

        # Define colors in grid order
        self.colors = {
            # row 0
            "GREEN_TURQUOISE": arcade.uicolor.GREEN_TURQUOISE,
            "GREEN_EMERALD": arcade.uicolor.GREEN_EMERALD,
            "BLUE_PETER_RIVER": arcade.uicolor.BLUE_PETER_RIVER,
            "PURPLE_AMETHYST": arcade.uicolor.PURPLE_AMETHYST,
            "DARK_BLUE_WET_ASPHALT": arcade.uicolor.DARK_BLUE_WET_ASPHALT,
            # row 1
            "GREEN_GREEN_SEA": arcade.uicolor.GREEN_GREEN_SEA,
            "GREEN_NEPHRITIS": arcade.uicolor.GREEN_NEPHRITIS,
            "BLUE_BELIZE_HOLE": arcade.uicolor.BLUE_BELIZE_HOLE,
            "PURPLE_WISTERIA": arcade.uicolor.PURPLE_WISTERIA,
            "DARK_BLUE_MIDNIGHT_BLUE": arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            # row 2
            "YELLOW_SUN_FLOWER": arcade.uicolor.YELLOW_SUN_FLOWER,
            "ORANGE_CARROT": arcade.uicolor.ORANGE_CARROT,
            "RED_ALIZARIN": arcade.uicolor.RED_ALIZARIN,
            "WHITE_CLOUDS": arcade.uicolor.WHITE_CLOUDS,
            "GRAY_CONCRETE": arcade.uicolor.GRAY_CONCRETE,
            # row 3
            "YELLOW_ORANGE": arcade.uicolor.YELLOW_ORANGE,
            "ORANGE_PUMPKIN": arcade.uicolor.ORANGE_PUMPKIN,
            "RED_POMEGRANATE": arcade.uicolor.RED_POMEGRANATE,
            "WHITE_SILVER": arcade.uicolor.WHITE_SILVER,
            "GRAY_ASBESTOS": arcade.uicolor.GRAY_ASBESTOS,
        }

        # setup grid with colors
        self.grid = self.root.add(
            UIGridLayout(
                column_count=5,
                row_count=4,
                size_hint=(1, 1),
            )
        )
        for i, (name, color) in enumerate(self.colors.items()):
            button = ColorButton(
                color_name=name,
                color=color,
                size_hint=(1, 1),
            )
            self.grid.add(button, row=i // 5, column=i % 5)

            # connect event handler
            button.on_choose_color = self.on_color_button_choose_color

        # setup toasts (temporary messages)
        self.toasts = self.root.add(UIBoxLayout(space_between=2), anchor_x="right", anchor_y="top")
        self.toasts.with_padding(all=10)

    def on_color_button_choose_color(self, event: ChooseColorEvent) -> bool:
        """Color button click event handler, which copies the color name to the clipboard.

        And shows a temporary message."""
        self.window.set_clipboard_text(f"arcade.uicolor.{event.color_name}")

        # prepare and show toast
        toast = Toast(f"Copied {event.color_name}", width=250, size_hint=(None, 0))
        toast.update_font(
            font_color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            font_size=9,
            bold=True,
        )
        toast.with_background(color=arcade.uicolor.GREEN_EMERALD)
        toast.with_padding(all=10)

        self.toasts.add(toast)

        return True

    def on_draw_before_ui(self):
        # Add draw commands that should be below the UI
        pass

    def on_draw_after_ui(self):
        # Add draw commands that should be on top of the UI (uncommon)
        pass


def main():
    window = arcade.Window(title="GUI Example: Color Picker")
    window.show_view(ColorView())
    window.run()


if __name__ == "__main__":
    main()
