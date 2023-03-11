import arcade
from arcade.gui import UIManager, UIFlatButton


def test_event_order_from_window(window: arcade.Window):
    # Ensure there are no pending events
    window.dispatch_pending_events()
    events = []

    mng = UIManager()

    @window.event("on_mouse_press")
    def record_window(*_):
        events.append("Window.on_mouse_press")

    @mng.event("on_event")
    def record_mng(event):
        events.append(f"UIManager.on_event({type(event).__name__})")

    mng.enable()
    window.dispatch_event("on_mouse_press", 100, 75, 1, 0)
    window.dispatch_pending_events()
    mng.disable()
    window.remove_handler("on_mouse_press", record_window)

    assert len(events) == 2
    assert events[0] == "UIManager.on_event(UIMousePressEvent)"
    assert events[1] == "Window.on_mouse_press"


def test_event_order_from_view(window):
    # Ensure there are no pending events
    window.dispatch_pending_events()
    events = []

    class MyView(arcade.View):
        def __init__(self):
            super().__init__()
            self.mng = UIManager()

            @self.mng.event("on_event")
            def record_mng(event):
                events.append(f"UIManager.on_event({type(event).__name__})")

        def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
            events.append("View.on_mouse_press")

        def on_show_view(self):
            self.mng.enable()

        def on_hide_view(self):
            self.mng.disable()

    @window.event("on_mouse_press")
    def record_window(*_):
        events.append("Window.on_mouse_press")

    view = MyView()
    window.show_view(view)
    window.dispatch_event("on_mouse_press", 100, 75, 1, 0)
    window.dispatch_pending_events()

    window.hide_view()
    window.remove_handler("on_mouse_press", record_window)

    assert len(events) == 3
    assert events[0] == "UIManager.on_event(UIMousePressEvent)"
    assert events[1] == "View.on_mouse_press"
    assert events[2] == "Window.on_mouse_press"


def test_event_consumed_by_widget(window):
    events = []

    class MyView(arcade.View):
        def __init__(self):
            super().__init__()
            self.mng = UIManager()
            button = UIFlatButton(x=50, y=50, width=100, height=50, text="Click ME")
            self.mng.add(button)

            @button.event("on_click")
            def record_widget(event):
                events.append("UIFlatButton.on_click")

            @self.mng.event("on_event")
            def record_mng(event):
                events.append(f"UIManager.on_event({type(event).__name__})")

        def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
            events.append("View.on_mouse_press")

        def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
            events.append("View.on_mouse_release")

        def on_show_view(self):
            self.mng.enable()

        def on_hide_view(self):
            self.mng.disable()

    @window.event("on_mouse_press")
    def record_window(*_):
        events.append("Window.on_mouse_press")

    @window.event("on_mouse_release")
    def record_window(*_):
        events.append("Window.on_mouse_release")

    view = MyView()
    window.show_view(view)
    window.dispatch_event("on_mouse_press", 100, 75, 1, 0)
    window.dispatch_event("on_mouse_release", 100, 75, 1, 0)
    window.dispatch_pending_events()
    window.hide_view()
    window.remove_handler("on_mouse_press", record_window)

    assert len(events) == 3, events
    assert events[0] == "UIManager.on_event(UIMousePressEvent)"
    assert events[1] == "UIManager.on_event(UIMouseReleaseEvent)"
    assert events[2] == "UIFlatButton.on_click"
