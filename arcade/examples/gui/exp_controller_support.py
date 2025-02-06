from typing import Optional

import arcade
from arcade import Texture
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIEvent,
    UIFlatButton,
    UIImage,
    UIMouseFilterMixin,
    UIOnClickEvent,
    UIView,
)
from arcade.gui.experimental.controller import (
    UIControllerBridge,
    UIControllerButtonPressEvent,
    UIControllerDpadEvent,
    UIFocusGroup,
)


class ControllerIndicator(UIAnchorLayout):
    BLANK_TEX = Texture.create_empty("empty", (40, 40), arcade.color.TRANSPARENT_BLACK)

    def __init__(self):
        super().__init__()

        self._indicator = self.add(UIImage(texture=self.BLANK_TEX), anchor_y="bottom", align_y=10)

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIControllerButtonPressEvent):
            self._indicator.texture = arcade.load_texture(
                f":resources:onscreen_controls/flat_dark/{event.button}.png"
            )
            arcade.unschedule(self.reset)
            arcade.schedule_once(self.reset, 0.5)
        elif isinstance(event, UIControllerDpadEvent):
            tex_map = {
                (1, 0): "right",
                (-1, 0): "left",
                (0, 1): "up",
                (0, -1): "down",
            }

            if event.vector in tex_map:
                self._indicator.texture = arcade.load_texture(
                    f":resources:onscreen_controls/flat_dark/{tex_map[event.vector]}.png"
                )
                arcade.unschedule(self.reset)
                arcade.schedule_once(self.reset, 0.5)

        return super().on_event(event)

    def reset(self, *_):
        print("Reset")
        self._indicator.texture = self.BLANK_TEX
        self.trigger_full_render()


class ControllerModal(UIMouseFilterMixin, UIFocusGroup):
    def __init__(self):
        super().__init__(size_hint=(0.8, 0.8))
        self.with_background(color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE)

        root = self.add(UIBoxLayout(space_between=10))

        root.add(UIFlatButton(text="Modal Button 1"))
        root.add(UIFlatButton(text="Modal Button 2"))
        root.add(UIFlatButton(text="Modal Button 3"))
        root.add(UIFlatButton(text="Close")).on_click = self.close

        self.detect_focusable_widgets()

    def on_event(self, event):
        if super().on_event(event):
            return True

        if isinstance(event, UIControllerButtonPressEvent):
            if event.button == "b":
                self.close(None)
                return True

        return False

    def close(self, event):
        print("Close")
        # self.trigger_full_render()
        self.trigger_full_render()
        self.parent.remove(self)


class MyView(UIView):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)

        self.controller_bridge = UIControllerBridge(self.ui)

        self.root = self.add_widget(ControllerIndicator())
        self.root = self.root.add(UIFocusGroup())
        box = self.root.add(UIBoxLayout(space_between=10), anchor_x="left")

        box.add(UIFlatButton(text="Button 1")).on_click = self.on_button_click
        box.add(UIFlatButton(text="Button 2")).on_click = self.on_button_click
        box.add(UIFlatButton(text="Button 3")).on_click = self.on_button_click

        self.root.detect_focusable_widgets()

    def on_button_click(self, event: UIOnClickEvent):
        print("Button clicked")
        self.root.add(ControllerModal())


if __name__ == "__main__":
    window = arcade.Window(title="Controller UI Example")
    window.show_view(MyView())
    arcade.run()
