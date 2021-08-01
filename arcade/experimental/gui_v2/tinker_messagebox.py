import arcade
from arcade.examples.perf_test.stress_test_draw_shapes import FPSCounter
from arcade.experimental.gui_v2 import UIManager
from arcade.experimental.gui_v2.events import UIOnClickEvent
from arcade.experimental.gui_v2.widgets import TextArea, FlatButton, \
    AnchorWidget, Group

LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent eget pellentesque velit. Nam eu rhoncus nulla. Fusce ornare libero eget ex vulputate, vitae mattis orci eleifend. Donec quis volutpat arcu. Proin lacinia velit id imperdiet ultrices. Fusce porta magna leo, non maximus justo facilisis vel. Duis pretium sem ut eros scelerisque, a dignissim ante pellentesque. Cras rutrum aliquam fermentum. Donec id mollis mi.

Nullam vitae nunc aliquet, lobortis purus eget, porttitor purus. Curabitur feugiat purus sit amet finibus accumsan. Proin varius, enim in pretium pulvinar, augue erat pellentesque ipsum, sit amet varius leo risus quis tellus. Donec posuere ligula risus, et scelerisque nibh cursus ac. Mauris feugiat tortor turpis, vitae imperdiet mi euismod aliquam. Fusce vel ligula volutpat, finibus sapien in, lacinia lorem. Proin tincidunt gravida nisl in pellentesque. Aenean sed arcu ipsum. Vivamus quam arcu, elementum nec auctor non, convallis non elit. Maecenas id scelerisque lectus. Vivamus eget sem tristique, dictum lorem eget, maximus leo. Mauris lorem tellus, molestie eu orci ut, porta aliquam est. Nullam lobortis tempor magna, egestas lacinia lectus.
"""


class UIMockup(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "UI Mockup", resizable=True)
        self.manager = UIManager()
        self.fps = FPSCounter()
        arcade.set_background_color(arcade.color.COOL_GREY)

        ok_button = FlatButton(text="OK")
        ok_button.on_click = self.on_button_click
        message_text = TextArea(text="Are", width=300, height=200).with_border(color=arcade.color.RED)

        self.manager.add(
            AnchorWidget(
                child=Group(width=320, height=220, children=[
                    AnchorWidget(child=message_text, anchor_x="left", anchor_y="top", align_x=10, align_y=-10),
                    AnchorWidget(child=ok_button, anchor_x="right", anchor_y="bottom", align_x=-10, align_y=10)
                ]).with_border())
        )

        print(f"Render {len(self.manager._children[0])} widgets")

    def on_button_click(self, event: UIOnClickEvent):
        print(event)

    def on_draw(self):
        self.fps.tick()
        arcade.start_render()
        self.manager.draw()
        # arcade.draw_text(f"{self.fps.get_fps():.0f}", self.width // 2, self.height // 2, color=arcade.color.RED,
        #                  font_size=20)

    def on_update(self, time_delta):
        self.manager.on_update(time_delta)

    # TODO These can be registered by UIManager
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        self.manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.manager.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_text(self, text):
        self.manager.on_text(text)

    def on_text_motion(self, motion):
        self.manager.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        self.manager.on_text_motion_select(motion)

    def on_resize(self, width: float, height: float):
        # TODO: Tell Widgets they need to re-draw because surface was cleared
        super().on_resize(width, height)
        self.manager.resize(width, height)


window = UIMockup()
arcade.run()
