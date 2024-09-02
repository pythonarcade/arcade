import arcade
from arcade import View
from tests.unit.section import RecorderSection, RecorderView


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
        "on_show_section",
        "on_mouse_enter",
        "on_mouse_press",
        "on_mouse_release",
        "on_draw",
        "on_update",
        "on_mouse_leave",
    ]


def test_sections_receive_callback_when_manager_enabled_and_disabled(window):
    # GIVEN
    view = RecorderView()
    manager = view.section_manager

    # SETUP
    recorder_section = RecorderSection(
        *window.rect.lbwh,
    )
    manager.add_section(section=recorder_section)
    window.show_view(view)  # will enable the manager

    # THEN
    assert recorder_section.events == ["on_show_section"]

    # WHEN
    window.show_view(View())  # will disable the manager

    # THEN
    assert recorder_section.events == ["on_show_section", "on_hide_section"]


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
