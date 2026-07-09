"""Hoverable cards, animated with UIAnimatedGroup.animate().

This example combines two new GUI features:

- :class:`UIAnimatedGroup` renders a widget subtree into a cached surface,
  which can be drawn with rotation, scaling, fading and tinting.
  The wrapped widgets are only re-rendered when they actually change,
  animating the group itself is basically free.
- Animations (:meth:`UIAnimatedGroup.animate`) tween properties over time.
  Starting a new animation takes over its properties from running ones,
  so hover in/out just starts a new animation - no cleanup required.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_animations_2
"""

from __future__ import annotations


import arcade
from arcade import Texture, resources
from arcade.anim import Easing
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIFlatButton,
    UIImage,
    UITextArea,
    UIView,
    bind,
)
from arcade.gui.experimental import UIAnimatedGroup


class Card(UIBoxLayout):
    def __init__(self, *, title: str, texture: Texture, text: str, **kwargs):
        super().__init__(
            children=[
                UIImage(texture=texture),
                UIFlatButton(text=title, size_hint=(1, None)),
                UITextArea(text=text, width=200, height=100).with_padding(all=5),
            ],
            vertical=True,
        )

        self.with_border(color=arcade.uicolor.WHITE, width=2)
        self.with_background(color=arcade.uicolor.GRAY_ASBESTOS)


class MainMenuView(UIView):
    def __init__(self):
        super().__init__()

        root = self.add_widget(UIAnchorLayout())

        # three cards with a picture, title and text,
        # hovering a card lifts and enlarges it
        cards = root.add(
            UIBoxLayout(vertical=False, align="center", size_hint=(0.0, 0.3), space_between=50),
            anchor_y="bottom",
            align_y=-120,
        )

        for title, texture, text in [
            ("Bee", ":resources:/images/enemies/bee.png", "A fantastic bee"),
            ("Fish", ":resources:/images/enemies/fishGreen.png", "A fantastic fish"),
            ("Ladybug", ":resources:/images/enemies/ladybug.png", "A fantastic ladybug"),
        ]:
            card = Card(title=title, texture=arcade.load_texture(texture), text=text)
            self._add_hover_effect(cards.add(UIAnimatedGroup(child=card)))

    def _add_hover_effect(self, group: UIAnimatedGroup):
        """Lift and enlarge the card while it is hovered.

        Starting a new animation takes over ``scale`` and ``offset_y`` from
        the previous one, so changing direction mid-animation just works.
        """

        def on_hover_change():
            if group.hovered:
                group.animate(scale=1.25, offset_y=100, duration=0.15, ease=Easing.BACK_OUT)
            else:
                group.animate(scale=1.0, offset_y=0, duration=0.15)

        bind(group, "hovered", on_hover_change)


def main():
    window = arcade.Window(1280, 720, "GUI Example: Animated Cards", resizable=True)
    window.show_view(MainMenuView())
    arcade.run()


if __name__ == "__main__":
    import pyglet
    # pyglet.options.text_antialiasing = False
    #
    from pyglet.graphics.api.gl import GL_NEAREST
    pyglet.font.base.Font.texture_min_filter = GL_NEAREST
    pyglet.font.base.Font.texture_mag_filter = GL_NEAREST
    resources.load_kenney_fonts()

    main()
