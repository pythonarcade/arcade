import arcade
from arcade import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT
from arcade.experimental.gui_v2 import UIManager
from arcade.experimental.gui_v2.widgets import Dummy, AnchorWidget, ListGroup, Space, Border, Padding


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = ListGroup(
            x=0, y=0,
            children=[
                Dummy(width=200, color=arcade.color.RED).with_padding(bottom=20),
                Dummy(width=200, color=arcade.color.YELLOW).with_padding(bottom=20),
                Dummy(width=200, color=arcade.color.GREEN).with_padding(bottom=20),
            ])
        self.manager.add(
            AnchorWidget(
                anchor_x="center_x",
                # x_align=-50,
                anchor_y="center_y",
                # y_align=-20,
                child=self.v_box)
        )

        self.h_box = ListGroup(
            x=0, y=0, vertical=False,
            children=[
                Dummy(width=100, color=arcade.color.RED),
                Space(width=20, height=100),
                Dummy(width=50, color=arcade.color.YELLOW).with_padding(right=30),
                Dummy(width=20, color=arcade.color.GREEN),
            ])

        self.manager.add(
            AnchorWidget(
                x_align=20,
                y_align=20,
                child=self.h_box.with_border())
        )

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

        if button == MOUSE_BUTTON_LEFT:
            self.v_box.add(Dummy(width=90, color=arcade.color.PINK))
        elif button == MOUSE_BUTTON_RIGHT:
            self.v_box.remove(self.v_box._children[-1])

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
