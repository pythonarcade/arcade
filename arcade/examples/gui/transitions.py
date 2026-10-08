"""
Example showing how to animate a widget with UIAnimatedGroup.animate().

A click sends the wrapped button on a round trip: right, up, and back to
where it started, while it is disabled. The group's ``offset_x``/``offset_y``
translate the cached subtree visually, without affecting layouting. Each
``then()`` step runs after the previous one finished; ``rel()`` marks targets
relative to the current value.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.transitions
"""

import arcade
from arcade.anim import Easing
from arcade.gui import UIManager
from arcade.gui.experimental import UIAnimatedGroup, rel
from arcade.gui.widgets.buttons import UIFlatButton


class AutoSizeButton(UIFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_label.fit_content()

    def prepare_layout(self):
        # update size hint min to fit children
        min_w = max(map(lambda c: c.width, self.children))
        min_h = max(map(lambda c: c.height, self.children))
        self.size_hint_min = (min_w, min_h)


class DemoWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Init UIManager
        self.manager = UIManager()
        self.manager.enable()

        button = AutoSizeButton(text="Click me I can move!")
        group = self.manager.add(UIAnimatedGroup(child=button))
        group.center_on_screen()

        @button.event
        def on_click(event):
            if button.disabled:
                return
            button.disabled = True

            def enable():
                button.disabled = False

            (
                group.animate(offset_x=rel(100), duration=1)
                .then(offset_y=rel(100), duration=1)
                .then(offset_x=0, duration=1, ease=Easing.SINE)
                .then(offset_y=0, duration=1, ease=Easing.SINE)
                .on_finish(enable)
            )

    def on_draw(self):
        self.clear()
        self.manager.draw()


if __name__ == "__main__":
    arcade.resources.load_kenney_fonts()
    DemoWindow().run()
