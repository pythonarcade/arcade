import arcade
from arcade.experimental.gui_v2 import UIManager
from arcade.experimental.gui_v2.widgets import Button, PlacedWidget


class UIMockup(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.RED),
            x_anchor="center_x",
            y_anchor="top",
        ))

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.BLUE),
            x_anchor="right",
            y_anchor="center_y",
        ))

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.GREEN),
            x_anchor="center_x",
            y_anchor="center_y",
        ))

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.YELLOW),
            x_anchor="left",
            y_anchor="bottom",
        ))

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.ORANGE),
            x_anchor="left",
            x_align=20,
            y_anchor="center_y",
        ))

        self.manager.add(PlacedWidget(
            Button(color=arcade.color.ORANGE),
            x_anchor="right",
            x_align=-40,
            y_anchor="bottom",
            y_align=40,
        ))

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()

    def on_update(self, time_delta):
        self.manager.on_update(time_delta)
        self.manager.render()

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
