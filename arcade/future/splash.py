"""
An experimental splash screen for Arcade.

This is a simple splash screen that shows the Arcade logo
for a few seconds before the actual game starts.

If Arcade is properly installed, you can run this script with:
python -m arcade.gui.experimental.splash
"""

import arcade
from arcade import Sprite, SpriteList, Text, View


class ArcadeSplash(View):
    """This view shows an Arcade splash screen before the actual game starts.

    Args:
        view: Next view to show after the splash screen.
        duration: The duration of the splash screen in seconds. (Default 3 seconds)
        dark_mode: If True, the splash screen will be shown in dark mode. (Default False)
    """

    def __init__(self, view: View, duration: float = 1.5, dark_mode: bool = False):
        super().__init__()
        self._next_view = view
        self._duration = duration
        self._time = 0.0
        self._dark_mode = dark_mode

        _text_color = (255, 255, 255, 255) if dark_mode else (0, 0, 0, 255)
        self._bg_color = (0, 0, 0, 255) if dark_mode else arcade.color.WHITE_SMOKE

        self._sprites: SpriteList[Sprite] = SpriteList()
        self._logo = Sprite(
            arcade.load_texture(":system:/logo.png"),
            center_x=self.window.center_x,
            center_y=self.window.center_y,
        )
        self._logo.size = 300, 300
        self._sprites.append(self._logo)

        self._text = Text(
            "Python Arcade",
            anchor_x="center",
            x=self.window.center_x,
            y=self._logo.bottom - 20,
            color=_text_color,
            font_size=40,
            bold=True,
        )

    def on_show_view(self):
        """Set background color and reset time."""
        arcade.set_background_color(self._bg_color)
        self._time = 0.0
        self._logo.alpha = 0

    def on_update(self, delta_time: float):
        """Update the time and switch to the next view after the duration."""
        self._time += delta_time
        if self._time >= self._duration:
            self.window.show_view(self._next_view)

        # fade in Arcade logo
        self._logo.alpha = min(255, int(255 * self._time / self._duration))

    def on_draw(self):
        """Draw the sprites and text."""
        self.clear()
        self._sprites.draw()
        self._text.draw()


if __name__ == "__main__":
    window = arcade.Window()
    window.show_view(ArcadeSplash(ArcadeSplash(dark_mode=True, view=arcade.View())))
    arcade.run()
