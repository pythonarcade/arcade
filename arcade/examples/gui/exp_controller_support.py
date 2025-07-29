"""
Example demonstrating controller support in an Arcade GUI.

This example shows how to integrate controller input with the Arcade GUI framework.
It includes a controller indicator widget that displays the last controller input,
and a modal dialog that can be navigated using a controller.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_controller_support
"""

import arcade
from arcade import Texture
from arcade.experimental.controller_window import ControllerWindow, ControllerView
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIDropdown,
    UIEvent,
    UIFlatButton,
    UIImage,
    UIMouseFilterMixin,
    UIOnChangeEvent,
    UIOnClickEvent,
    UISlider,
    UIView,
)
from arcade.gui.events import (
    UIControllerButtonEvent,
    UIControllerButtonPressEvent,
    UIControllerDpadEvent,
    UIControllerEvent,
    UIControllerStickEvent,
    UIControllerTriggerEvent,
)
from arcade.gui.experimental.focus import UIFocusGroup
from arcade.types import Color


class ControllerIndicator(UIAnchorLayout):
    """
    A widget that displays the last controller input.
    """

    BLANK_TEX = Texture.create_empty("empty", (40, 40), arcade.color.TRANSPARENT_BLACK)
    TEXTURE_CACHE: dict[str, Texture] = {}

    def __init__(self):
        super().__init__()

        self._indicator = self.add(UIImage(texture=self.BLANK_TEX), anchor_y="bottom", align_y=10)
        self._indicator.with_background(color=Color(0, 0, 0, 0))
        self._indicator._strong_background = True

    @classmethod
    def get_texture(cls, path: str) -> Texture:
        if path not in cls.TEXTURE_CACHE:
            cls.TEXTURE_CACHE[path] = arcade.load_texture(path)
        return cls.TEXTURE_CACHE[path]

    @classmethod
    def input_prompts(cls, event: UIControllerEvent) -> Texture | None:
        if isinstance(event, UIControllerButtonEvent):
            match event.button:
                case "a":
                    return cls.get_texture(":resources:input_prompt/xbox/button_a.png")
                case "b":
                    return cls.get_texture(":resources:input_prompt/xbox/button_b.png")
                case "x":
                    return cls.get_texture(":resources:input_prompt/xbox/button_x.png")
                case "y":
                    return cls.get_texture(":resources:input_prompt/xbox/button_y.png")
                case "rightshoulder":
                    return cls.get_texture(":resources:input_prompt/xbox/rb.png")
                case "leftshoulder":
                    return cls.get_texture(":resources:input_prompt/xbox/lb.png")
                case "start":
                    return cls.get_texture(":resources:input_prompt/xbox/button_start.png")
                case "back":
                    return cls.get_texture(":resources:input_prompt/xbox/button_back.png")

        if isinstance(event, UIControllerTriggerEvent):
            match event.name:
                case "lefttrigger":
                    return cls.get_texture(":resources:input_prompt/xbox/lt.png")
                case "righttrigger":
                    return cls.get_texture(":resources:input_prompt/xbox/rt.png")

        if isinstance(event, UIControllerDpadEvent):
            match event.vector:
                case (1, 0):
                    return cls.get_texture(":resources:input_prompt/xbox/dpad_right.png")
                case (-1, 0):
                    return cls.get_texture(":resources:input_prompt/xbox/dpad_left.png")
                case (0, 1):
                    return cls.get_texture(":resources:input_prompt/xbox/dpad_up.png")
                case (0, -1):
                    return cls.get_texture(":resources:input_prompt/xbox/dpad_down.png")

        if isinstance(event, UIControllerStickEvent) and event.vector.length() > 0.2:
            stick = "l" if event.name == "leftstick" else "r"

            # map atan2(y, x) to direction string (up, down, left, right)
            heading = event.vector.heading()
            if 0.785 > heading > -0.785:
                return cls.get_texture(f":resources:input_prompt/xbox/stick_{stick}_right.png")
            elif 0.785 < heading < 2.356:
                return cls.get_texture(f":resources:input_prompt/xbox/stick_{stick}_up.png")
            elif heading > 2.356 or heading < -2.356:
                return cls.get_texture(f":resources:input_prompt/xbox/stick_{stick}_left.png")
            elif -2.356 < heading < -0.785:
                return cls.get_texture(f":resources:input_prompt/xbox/stick_{stick}_down.png")

        return None

    def on_event(self, event: UIEvent) -> bool | None:
        if isinstance(event, UIControllerEvent):
            input_texture = self.input_prompts(event)

            if input_texture:
                self._indicator.texture = input_texture

                arcade.unschedule(self.reset)
                arcade.schedule_once(self.reset, 0.5)

        return super().on_event(event)

    def reset(self, *_):
        self._indicator.texture = self.BLANK_TEX


class ControllerModal(UIMouseFilterMixin, UIFocusGroup):
    def __init__(self):
        super().__init__(size_hint=(0.8, 0.8))
        self.with_background(color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE)

        root = self.add(UIBoxLayout(space_between=10))

        root.add(UIFlatButton(text="Modal Button 1", width=200))
        root.add(UIFlatButton(text="Modal Button 2", width=200))
        root.add(UIFlatButton(text="Modal Button 3", width=200))
        root.add(UIFlatButton(text="Close")).on_click = self.close

        self.detect_focusable_widgets()
        self.set_focus()

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


class MyView(ControllerView, UIView):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)

        base = self.add_widget(ControllerIndicator())
        self.root = base.add(UIFocusGroup())
        self.root.with_padding(left=10)
        box = self.root.add(UIBoxLayout(space_between=10), anchor_x="left")

        box.add(UIFlatButton(text="Button 1")).on_click = self.on_button_click
        box.add(UIFlatButton(text="Button 2")).on_click = self.on_button_click
        box.add(UIFlatButton(text="Button 3")).on_click = self.on_button_click

        box.add(UIDropdown(default="Option 1", options=["Option 1", "Option 2", "Option 3"]))

        slider = box.add(UISlider(value=0.5, min_value=0, max_value=1, width=200))

        @slider.event
        def on_change(event: UIOnChangeEvent):
            print(f"Slider value changed: {event}")

        self.root.detect_focusable_widgets()

    def on_button_click(self, event: UIOnClickEvent):
        print("Button clicked")
        self.root.add(ControllerModal())

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        # make the example close with the escape key
        if symbol == arcade.key.ESCAPE:
            self.window.close()
            return True
        return super().on_key_press(symbol, modifiers)


if __name__ == "__main__":
    window = ControllerWindow(title="Controller UI Example")
    window.show_view(MyView())
    arcade.run()
