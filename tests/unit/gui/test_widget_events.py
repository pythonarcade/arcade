from arcade.gui import UIWidget, Surface
from arcade.gui.events import UIOnUpdateEvent


class TWidget(UIWidget):
    render_triggered = False
    update_triggered = False

    def on_update(self, dt):
        self.update_triggered = True

    def do_render(self, surface: Surface):
        self.render_triggered = True


def test_widget_trigger_on_update():
    # GIVEN
    widget = TWidget()

    # WHEN
    widget.dispatch_ui_event(UIOnUpdateEvent(None, 5))

    # THEN
    assert widget.update_triggered


def test_widget_trigger_do_render():
    # GIVEN
    widget = TWidget()

    # WHEN
    widget.do_render(None)

    # THEN
    assert widget.render_triggered
