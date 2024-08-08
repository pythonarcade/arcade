import arcade
from arcade import SectionManager, Section


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


def test_section_manager_enable_event_handling(window):
    # GIVEN
    view = RecorderView()
    manager = view.section_manager

    # SETUP
    recorder_section = RecorderSection(
        *window.rect.lbwh,
    )
    manager.add_section(section=recorder_section)
    window.show_view(view)

    # WHEN

    window.dispatch_event("on_mouse_motion", 10, 10, 0, 0)
    # mouse motion will trigger mouse enter automatically
    window.dispatch_event("on_mouse_press", 11, 11, arcade.MOUSE_BUTTON_LEFT, 0)
    window.dispatch_event("on_mouse_release", 11, 11, arcade.MOUSE_BUTTON_LEFT, 0)
    window.dispatch_event("on_draw")
    window.dispatch_event("on_update", 1 / 60)
    window.dispatch_event("on_mouse_leave", 10, 10)
    window.dispatch_events()

    # THEN
    assert recorder_section.events == [
        "on_mouse_enter",
        "on_mouse_press",
        "on_mouse_release",
        "on_draw",
        "on_update",
        "on_mouse_leave",
    ]


def test_view_receives_events_once(window):
    # GIVEN
    view = RecorderView()
    manager = view.section_manager

    # SETUP
    recorder_section = RecorderSection(
        *window.rect.lbwh, prevent_dispatch_view={False}, prevent_dispatch={True}
    )
    manager.add_section(section=recorder_section)
    window.show_view(view)

    # WHEN
    window.dispatch_event("on_mouse_motion", 10, 10, 0, 0)
    window.dispatch_event("on_mouse_press", 10, 10, arcade.MOUSE_BUTTON_LEFT, 0)
    window.dispatch_event("on_mouse_release", 10, 10, arcade.MOUSE_BUTTON_LEFT, 0)
    window.dispatch_event("on_mouse_leave", 10, 10)
    window.dispatch_event("on_draw")
    window.dispatch_event("on_update", 1 / 60)
    window.dispatch_events()

    # THEN
    assert view.events == [
        "on_mouse_enter",
        "on_mouse_motion",
        "on_mouse_press",
        "on_mouse_release",
        "on_mouse_leave",
        "on_draw",
        "on_update",
    ]
