"""
Interactive Sprite Widget

Demonstrates UIInteractiveSpriteWidget — making sprites clickable
inside the Arcade UI system with hover and press feedback.

Click a gem to score a point. Gems light up on hover and
shrink when pressed.

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.interactive_sprite_widget
"""

import arcade
from arcade.color import TRANSPARENT_BLACK
from arcade.gui import UIManager, UIInteractiveSpriteWidget
from arcade.gui.property import bind
from arcade.gui.surface import Surface
from arcade.gui.widgets.layout import UIBoxLayout, UIAnchorLayout

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Interactive Sprite Widget Example"

GEM_IMAGES = [
    ":resources:images/items/gemBlue.png",
    ":resources:images/items/gemGreen.png",
    ":resources:images/items/gemRed.png",
    ":resources:images/items/gemYellow.png",
]
GEM_SCALE = 0.75
PRESS_SHRINK = 0.85


class PressableGemWidget(UIInteractiveSpriteWidget):
    """A gem that visually shrinks when pressed, without affecting layout."""

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(color=TRANSPARENT_BLACK)
        if self._sprite is not None:
            if self.pressed:
                draw_width = self.width * PRESS_SHRINK
                draw_height = self.height * PRESS_SHRINK
                offset_x = (self.width - draw_width) / 2
                offset_y = (self.height - draw_height) / 2
                surface.draw_sprite(offset_x, offset_y, draw_width, draw_height, self._sprite)
            else:
                surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.score = 0
        self.score_display = None
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def setup(self):
        self.score = 0
        self.score_display = arcade.Text(
            "Score: 0", 10, WINDOW_HEIGHT - 30,
            arcade.color.WHITE, font_size=18,
        )

        gem_row = UIBoxLayout(vertical=False, space_between=30)

        for image_path in GEM_IMAGES:
            sprite = arcade.Sprite(image_path, scale=GEM_SCALE)
            widget = PressableGemWidget(sprite=sprite)

            def make_hover_callback(wgt, spr):
                def on_hover_change(instance):
                    if wgt.hovered:
                        spr.color = (220, 220, 255)
                    else:
                        spr.color = (255, 255, 255)
                return on_hover_change
            bind(widget, "hovered", make_hover_callback(widget, sprite))

            def make_click_callback(path):
                def on_click(event):
                    self.score += 1
                    self.score_display.text = f"Score: {self.score}"
                return on_click
            widget.on_click = make_click_callback(image_path)

            gem_row.add(widget)

        anchor = UIAnchorLayout(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, size_hint=None)
        anchor.add(gem_row, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor)

    def on_show_view(self):
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()
        self.score_display.draw()


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    view = GameView()
    window.show_view(view)
    view.setup()
    arcade.run()


if __name__ == "__main__":
    main()
