import arcade
from arcade.experimental.gui_v2 import UIManager
from arcade.experimental.gui_v2.widgets import Dummy, AnchorWidget


class UIMockup(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.RED),
            anchor_x="center_x",
            anchor_y="top",
        ))

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.BLUE),
            anchor_x="right",
            anchor_y="center_y",
        ))

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.GREEN),
            anchor_x="center_x",
            anchor_y="center_y",
        ))

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.YELLOW),
            anchor_x="left",
            anchor_y="bottom",
        ))

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.ORANGE),
            anchor_x="left",
            align_x=20,
            anchor_y="center_y",
        ))

        self.manager.add(AnchorWidget(
            child=Dummy(color=arcade.color.ORANGE),
            anchor_x="right",
            align_x=-40,
            anchor_y="bottom",
            align_y=40,
        ))

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()

    def on_update(self, time_delta):
        self.manager.on_update(time_delta)

    # TODO These can be registered by UIManager
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.manager.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_resize(self, width: float, height: float):
        # TODO: Tell Widgets they need to re-draw because surface was cleared
        super().on_resize(width, height)
        self.manager.resize(width, height)


window = UIMockup()
arcade.run()
