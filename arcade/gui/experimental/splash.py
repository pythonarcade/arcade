"""
An experimental splash screen for arcade.

This is a simple splash screen that shows the arcade logo
for a few seconds before the actual game starts.

If arcade is properly installed, you can run this script with:
python -m arcade.gui.experimental.splash
"""

import arcade
from arcade import View
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIImage, UILabel, UIView


class ArcadeSplash(UIView):
    """This view shows an arcade splash screen before the actual game starts.

    Args:
        view: Next view to show after the splash screen.
        duration: The duration of the splash screen in seconds. (Default 3 seconds)
    """

    def __init__(self, view: View, duration: int = 3):
        super().__init__()
        self.view = view
        self.duration = duration
        self._time = 0.0

        anchor = self.ui.add(UIAnchorLayout())
        box = anchor.add(UIBoxLayout(space_between=20))
        self._logo = box.add(
            UIImage(texture=arcade.load_texture(":system:/logo.png"), width=400, height=400)
        )
        self._logo.alpha = 0
        box.add(UILabel("Python Arcade", text_color=(0, 0, 0, 255), font_size=40, bold=True))

    def on_show_view(self):
        """Set background color and reset time."""
        super().on_show_view()
        arcade.set_background_color(arcade.color.WHITE_SMOKE)
        self._time = 0.0

    def on_update(self, delta_time: float):
        """Update the time and switch to the next view after the duration."""
        self._time += delta_time
        if self._time >= self.duration:
            self.window.show_view(self.view)

        # fade in arcade logo
        self._logo.alpha = min(255, int(255 * self._time / self.duration))


if __name__ == "__main__":
    window = arcade.Window()
    window.show_view(ArcadeSplash(View()))
    arcade.run()
