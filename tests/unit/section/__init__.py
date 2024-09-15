import arcade
from arcade import Section, SectionManager


class RecorderView(arcade.View):
    def __init__(self):
        super().__init__()

        self.section_manager = SectionManager(self)
        self.events = []

    def on_mouse_enter(self, x: float, y: float):
        self.events.append("on_mouse_enter")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.events.append("on_mouse_motion")

    def on_mouse_leave(self, x: float, y: float):
        self.events.append("on_mouse_leave")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.events.append("on_mouse_press")

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.events.append("on_mouse_release")

    def on_show_view(self) -> None:
        self.section_manager.enable()

    def on_hide_view(self) -> None:
        self.section_manager.disable()

    def on_update(self, delta_time: float):
        self.events.append("on_update")

    def on_draw(self):
        self.events.append("on_draw")


class RecorderSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []

    def on_mouse_enter(self, x: float, y: float):
        self.events.append("on_mouse_enter")

    def on_mouse_leave(self, x: float, y: float):
        self.events.append("on_mouse_leave")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.events.append("on_mouse_press")

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.events.append("on_mouse_release")

    def on_update(self, delta_time: float):
        self.events.append("on_update")

    def on_draw(self):
        self.events.append("on_draw")

    def on_show_section(self):
        self.events.append("on_show_section")

    def on_hide_section(self):
        self.events.append("on_hide_section")
