from arcade.gui.events import UIEvent

from arcade.gui.widgets import UIDummy


# TODO add tests

def test_widget():
    # GIVEN
    widget = UIDummy()

    # WHEN
    widget.on_event(UIEvent(widget))

    # THEN
    assert widget.rect == (0, 0, 100, 100)
